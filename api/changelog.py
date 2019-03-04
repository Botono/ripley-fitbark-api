import boto3
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)
import xxhash
from operator import itemgetter

from config import config
import utils


changelog = Blueprint('changelog', __name__)

SHEET_ID = '1ZLBAN7ZObEoB8hdPoITFkXPzPyO4ycTr2T-om2K6TG4'


valid_types = ['Medicine', 'Diet', 'Other']

def validate_changelog_object(body):
    if not body.get('message'):
        return 'message is a required field'

    if not body.get('date'):
        return 'date is a required field'
    elif not utils.is_date(body['date']):
        return 'date must be a date, dumbass'

    if not body.get('type'):
        return 'type is a required field'
    elif body.get('type') not in valid_types:
        return 'invalid value for type'

    return ''

@changelog.route('/changelog', methods=['GET'])
def getChangelog():

    rawResults = []

    tableName = 'Ripley_Changelog'

    try:
        table = config['db'].Table(tableName)

        response = table.scan(
            # FilterExpression=Key('date').between(startDate, endDate)
        )
        rawResults.extend(response['Items'])

        while response.get('LastEvaluatedKey'):
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'])
            rawResults.extend(response['Items'])

    except Exception as e:
        return jsonify('DB scan failed: {0}'.format(str(e))), 500

    processedResults = []
    currentDate = ''

    for result in rawResults:
        processedResults.append(result)

    # Reverse sort results
    processedResults = sorted(processedResults, key=itemgetter('date'), reverse=True)

    return jsonify(processedResults), 200

@changelog.route('/changelog', methods=['POST'])
def createChangelog():
    try:
        table = config['db'].Table('Ripley_Changelog')
        body = request.get_json()
        # validate
        errMsg = validate_changelog_object(body)

        if errMsg:
            response = utils.error_log(errMsg)
            return jsonify(response), 400

        body['date'] = utils.format_date(body['date'])
        message_hash = xxhash.xxh64(body['message']).hexdigest()
        body['messageHash'] = message_hash

        get_response = table.get_item(Key={'messageHash': message_hash, 'date': body['date']})

        utils.debug_log(
            'postWater(): get_item() response: {}'.format(get_response))

        if get_response.get('Item', {}):
            errMsg = utils.error_log(
                'Item already exists with key {}, update it instead'.format(message_hash))
            return jsonify(errMsg), 409

        table.put_item(
            Item=body
        )

        return jsonify(body), 200
    except Exception as e:
        errMsg = utils.error_log(str(e))
        return jsonify(errMsg), 500
