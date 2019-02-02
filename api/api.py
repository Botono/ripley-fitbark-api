import awsgi

from flask import (
    Flask,
    jsonify,
    url_for
)

from fitbark import fitbark

app = Flask(__name__)
app.register_blueprint(fitbark)

@app.route('/')
def index():
    return jsonify('Hello'), 200

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
