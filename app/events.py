import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, session, url_for)

import app

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')
bp = Blueprint("events", __name__, url_prefix='/events')


@bp.route('/', methods=['GET', 'POST'])
def events():
    try:
        if request.method == 'GET':
            response = table.query(
                IndexName='item_type_index',
                KeyConditionExpression=Key('item_type').eq('host')
            )

            return jsonify({
                'isSuccess': True,
                'data': response['Items']
            })
        if request.method == "POST":
            response = table.put_item(
                Item={
                    'username': 'eric',
                    'start_time': 1585462294,  # timestamp
                    'title': 'tennis',
                    'required_parti_num': 10,
                    'address': 'st george',
                    'is_active': 1,
                    'item_type': 'host',
                    'end_time': 1585492294,  # seconds
                    'event_type': "sports",
                }
            )
            return response
    except (botocore.exceptions.ClientError, AssertionError) as e:
        return jsonify({
            'isSucess': False,
            'message': e.args
        })


@bp.route('/join', methods=['POST'])
def join_event():
    if request.method == "POST":

        username = 'sara'
        start_time = 1585462294
        end_time = 1585492294
        response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )

        if response["Items"]:
            for i in response["Items"]:
                if end_time < i["start_time"] or start_time > i["end_time"]:
                    pass
                else:
                    return "Your events have conflicts"

        response = table.put_item(
            Item={
                'username': 'sara',
                'start_time': 1585462294,
                'end_time': 1585492294,  # current timestamp
                'title': 'tennis',
                'item_type': 'participant',
            })
        return "participants added to event"


@bp.route('/rate', methods=['POST'])
def rate_event():
    response = table.update_item(
        Key={
            'username': 'sara',
            'start_time': 1585462294
        },
        UpdateExpression="SET stars= :var1",
        ExpressionAttributeValues={
            ':var1': 1
        },
        ReturnValues="UPDATED_NEW"

    )
    return 'rate events'


@bp.route('/dropout', methods=['DELETE'])
def dropout_event():
    try:
        response = table.delete_item(
            Key={
                'username': 'sara',
                'start_time': 1585462294
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
        else:
            raise
    else:
        print("DeleteItem succeeded:")
    return response


# if __name__== "__main__":
#   createEvent()
