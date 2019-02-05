import dateutil.parser as parser
from googleapiclient.discovery import build
from flask import (
    Flask,
    Blueprint,
    jsonify,
    request,
    url_for,
)

import google_auth
from config import config
import utils


changelog = Blueprint('changelog', __name__)

SHEET_ID = '1ZLBAN7ZObEoB8hdPoITFkXPzPyO4ycTr2T-om2K6TG4'


@changelog.route('/changelog', methods=['GET'])
def getChangelog():

    try:
        google_auth.load_credentials('sheets')
        range_name = 'Form Responses 1!B2:D'
        service = build(
            'sheets', 'v4', credentials=config['googleAPICreds'], cache_discovery=False)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID,
                                    range=range_name).execute()
        values = result.get('values', [])
        # Remove empty values
        values[:] = [x for x in values if x != []]

        if not values:
            utils.debug_log('/changelog GET: No results')
        else:
            utils.debug_log(
                '/changelog GET: {0} records found!'.format(len(values)))

        # Format data
        formattedResults = {}
        for row in values:
            date = parser.parse(row[0])
            formattedResults[date.strftime("%Y/%m/%d")] = {
                'change_type': row[1],
                'description': row[2],
            }

    except Exception as e:
        print('[ERROR] {0}'.format(str(e)))
        return jsonify('A problem occurred. See the error log for details.'), 500

    return jsonify(formattedResults), 200
