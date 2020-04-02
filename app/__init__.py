import decimal
from datetime import datetime

import boto3

import botocore
from flask import Flask, render_template, request, jsonify
from boto3.dynamodb.conditions import Key, Attr

from app import auth, events, users

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')


webapp = Flask(__name__, instance_relative_config=True)
webapp.secret_key = 'super secret key'


webapp.register_blueprint(auth.bp)
webapp.register_blueprint(events.bp)
webapp.register_blueprint(users.bp)

table_name = 'Events'
table_names = [table.name for table in dynamodb.tables.all()]
if table_name not in table_names:
    response = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'start_time',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'start_time',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'item_type',
                'AttributeType': 'S'
            }

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        },
        GlobalSecondaryIndexes=[
            {
                "IndexName": "item_type_index",
                "KeySchema": [
                    {
                        "AttributeName": "item_type",
                        "KeyType": "HASH"
                    },
                    {
                        'AttributeName': 'start_time',
                        'KeyType': 'RANGE'
                    }
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                }
            }
        ]
    )


@webapp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@webapp.route('/profile', methods=['GET'])
def profile():
    profile = {
        'username': 'maxxx580',
        'self': True,
        'joined_events': [{
            'title': 'event title 1',
            'address': '215 queen',
            'start_time': datetime.utcnow(),
            'end_time': '123345667',
            'rating': '4'
        }],
        'hosted_events': [{
            'title': 'event title 2',
            'address': '225 queen',
            'start_time': datetime.utcnow(),
            'end_time': '123345667',
            'rating': '4'
        }],
        'messages': [
            {
                'from': 'user 1',
                'time': datetime.utcnow(),
                'text': 'message 1'
            },
            {
                'from': 'user 2',
                'time': datetime.utcnow(),
                'text': 'message 2'
            }
        ]
    }
    return render_template('profile.html', profile=profile)


@webapp.route('/event', methods=['GET'])
def event():
    try:
        print(request.args.get('username'))
        event_response = dynamodb.Table('Events').query(
            KeyConditionExpression=Key('username').eq(
                request.args.get('username')) &
            Key('start_time').eq(int(request.args.get('timestamp')))
        )
        host_response = dynamodb.Table('Events').query(
            KeyConditionExpression=Key('username').eq(
                request.args.get('username')),
            FilterExpression=Attr('item_type').eq("account")
        )
        review_response = dynamodb.Table('Events').query(
            KeyConditionExpression=Key('username').eq(
                request.args.get('username')) &
            Key('start_time').eq(int(request.args.get('timestamp'))),
            FilterExpression=Attr('item_type').eq('participant')
        )

        event = {
            'username': host_response['Items'][0]['username'],
            'email': "test eamil",  # host_response['Items'][0]['email'],
            # host_response['Items'][0]['phone_number'],
            'phone_number': 'test number',
            # sum([float(event['start']) for event in review_response['Items']])//len(review_response['Items'])
            'review': 3,
            'start_time': str(datetime.fromtimestamp(event_response['Items'][0]['start_time'])),
            'end_time': str(datetime.fromtimestamp(event_response['Items'][0]['end_time'])),
            'address': event_response['Items'][0]['address'],
            'title': event_response['Items'][0]['title']
        }
        return render_template('event.html', event=event)
    except (botocore.exceptions.ClientError, AssertionError) as e:
        return e.args


@webapp.route('/users/message', methods=['GET'])
def messages():
    username = "eric"
    receiver = "sara"
    return render_template('messages.html', username=username, receiver=receiver)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return int(obj)
    raise TypeError
