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
    lables = ['WBC', 'RBC', 'HGB', 'HCT', 'MCV', 'MCH', 'MCHC', 'Plaelet Count', 'Neutrophils %', 'Bands', 'Lymphocytes %',
              'Monocytes %', 'Eosinophils %', 'Basophils %', 'Abs Neutrophils', 'Abs Lymphocytes', 'Abs Monocytes', 'Abs Eosinophils', 'Abs Basophils']

    return jsonify(lables), 200
