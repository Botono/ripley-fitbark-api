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
    return jsonify(status=200, message='The URL for this page is {}'.format(url_for('index')))


@app.route('/foo')
def foo():
    return jsonify(status=200, message='The URL for this page is {}'.format(url_for('foo')))



def lambda_handler(event, context):
    return awsgi.response(app, event, context)
