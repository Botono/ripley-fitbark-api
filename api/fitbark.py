import boto3
import validator
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
    return jsonify(status=200, message='The URL for this page is {}'.format(url_for('fitbarkApi.getActivity')))


@fitbark.route('/fitbark')
def fitbark_root():
    return jsonify(status=200, message='The URL for this page is {}'.format(url_for('fitbarkApi.fitbark_root')))
