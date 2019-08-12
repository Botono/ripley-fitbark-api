import boto3


boto_sess = boto3.session.Session(
    region_name='us-west-2', profile_name='ripley_api')
db = boto_sess.resource('dynamodb')
water_bowl_weight = 1595
water_start_amount = 3000

table = db.Table('Ripley_Water')
rawResults = []

response = table.scan()
rawResults.extend(response['Items'])

while response.get('LastEvaluatedKey'):
    response = table.scan(
        ExclusiveStartKey=response['LastEvaluatedKey'])
    rawResults.extend(response['Items'])

with table.batch_writer() as batch:
    for item in rawResults:
        item['water_grams'] = water_start_amount - \
            (item['water'] - water_bowl_weight)
        print('Updating {} with water_grams value of {}'.format(item.get('date'), item.get('water_grams')))
        batch.put_item(Item=item)
