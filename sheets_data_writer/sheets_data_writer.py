import boto3
import simplejson as json

db = None

def handler(event, context):
    try:

        db = boto3.resource('dynamodb')
        for record in event['Records']:
            # {'dataType': 'water', 'date': '2019-02-10', 'water': 'asdf', 'kibble_eaten': True, 'note': '123'}
            print(record['messageId'])
            payload = json.loads(record['body'])

            dataType = payload.get('dataType')
            del payload['dataType']

            if dataType == 'water':
                handleWater(payload)
            elif dataType == 'changelog':
                handleChangelog(payload)
            print(payload)
    except Exception as e:
        print('[ERROR] Processing failed: {0}'.format(str(e)))
        raise e

def handleWater(payload):
    try:
        db = boto3.resource('dynamodb')
        table = db.Table('Ripley_Water')
        payload['water'] = int(payload['water'])

        table.put_item(
            Item=payload
        )
        print('Success: saved Water entry with date {0}'.format(payload['date']))
    except Exception as e:
        print('[ERROR] handleWater failed')
        raise e


def handleChangelog(payload):
    try:
        db = boto3.resource('dynamodb')
        table = db.Table('Ripley_Changelog')

        table.put_item(
            Item=payload
        )
        print('Success: saved Changelog entry with date {0}'.format(
            payload['date']))
    except Exception as e:
        print('[ERROR] handleChangelog failed')
        raise e
