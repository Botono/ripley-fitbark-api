import boto3
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)
from operator import itemgetter

from config import config
import utils


changelog = Blueprint('changelog', __name__)

SHEET_ID = '1ZLBAN7ZObEoB8hdPoITFkXPzPyO4ycTr2T-om2K6TG4'


@changelog.route('/changelog', methods=['GET'])
def getChangelog():

    rawResults = []

    tableName = 'Ripley_Changelog'

    try:
        if config['db'] is None:
            config['db'] = boto3.resource(
                'dynamodb', region_name=config['region'])

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
