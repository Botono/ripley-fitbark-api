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

@fitbark.route('/fitbark/activity/hourly', methods=['GET'])
def getActivityHourly():

    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')

    rawResults = []

    tableName = 'RipleyFitbark_Activity_Hourly'

    try:
        db = boto3.resource('dynamodb', region_name=config['region'])
        table = db.Table(tableName)

        response = table.scan(
            FilterExpression=Key('date').between(startDate, endDate)
        )
        rawResults.extend(response['Items'])

        while response.get('LastEvaluatedKey'):
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            rawResults.extend(response['Items'])

    except Exception as e:
        return jsonify('DB scan failed: {0}'.format(str(e))), 500

    processedResults = {}
    currentDate = ''

    for result in rawResults:
        if result['date'] != currentDate:
            currentDate = result['date']
            processedResults[currentDate] = []
        processedResults[currentDate].append(result)

    return jsonify(processedResults), 200


@fitbark.route('/fitbark/activity/daily', methods=['GET'])
def getActivityDaily():

    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')

    rawResults = []

    tableName = 'RipleyFitbark_Activity_Daily'

    try:
        db = boto3.resource('dynamodb', region_name=config['region'])
        table = db.Table(tableName)

        response = table.scan(
            FilterExpression=Key('date').between(startDate, endDate)
        )
        rawResults.extend(response['Items'])

        while response.get('LastEvaluatedKey'):
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'])
            rawResults.extend(response['Items'])

    except Exception as e:
        return jsonify('DB scan failed: {0}'.format(str(e))), 500

    processedResults = {}

    for result in rawResults:
        processedResults[result['date']] = result

    return jsonify(processedResults), 200

@fitbark.route('/fitbark')
def fitbark_root():
    return jsonify(status=200, message='The URL for this page is {}'.format(url_for('fitbarkApi.fitbark_root')))
