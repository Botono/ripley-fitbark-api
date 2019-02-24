import boto3
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)
import dateutil.parser as parser
from copy import copy

import utils
from config import config


water = Blueprint('water', __name__)

SHEET_ID = '1UbzDb1yA0XIStT4A5_5Uf3V4RWEXrM-_2gFpfBjtTb8'

def validate_water_object(body):
    if not body.get('water'):
        return 'water is a required field.'
    elif not utils.is_number(body['water']):
        return 'water must be a number'

    if not body.get('date'):
        return 'date is a required field.'
    elif not utils.is_date(body['date']):
        return 'date must be a date, dumbass'

    return ''

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
        errMsg = utils.error_log(str(e))
        return jsonify(errMsg), 500

    processedResults = {}
    currentDate = ''

    for result in rawResults:
         processedResults[result['date']] = {
             'water': config['water_start_amount'] - (result['water'] - config['water_bowl_weight']),
             'kibble_eaten': result.get('kibble_eaten', False),
             'notes': result.get('notes', ''),
         }

    return jsonify(processedResults), 200


@water.route('/water', methods=['POST'])
def postWater():

    try:
        table = config['db'].Table('Ripley_Water')
        body = request.get_json()
        # validate
        errMsg = validate_water_object(body)

        if errMsg:
            response = utils.error_log(errMsg)
            return jsonify(response), 400

        body['date'] = utils.format_date(body['date'])

        if not body['kibble_eaten']:
            body['kibble_eaten'] = False


        get_response = table.get_item(Key={'date': body['date']})

        utils.debug_log(
            'postWater(): get_item() response: {}'.format(get_response))

        if get_response.get('Item', {}):
            errMsg = utils.error_log(
                'Item already exists with key {}, update it instead'.format(body['date']))
            return jsonify(errMsg), 400

        table.put_item(
            Item=body
        )

        return jsonify(body), 200
    except Exception as e:
        errMsg = utils.error_log(str(e))
        return jsonify(errMsg), 500


@water.route('/water/<water_date>', methods=['PUT'])
def updateWater(water_date):
    body = request.get_json()

    # validate
    errMsg = validate_water_object(body)

    if errMsg:
        response = utils.error_log(errMsg)
        return jsonify(response), 400

    body['date'] = utils.format_date(body['date'])

    if not body['kibble_eaten']:
        body['kibble_eaten'] = False

    try:
        table = config['db'].Table('Ripley_Water')

        get_response = table.get_item(Key={'date': water_date})

        utils.debug_log('updateWater(): get_item() response: {}'.format(get_response))

        if not get_response.get('Item', {}):
            errMsg = utils.error_log('Cannot update an item that does not exist')
            return jsonify(errMsg), 404
        else:
            original = get_response['Item']

        table.put_item(
            Item=body
        )

        if original['date'] != body['date']:
            table.delete_item(
                Key={
                    'date': original['date']
                }
            )

        return jsonify(body), 200
    except Exception as e:
        errMsg = utils.error_log(str(e))
        return jsonify(errMsg), 500

@water.route('/water/<water_date>', methods=['PATCH'])
def patchWater(water_date):

    def validateOp(obj):
        if obj['key'] == 'date':
            if not utils.is_date(obj['value']):
                return 'Date is invalid'
        if obj['key'] == 'water':
            if not utils.is_number(obj['value']):
                return 'Water must be a number'

        if obj['op'] == 'remove':
            if obj['key'] != 'notes':
                return 'Only notes can be removed'

        return ''

    try:
        if not utils.is_date(water_date):
            errMsg = utils.error_log('Invalid date in path')
            return jsonify(errMsg), 400

        table = config['db'].Table('Ripley_Water')
        ops = request.get_json()['ops']

        # [ { "op": "add", "key": "notes", "value": "a new notes to add" } ]

        for obj in ops:
            errMsg = validateOp(obj)
            if errMsg:
                response = utils.error_log(errMsg)
                return jsonify(response), 400

            if obj['op'] == 'update':
                get_response = table.get_item(Key={'date': water_date})

                utils.debug_log(
                    'patchWater(): get_item() response: {}'.format(get_response))

                if not get_response.get('Item', {}):
                    errMsg = utils.error_log(
                        'Cannot update an item that does not exist')
                    return jsonify(errMsg), 404
                else:
                    original = get_response['Item']

                record = copy(original)
                record[obj['key']] = obj['value']
                table.put_item(
                    Item = record
                )

                # Date was updated, remove old record
                if obj['key'] == 'date':
                    table.delete_item(
                        Key = {
                            'date': original['date']
                        }
                    )
            elif obj['op'] == 'remove':
                get_response = table.get_item(Key={'date': water_date})

                utils.debug_log(
                    'pathWater(): get_item() response: {}'.format(get_response))

                if not get_response.get('Item', {}):
                    errMsg = utils.error_log(
                        'Cannot update an item that does not exist')
                    return jsonify(errMsg), 404
                else:
                    original = get_response['Item']
                record = copy(original)
                # Note is the only attribute that can be removed
                del record['notes']
                table.put_item(
                    Item=record
                )

        return jsonify('{}'), 405
    except Exception as e:
        errMsg = utils.error_log(str(e))
        return jsonify(errMsg), 500


