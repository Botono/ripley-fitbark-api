import json

def handler(event, context):
    message = 'THIS WILL BE AN API'
    print('This API is whack')
    return {
        "statusCode": 200,
        "body": json.dumps(message)
    }
