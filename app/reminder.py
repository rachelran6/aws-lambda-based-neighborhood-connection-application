import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError
from flask import Flask
from flask_mail import Mail, Message
import time
from datetime import datetime


app = Flask(__name__)

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

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')

def send_email(recipients,title, start_time):
    print("==========recipients:",recipients)
    with app.app_context():
        start_time = datetime.fromtimestamp(start_time)
        body = "Hello,\n Your event {} is schedule at {}".format(title,start_time)
        msg = Message("Event Notification",
                      body=body,
                      sender=("Your Neighborhood","h.liu9797@gmail.com"),
                      recipients=recipients)
        mail.send(msg)

def check_event():
    print('=======background check event start=======')
    event_response = table.query(
        IndexName='item_type_index',
        KeyConditionExpression=Key('item_type').eq('host')
    )
    current_timestamp = int(time.time())
    if len(event_response['Items'])!=0:
        for i in event_response['Items']:
            if current_timestamp<int(i["start_time"])<current_timestamp+ 60*60 :
                host_response = table.query(
                    KeyConditionExpression=Key('username').eq(i["username"]) & Key('start_time').lt(0)
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
                        KeyConditionExpression=Key('username').eq(participant["username"])& Key('start_time').lt(0)
                    )

                    for parti in participant_response['Items']:
                        recipients.append(parti['email'])
                send_email(recipients,i['title'],i['start_time'])