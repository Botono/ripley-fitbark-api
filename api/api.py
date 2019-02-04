import awsgi
import os

from flask import (
    Flask,
    jsonify,
    url_for
)
from flask_cors import CORS

from config import config
from fitbark import fitbark
from water import water


app = Flask(__name__)
app.register_blueprint(fitbark)
app.register_blueprint(water)

CORS(app)

def lambda_handler(event, context):
    config['debug_mode'] = os.environ.get('DEBUG', False)
    return awsgi.response(app, event, context)
