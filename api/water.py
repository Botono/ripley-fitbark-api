import boto3
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)

import utils
from config import config


water = Blueprint('water', __name__)

SHEET_ID = '1UbzDb1yA0XIStT4A5_5Uf3V4RWEXrM-_2gFpfBjtTb8'

@water.route('/water', methods=['GET'])
def getWater():

    rawResults = []

    tableName = 'Ripley_Water'

    try:
        if config['db'] is None:
            config['db'] = boto3.resource('dynamodb', region_name=config['region'])

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

    processedResults = {}
    currentDate = ''

    for result in rawResults:
         processedResults[result['date']] = {
             'water': config['water_start_amount'] - (result['water'] - config['water_bowl_weight']),
             'kibble_eaten': result.get('kibble_eaten', False),
             'note': result.get('note', ''),
         }

    return jsonify(processedResults), 200
