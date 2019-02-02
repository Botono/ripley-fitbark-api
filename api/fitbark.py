import boto3
from boto3.dynamodb.conditions import Key, Attr
import validator
from config import config
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)


fitbark = Blueprint('fitbarkApi', __name__)

@fitbark.route('/fitbark/activity', methods=['GET'])
def getActivity():

    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    resolution = request.args.get('resolution')

    apiResults = []

    tableName = 'RipleyFitbark_Activity_Hourly' if resolution == 'hourly' else 'RipleyFitbark_Activity_Daily'

    try:
        db = boto3.resource('dynamodb', region_name=config['region'])
        table = db.Table(tableName)

        response = table.scan(
            FilterExpression=Key('date').between(startDate, endDate)
        )
        apiResults.extend(response['Items'])

        while response.get('LastEvaluatedKey'):
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            apiResults.extend(response['Items'])

        print(apiResults)
    except Exception as e:
        return jsonify('DB scan failed: {0}'.format(str(e))), 500

    return jsonify(apiResults), 200


@fitbark.route('/fitbark')
def fitbark_root():
    return jsonify(status=200, message='The URL for this page is {}'.format(url_for('fitbarkApi.fitbark_root')))
