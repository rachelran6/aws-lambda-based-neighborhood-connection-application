from flask import Blueprint, request, jsonify, abort, url_for, redirect
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
import botocore
import boto3

bp = Blueprint("users", __name__, url_prefix='/users')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')


@bp.route('/', methods=['GET'])
def users():

    return 'users index'


@bp.route('/messages', methods=['GET', 'POST', 'DELETE'])
def messages():
    username = 'username'
    receiver = 'receiver'
    message_sent = {}
    message_received = {}
    try:
        if request.method == 'GET':
            response_sender = table.query(
                IndexName="item_typeIndex",
                KeyConditionExpression=Key('item_type').eq('message'),
                FilterExpression=Attr('username').eq(username) & Attr('receiver').eq(receiver)
            )
            if response_sender["Items"]:
                for i in response_sender["Items"]:
                    message_sent[i["start_time"]] = i["message"]

            response_receiver = table.query(
                IndexName="item_typeIndex",
                KeyConditionExpression=Key('item_type').eq('message'),
                FilterExpression=Attr('username').eq(receiver) & Attr('receiver').eq(username)
            )
            if response_receiver["Items"]:
                for i in response_receiver["Items"]:
                    message_received[i["start_time"]] = i["message"]

            message_sent = sorted(message_sent.keys())
            message_received = sorted(message_received.keys())
            if len(message_sent) == 0 & len(message_received) == 0:
                return "no messages"
            else:
                return message_sent, message_received

        elif request.method == 'POST':
            username = 'username'
            message = 'this is a message'
            start_time = datetime.utcnow()
            item_type = 'message'
            receiver = 'receiver'

            response = table.put_item(
                Item={
                    'username': username,
                    'start_time': start_time,
                    'message': message,
                    'item_type': item_type,
                    'receiver': receiver
                }
            )

            return jsonify({
                'isSuccess': True,
                'response': response
            })

        elif request.method == 'DELETE':

            return jsonify({
                'isSuccess': True,
            })
        else:
            abort(405)
    except botocore.exceptions.ClientError as e:
        return jsonify({
            'isSuccess': False,
            'message': e.args
        })

    return 'user message'
