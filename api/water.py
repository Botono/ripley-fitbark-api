import boto3
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)
import dateutil.parser as parser
import simplejson as json
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

def getWaterDataFromS3():
    content_object = config['s3'].Object(
        config['data_bucket'], 'water/data.json')
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    return json_content

def writeWaterDataToS3(dataDict):
    object = config['s3'].Object(config['data_bucket'], 'water/data.json')
    object.put(Body=json.dumps(dataDict))

@water.route('/water', methods=['GET'])
def getWater():

    try:
        json_content = getWaterDataFromS3()
    except Exception as e:
        errMsg = utils.error_log(str(e))
        return jsonify(errMsg), 500

    return jsonify(json_content), 200


@water.route('/water', methods=['POST'])
def postWater():

    try:
        body = request.get_json()
        # validate
        errMsg = validate_water_object(body)

        if errMsg:
            response = utils.error_log(errMsg)
            return jsonify(response), 400

        water_data = getWaterDataFromS3()

        new_data = {}
        new_data['kibble_eaten'] = body.get('kibble_eaten', False)
        new_data['notes'] = body.get('notes', '')
        new_data['water'] = config['water_start_amount'] - \
            (body['water'] - config['water_bowl_weight'])

        water_data[utils.format_date(body['date'])] = new_data

        writeWaterDataToS3(water_data)

        return jsonify(water_data), 200
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
