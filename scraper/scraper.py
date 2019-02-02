import boto3
import json
import requests
import dateutil.tz
import simplejson as json

from datetime import datetime, timedelta, timezone
from decimal import Decimal


def handler(event, context):

    secrets = boto3.client('secretsmanager')

    try:
        api_token = secrets.get_secret_value(
            SecretId='RipleyFitbark_api_token')['SecretString']
        ripley_slug = secrets.get_secret_value(
            SecretId='RipleyFitbark_ripley_slug')['SecretString']
    except Exception:
        return {
            'error': 'Could not read secrets'
        }

    #Set dates
    pst = dateutil.tz.gettz('America/Los_Angeles')
    d = datetime.now(tz=pst)-timedelta(3)
    startDate = d.strftime('%Y-%m-%d')
    d = datetime.now(tz=pst)-timedelta(1)
    endDate = d.strftime('%Y-%m-%d')

    queryFrom = event.get('from', startDate)
    queryTo = event.get('to', endDate)
    queryResolution = event.get('resolution', 'HOURLY')

    print('Query Parameters: FROM: {0} TO: {1} RESOLUTION: {2}'.format(queryFrom, queryTo, queryResolution))

    url = 'https://app.fitbark.com/api/v2/activity_series'
    headers = {'Authorization': 'Bearer {0}'.format(api_token)}
    body = {}
    body['activity_series'] = {}
    body['activity_series']['slug'] = ripley_slug
    body['activity_series']['from'] = queryFrom
    body['activity_series']['to'] = queryTo
    body['activity_series']['resolution'] = queryResolution

    # HOURLY
    try:
        r = requests.post(url, json=body, headers=headers)

        records = r.json(parse_float=Decimal)

        records = format_records(records['activity_series']['records'])

        db = boto3.resource('dynamodb')
        table = db.Table('RipleyFitbark_Activity_Hourly')

        for record in records:
            table.put_item(
                Item=record
            )
        print('HOURLY records added for {0} - {1}'.format(queryFrom, queryTo))
    except Exception as e:
        print('ERROR: HOURLY update failed: {0}'.format(str(e)))
        return {
            'error': 'HOURLY update failed: {0}'.format(str(e)),
            'body': body
        }

    #DAILY - only run if event is not set
    if not event.get('resolution', False):
        body['activity_series']['resolution'] = 'DAILY'
        try:
            r = requests.post(url, json=body, headers=headers)

            records = r.json(parse_float=Decimal)['activity_series']['records']

            db = boto3.resource('dynamodb')
            table = db.Table('RipleyFitbark_Activity_Daily')

            for record in records:
                table.put_item(
                    Item=record
                )
            print('DAILY records added for {0} - {1}'.format(queryFrom, queryTo))
        except Exception as e:
            print('ERROR: DAILY update failed: {0}'.format(str(e)))
            return {
                'error': 'DAILY update failed: {0}'.format(str(e)),
                'body': body
            }

def format_records(records):
    for record in records:
        dateAndTime = record['date'].split()
        record['date'] = dateAndTime[0]
        record['time'] = dateAndTime[1]

    return records
