import json
from datetime import datetime

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, session, url_for)

import app

import json
from datetime import datetime
import app

from .auth import login_required

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')
bp = Blueprint("events", __name__, url_prefix='/events')


@bp.route('/', methods=['GET', 'POST'])
@login_required
def events():

    try:
        if request.method == 'GET':
            response = table.query(
                IndexName='item_type_index',
                KeyConditionExpression=Key('item_type').eq('host')
            )
            return json.dumps({
                'isSuccess': True,
                'data': response['Items']
            }, default=app.decimal_default)
        if request.method == "POST":
            table.put_item(
                Item={
                    'username': 'eric',#session.get('username'),
                    'start_time': int(datetime.fromisoformat(request.form['start_time']).timestamp()),
                    'end_time': int(datetime.fromisoformat(request.form['end_time']).timestamp()),
                    'title': request.form['title'],
                    'required_parti_num': request.form['required_participant_number'],
                    'address': request.form['address'],
                    'is_active': 1,
                    'item_type': 'host',
                    'event_type': request.form['event_type']
                })
            return jsonify({
                'isSuccess': True,
                'url': url_for('index')
            })

    except (botocore.exceptions.ClientError, AssertionError) as e:
        return jsonify({
            'isSucess': False,
            'message': e.args
        })



@bp.route('/join', methods=['POST'])
@login_required
def join():
    try:
        username = session.get('username')
        start_time = int(request.get_json()['start_time'])
        end_time = int(request.get_json()['end_time'])
        response_host = table.query(
            KeyConditionExpression=Key('username').eq(username))

        for i in response_host["Items"]:
            if i['item_type'] != 'account' \
                    and _is_conflict(int(i["start_time"]), int(i["end_time"]), start_time, end_time):
                return jsonify({
                    'isSuccess': False,
                    'message': 'you have a time conflict'
                })
        table.put_item(
            Item={
                'username': username,
                'start_time': start_time,
                'end_time': end_time,
                'item_type': 'participant',
            })
        return jsonify({
            'isSucess': True
        })
    except ClientError as e:
        return jsonify({
            'isSuccess': False,
            'message': e.args
        })


@bp.route('/rate', methods=['POST'])
@login_required
def rate():
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


@bp.route('/drop', methods=['POST'])
@login_required
def dropout():
    try:
        table.delete_item(
            Key={
                'username': request.get_json()['username'],
                'start_time': request.get_json()['start_time']
            })
        return jsonify({
            'isSuccess': True
        })
    except ClientError as e:
        return jsonify({
            'isSuccess': False,
            'message': e.args
        })


def _is_conflict(s1, e1, s2, e2):
    return not (s1 >= e2 or s2 >= e1)


if __name__ == "__main__":
    pass
