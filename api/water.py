import google_auth
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)
from googleapiclient.discovery import build

import utils
from config import config


water = Blueprint('water', __name__)

SHEET_ID = '1UbzDb1yA0XIStT4A5_5Uf3V4RWEXrM-_2gFpfBjtTb8'

@water.route('/water', methods=['GET'])
def getWater():

    try:
        google_auth.load_credentials('sheets')
        range_name = 'Form Responses 1!A2:D'
        service = build(
            'sheets', 'v4', credentials=config['googleAPICreds'], cache_discovery=False)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID,
                                    range=range_name).execute()
        values = result.get('values', [])
        # Remove empty values
        values[:] = [x for x in values if x != []]

        if not values:
            utils.debug_log('/water GET: No results')
        else:
            utils.debug_log('/water GET: {0} records found!'.format(len(values)))

        # Format data
        formattedResults = {}
        for row in values:

            formattedResults[row[0]] = {
                'water': config['water_start_amount'] - (int(row[1]) - config['water_bowl_weight']),
                'kibble_eaten': bool(utils.safe_list_get(row, 2, False)),
                'note': utils.safe_list_get(row, 3, ''),
            }

    except Exception as e:
        print('[ERROR] {0}'.format(str(e)))
        return jsonify('A problem occurred. See the error log for details.'), 500

    return jsonify(formattedResults), 200
