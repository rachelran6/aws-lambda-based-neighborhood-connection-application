import atexit

import boto3
from apscheduler.schedulers.blocking import BlockingScheduler
from boto3.dynamodb.conditions import Attr, Key
from datetime import datetime

import time


def invoke_send_email():
    print("invoke")
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:253735393254:function:sendemail-dev'
    )


def update_events():
    table = boto3.resource('dynamodb', region_name='us-east-1').Table('Events')
    outdated_item_response = table.query(
        IndexName='item_type_index',
        KeyConditionExpression=Key('item_type').eq('host')&Key('start_time').lt(int(datetime.utcnow().strftime("%s"))),
        FilterExpression= Attr('is_active').eq(1)
    )

    for item in outdated_item_response['Items']:
        table.update_item(
            Key={
                'username': item['username'],
                'start_time': item['start_time']
            },
            UpdateExpression='SET is_active = :val1',
            ExpressionAttributeValues={
                ':val1': 0
            }
        )



scheduler = BlockingScheduler()
scheduler.add_job(func=invoke_send_email,
                  trigger='interval', seconds=60*60)

scheduler.add_job(func=update_events,
                  trigger='interval', seconds=60*60)

scheduler.start()

atexit.register(lambda: scheduler.shutdown())
