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

    valid_resolutions = ['hourly', 'daily']
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    resolution = request.args.get('resolution')

    if resolution not in valid_resolutions:
        return jsonify('resolution must be "hourly" or "daily"'), 400

    rawResults = []

    tableName = 'RipleyFitbark_Activity_{0}'.format(resolution.capitalize())

    try:
        if config['db'] is None:
            config['db'] = boto3.resource(
                'dynamodb', region_name=config['region'])

        table = config['db'].Table(tableName)

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

    if resolution == 'hourly':
        for result in rawResults:
            if result['date'] != currentDate:
                currentDate = result['date']
                processedResults[currentDate] = []
            processedResults[currentDate].append(result)
    else:
        for result in rawResults:
            processedResults[result['date']] = result

    return jsonify(processedResults), 200


@fitbark.route('/fitbark')
def fitbark_root():
    return jsonify(status=200, message='The URL for this page is {}'.format(url_for('fitbarkApi.fitbark_root')))
