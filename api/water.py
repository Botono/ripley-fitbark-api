import boto3
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)
import dateutil.parser as parser

import utils
from config import config


water = Blueprint('water', __name__)

SHEET_ID = '1UbzDb1yA0XIStT4A5_5Uf3V4RWEXrM-_2gFpfBjtTb8'

@water.route('/water', methods=['GET'])
def getWater():

    rawResults = []

    tableName = 'Ripley_Water'

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

    processedResults = {}
    currentDate = ''

    for result in rawResults:
         processedResults[result['date']] = {
             'water': config['water_start_amount'] - (result['water'] - config['water_bowl_weight']),
             'kibble_eaten': result.get('kibble_eaten', False),
             'note': result.get('note', ''),
         }

    return jsonify(processedResults), 200


@water.route('/water', methods=['POST', 'PUT'])
def updateWater():
    body = request.get_json()

    # validate
    validationErr = ''
    if not body['water']:
        validationErr = 'water is a required field.'

    if not body['date']:
        validationErr = 'date is a required field.'
    elif not utils.is_date(body['date']):
        validationErr = 'date must be a date, dumbass'
    else:
        body['date'] = parser.parse(body['date']).strftime("%Y-%m-%d")

    if not body['kibble_eaten']:
        body['kibble_eaten'] = False

    if not utils.is_number(body['water']):
        validationErr = 'water must be a number'

    if validationErr:
        return jsonify('Validation error: {0}'.format(validationErr)), 400

    try:
        table = config['db'].Table('Ripley_Water')

        table.put_item(
            Item=body
        )

        return jsonify(body), 200
    except Exception as e:
        return jsonify('[ERROR]: {0}'.format(str(e))), 500
