import awsgi
import os
import boto3

from flask import (
    Flask,
    jsonify,
    url_for
)
from flask_cors import CORS

from config import config
from changelog import changelog
from fitbark import fitbark
from water import water
from bloodwork import bloodwork


app = Flask(__name__)
app.register_blueprint(fitbark)
app.register_blueprint(water)
app.register_blueprint(changelog)
app.register_blueprint(bloodwork)

CORS(app, origins=['http://localhost:3000',
                   '^(https?://(?:.+\.)?ripley\.dog(?::\d{1,5})?)$',
                   '^(https?://(?:.+\.)?botono\.com(?::\d{1,5})?)$'])

def lambda_handler(event, context):
    config['debug_mode'] = os.environ.get('DEBUG', False)
    if config['db'] is None:
        config['db'] = boto3.resource(
            'dynamodb', region_name=config['region'])
    return awsgi.response(app, event, context)
