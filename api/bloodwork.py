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


bloodwork = Blueprint('bloodwork', __name__)


@bloodwork.route('/bloodwork', methods=['GET'])
def getBloodwork():
    rawResults = []

    tableName = 'Ripley_Bloodwork'

    try:
        if config['db'] is None:
            config['db'] = boto3.resource(
                'dynamodb', region_name=config['region'])

        table = config['db'].Table(tableName)

        response = table.scan()
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
         processedResults[result['date']] = result

    return jsonify(processedResults), 200

@bloodwork.route('/bloodwork/labels', methods=['GET'])
def getBloodworkLabels():
    lables = [
        {
            'name': 'WBC',
            'lower': 4,
            'upper': 15.5,
        },
        {
            'name': 'RBC',
            'lower': 4.8,
            'upper': 9.3,
        },
        {
            'name': 'HGB',
            'lower': 12.1,
            'upper': 20.3,
        },
        {
            'name': 'HCT',
            'lower': 36,
            'upper': 60,
        },
        {
            'name': 'MCV',
            'lower': 58,
            'upper': 79,
        },
        {
            'name': 'MCH',
            'lower': 19,
            'upper': 28,
        },
        {
            'name': 'MCHC',
            'lower': 30,
            'upper': 38,
        },
        {
            'name': 'Plaelet Count',
            'lower': 170,
            'upper': 400,
        },
        {
            'name': 'Neutrophils %',
            'lower': 60,
            'upper': 77,
        },
        {
            'name': 'Bands',
            'lower': 0,
            'upper': 3,
        },
        {
            'name': 'Lymphocytes %',
            'lower': 12,
            'upper': 30,
        },
        {
            'name': 'Monocytes %',
            'lower': 3,
            'upper': 10,
        },
        {
            'name': 'Eosinophils %',
            'lower': 2,
            'upper': 10,
        },
        {
            'name': 'Basophils %',
            'lower': 0,
            'upper': 1,
        },
        {
            'name': 'Abs Neutrophils',
            'lower': 2060,
            'upper': 10600,
        },
        {
            'name': 'Abs Lymphocytes',
            'lower': 690,
            'upper': 4500,
        },
        {
            'name': 'Abs Monocytes',
            'lower': 0,
            'upper': 840,
        },
        {
            'name': 'Abs Eosinophils',
            'lower': 0,
            'upper': 1200,
        },
        {
            'name': 'Abs Basophils',
            'lower': 0,
            'upper': 150,
        },
    ]

    return jsonify(lables), 200
