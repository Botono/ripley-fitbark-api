import awsgi
import boto3
from flask import (
    Flask,
    jsonify,
)

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify(status=200, message='OK')

@app.route('/fitbark')
def fitbar():
    return jsonify(status=200, message='fitbark')

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
