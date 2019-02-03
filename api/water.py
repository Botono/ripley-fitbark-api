from config import config
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)
from googleapiclient.discovery import build
# from oauth2client.client import flow_from_clientsecrets

water = Blueprint('water', __name__)

SHEET_ID = '1UbzDb1yA0XIStT4A5_5Uf3V4RWEXrM-_2gFpfBjtTb8'


@water.route('/water', methods=['GET'])
def getWater():
    # range_name = 'Form Responses 1!B2:B'
    # try:
    #     flow = flow_from_clientsecrets('cred.json',
    #                                    scope='https://www.googleapis.com/auth/calendar',
    #                                    redirect_uri='http://example.com/auth_return')

    #     service = build('sheets', 'v4', developerKey=apiKey)
    #     sheet = service.spreadsheets()
    #     result = sheet.values().get(spreadsheetId=SHEET_ID,
    #                                 range=range_name).execute()
    #     values = result.get('values', [])

    #     if not values:
    #         print('No data found.')
    #     else:
    #         for row in values:
    #             print(row)

    # except Exception as e:
    #     return jsonify('A problem occurred: {0}'.format(str(e))), 500

    return jsonify(status=200, message='The URL for this page is {}'.format(url_for('water.getWater')))
