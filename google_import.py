from google.oauth2 import service_account
from googleapiclient.discovery import build
import boto3
import json
from datetime import datetime, timedelta, timezone
import dateutil.parser as parser
from decimal import Decimal


def safe_list_get(l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default

def get_creds():
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets'
    ]

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=scopes)
        return credentials

    except Exception as e:
        raise e


# Water
try:
    boto_sess = boto3.session.Session(region_name='us-west-2', profile_name='ripley_api')
    db = boto_sess.resource('dynamodb')
    sheet_id = '1UbzDb1yA0XIStT4A5_5Uf3V4RWEXrM-_2gFpfBjtTb8'

    range_name = 'Form Responses 1!A2:D'
    service = build(
        'sheets', 'v4', credentials=get_creds(), cache_discovery=False)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=range_name).execute()
    values = result.get('values', [])
    # Remove empty values
    values[:] = [x for x in values if x != []]

    # if not values:
    #     utils.debug_log('/water GET: No results')
    # else:
    #     utils.debug_log(
    #         '/water GET: {0} records found!'.format(len(values)))

    table = db.Table('Ripley_Water')

    for row in values:
        date = parser.parse(row[0])
        print('Writing water with date {0}'.format(
            date.strftime("%Y-%m-%d")))

        item = {
            'date': date.strftime("%Y-%m-%d"),
            'water': int(row[1]),
            'kibble_eaten': bool(safe_list_get(row, 2, False)),
        }

        note = safe_list_get(row, 3, '')

        if note:
            item['note'] = note

        table.put_item(
            Item=item
        )
    print('Water data loaded')
except Exception as e:
    print('[ERROR] Failure getting Water data: {0}'.format(str(e)))

try:
    # Changelog
    range_name = 'Form Responses 1!A2:C'
    sheet_id = '1ZLBAN7ZObEoB8hdPoITFkXPzPyO4ycTr2T-om2K6TG4'
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=range_name).execute()
    values = result.get('values', [])
    # Remove empty values
    values[:] = [x for x in values if x != []]

    # if not values:
    #     utils.debug_log('/changelog GET: No results')
    # else:
    #     utils.debug_log(
    #         '/changelog GET: {0} records found!'.format(len(values)))

    # Format data
    formattedResults = {}
    table = db.Table('Ripley_Changelog')
    for row in values:
        date = parser.parse(row[0])
        print('Writing changelog with date {0}'.format(
            date.strftime("%Y-%m-%d")))
        table.put_item(
            Item={
                'date': date.strftime("%Y-%m-%d"),
                'type': row[1],
                'message': row[2],
            }
        )
    print('Changelog data written')
except Exception as e:
    print('[ERROR] Failure getting Changelog data: {0}'.format(str(e)))
