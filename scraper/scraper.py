import boto3
import json
import requests

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

    url = 'https://app.fitbark.com/api/v2/activity_series'
    headers = {'Authorization': 'Bearer {0}'.format(api_token)}
    body = {}
    body['activity_series'] = {}
    body['activity_series']['slug'] = ripley_slug
    body['activity_series']['from'] = '2018-12-26'
    body['activity_series']['to'] = '2018-12-31'
    body['activity_series']['resolution'] = 'DAILY'

    try:
        r = requests.post(url, json=body, headers=headers)

        return r.json()

    except Exception as e:
        return {
            'error': 'API request failed: {0}'.format(str(e)),
            'body': body
        }
