import csv
import boto3
from dynamodb_json import json_util as json
from decimal import Decimal

table_name = 'RipleyFitbark_Activity_Daily'

db_data = []
'''
"date (S)","time (S)","activity_goal (N)","activity_value (N)","distance_in_miles (N)","kcalories (N)","min_active (N)","min_play (N)","min_rest (N)"
"2019-01-18","02:00:00","23100","102","0.01","24","6","0","54"

"date (S)","activity_average (N)","activity_value (N)","daily_target (N)","has_trophy (N)","min_active (N)","min_play (N)","min_rest (N)"
"2019-01-12","46766","5214","4200","0","389","58","352"
'''

with open('RipleyFitbark_Activity_Daily.csv', 'r') as f:
    reader = csv.reader(f)
    count = 0
    for row in reader:
        count = count + 1
        if count == 1:
            continue
        put_item = {}

        # put_item['date'] = row[0]
        # put_item['time'] = row[1]
        # put_item['activity_goal'] = int(row[2])
        # put_item['activity_value'] = int(row[3])
        # put_item['distance_in_miles'] = Decimal(row[4])
        # put_item['kcalories'] = int(row[5])
        # put_item['min_active'] = int(row[6])
        # put_item['min_play'] = int(row[7])
        # put_item['min_rest'] = int(row[8])

        put_item['date'] = row[0]
        put_item['activity_average'] = int(row[1])
        put_item['activity_value'] = int(row[2])
        put_item['daily_target'] = int(row[3])
        put_item['has_trophy'] = int(row[4])
        put_item['min_active'] = int(row[5])
        put_item['min_play'] = int(row[6])
        put_item['min_rest'] = int(row[7])
        db_data.append(put_item)


session = boto3.session.Session(profile_name='ripley_api', region_name='us-west-2')
db = session.resource('dynamodb')
table = db.Table('RipleyFitbark_Activity_Daily')

with table.batch_writer() as batch:
    for item in db_data:
        batch.put_item(
            Item=item
        )

