import decimal
from datetime import datetime

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from flask import Flask, g, jsonify, render_template, request, url_for
from boto3.dynamodb.conditions import Key
from flask import Flask, render_template, request
from app import auth, events, users

from .auth import login_required

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
s3_client = boto3.client('s3')
BUCKET = "ece1779-a3-pic"
table = dynamodb.Table('Events')

webapp = Flask(__name__, instance_relative_config=True)
webapp.secret_key = 'super secret key'


webapp.register_blueprint(events.bp)
webapp.register_blueprint(users.bp)
webapp.register_blueprint(auth.bp)

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
@login_required
def index():
    return render_template('index.html',
                           urls={
                               'events': url_for('index'),
                               'messages': url_for('messages'),
                               'profile': url_for('profile')
                           })


@webapp.route('/profile', methods=['GET'])
@login_required
def profile():
    username = g.user
    table = dynamodb.Table('Events')
    host_response = table.query(
        KeyConditionExpression=Key('username').eq(username),
        FilterExpression=Attr('item_type').eq('account')
    )
    hosted_events_response = table.query(
        KeyConditionExpression=Key('username').eq(username),
        FilterExpression=Attr('item_type').eq('host')
    )
    joined_events_response = table.query(
        KeyConditionExpression=Key('username').eq(username),
        FilterExpression=Attr('item_type').eq("participant")
    )
    joined_events=[]
    for i in joined_events_response['Items']:
        joined_event = table.query(
            IndexName="item_type_index",
            KeyConditionExpression=Key('item_type').eq('host') & Key('start_time').eq(i['start_time'])
        )
        joined_events.append(joined_event['Items'][0])

    profile_response = table.query(
        IndexName="item_type_index",
        KeyConditionExpression=Key('item_type').eq('account'),
        FilterExpression=Attr('username').eq(username)
    )

    image_url = s3_client.generate_presigned_url('get_object',
                                                 Params={
                                                     'Bucket': BUCKET,
                                                     'Key': profile_response['Items'][0]['profile_image'],
                                                 },
                                                 ExpiresIn=3600)
    profile = {
        'username': username,
        'email':  host_response['Items'][0]['email'],
        'number':  host_response['Items'][0]['phone_number'],
        'image_url': image_url,
        'hosted_events': hosted_events_response['Items'],
        'joined_events': joined_events#joined_events_response['Items']
    }
    urls = {
        'events': url_for('index'),
        'messages': url_for('messages'),
        'profile': url_for('profile')
    }
    return render_template('profile.html',
                           profile=profile,
                           urls=urls,
                           show_time=datetime.fromtimestamp)


@webapp.route('/event', methods=['GET'])
@login_required
def event():
    try:
        username = request.args.get('username')
        start_time = int(request.args.get('timestamp'))
        event_response = dynamodb.Table('Events').query(
            KeyConditionExpression=Key('username').eq(
                username) & Key('start_time').eq(start_time)
        )
        host_response = dynamodb.Table('Events').query(
            KeyConditionExpression=Key('username').eq(
                username),
            FilterExpression=Attr('item_type').eq("account")
        )
        participant_response = dynamodb.Table('Events').query(
            IndexName='item_type_index',
            KeyConditionExpression=Key('start_time').eq(
                start_time) & Key('item_type').eq('participant')
        )
        review_response = dynamodb.Table('Events').query(
            KeyConditionExpression=Key('username').eq(username),
            FilterExpression=Attr('item_type').eq('rating')
        )

        event = {
            'username': host_response['Items'][0]['username'],
            'email': host_response['Items'][0]['email'],
            'phone_number':  host_response['Items'][0]['phone_number'],
            'review': _calculate_average_review_start(review_response['Items']),
            'start_time': str(datetime.fromtimestamp(event_response['Items'][0]['start_time'])),
            'end_time': str(datetime.fromtimestamp(event_response['Items'][0]['end_time'])),
            'address': event_response['Items'][0]['address'],
            'title': event_response['Items'][0]['title'],
            'start_time_int': event_response['Items'][0]['start_time'],
            'end_time_int': event_response['Items'][0]['end_time'],
            'participant_count': len(participant_response['Items']),
            'required_participant_count': event_response['Items'][0]['required_parti_num']
        }
        return render_template('event.html', event=event, urls={
            'events': url_for('index'),
            'messages': url_for('messages'),
            'profile': url_for('profile'),
            'join': url_for('events.join')
        })
    except (botocore.exceptions.ClientError, AssertionError) as e:
        return e.args


@webapp.route('/users/message', methods=['GET'])
@login_required
def messages():
    username = g.user
    receiver = ''
    if 'receiver' in request.args:
        receiver = request.args.get('receiver')
        send_message = " "
        start_time = int(datetime.utcnow().strftime("%s"))
        item_type = 'message'

        response = table.put_item(
            Item={
                'username': username,
                'start_time': start_time,
                'message': send_message,
                'item_type': item_type,
                'receiver': receiver,
            }
        )
    return render_template('messages.html',
                           username=username,
                           receiver=receiver,
                           urls={
                               'events': url_for('index'),
                               'messages': url_for('messages'),
                               'profile': url_for('profile')
                           })


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return int(obj)
    raise TypeError


def _calculate_average_review_start(items):
    star = 0
    for item in items:
        star += int(item['star'])

    if star > 0:
        star = star // len(items)

    return star
