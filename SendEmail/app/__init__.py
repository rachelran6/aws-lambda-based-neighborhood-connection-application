from flask import Flask
from flask_mail import Mail, Message
import datetime
from datetime import datetime
import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError
import json
import time
app = Flask(__name__)
print('=======background check event start=======')

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'neighborhood.notification@gmail.com',
    MAIL_PASSWORD = 'notification123',
))
mail = Mail(app)

def send_email(recipients, start_time, title):
    print("==========recipients:", recipients)

    with app.app_context():
        start_time = datetime.fromtimestamp(start_time)
        body = "Hello,\nYour event {} is scheduled at {}".format(title, start_time)
        msg = Message("Event Notification",
                      body=body,
                      sender=("Your Neighborhood", "neighborhood.notification@gmail.com"),
                      recipients=recipients)
        mail.send(msg)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')
event_response = table.query(
    IndexName='item_type_index',
    KeyConditionExpression=Key('item_type').eq('host')
)
current_timestamp = int(time.time())
if len(event_response['Items'])!=0:
    for i in event_response['Items']:
        if current_timestamp<int(i["start_time"])<current_timestamp+ 60*60 :
            host_response = table.query(
                KeyConditionExpression=Key('username').eq(i["username"]),
                FilterExpression=Attr('item_type').eq('account')
            )
            recipients=[]
            print(host_response)
            for host in host_response['Items']:
                recipients.append(host['email'])

            group_response = table.query(
                IndexName='item_type_index',
                KeyConditionExpression=Key('item_type').eq('participant') & Key('start_time').eq(i["start_time"])
            )
            for participant in group_response['Items']:
                participant_response = table.query(
                    KeyConditionExpression=Key('username').eq(participant["username"]),
                    FilterExpression=Attr('item_type').eq('account')
                )

                for parti in participant_response['Items']:
                    recipients.append(parti['email'])

            send_email(recipients, i['start_time'],i['title'])
