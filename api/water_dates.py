import simplejson as json
import dateutil.parser as parser
from datetime import timedelta

import utils
from config import config

try:
    new_data = {}
    with open('water_data.json', ) as data_file:
        water_data = json.load(data_file)
        for current_date in water_data.keys():
            new_date = parser.parse(current_date) - timedelta(days=1)
            new_date_formatted = new_date.strftime("%Y-%m-%d")
            print('{} to {}'.format(current_date, new_date_formatted))
            new_data[new_date_formatted] = water_data[current_date]

    with open('new_water_data.json', 'w') as new_file:
        json.dump(new_data, new_file)
except Exception as e:
    raise e
    # print('Failure modifying data: {}'.format(str(e)))
