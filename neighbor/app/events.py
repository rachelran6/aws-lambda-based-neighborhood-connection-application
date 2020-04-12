import json
from datetime import datetime

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for, g)

import app

import json
from datetime import datetime
import app

from .auth import login_required

table = boto3.resource('dynamodb', region_name='us-east-1').Table('Events')
bp = Blueprint("events", __name__, url_prefix='/events')


@bp.route('/', methods=['GET', 'POST'])
@login_required
def events():
    try:
        if request.method == 'GET':
            response = table.query(
                IndexName='item_type_index',
                KeyConditionExpression=Key('item_type').eq('host'),
                FilterExpression=Attr('is_active').eq(1)
            )
            return json.dumps({
                'isSuccess': True,
                'data': response['Items']
            }, default=app.decimal_default)
        if request.method == "POST":
            table.put_item(
                Item={
                    'username': g.user,
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
        username = g.user
        start_time = int(request.get_json()['start_time'])
        end_time = int(request.get_json()['end_time'])
        title = request.get_json()['title']
        address = request.get_json()['address']
        required_parti_num = request.get_json()['required_participant_count']

        response_participants = table.query(
            IndexName='item_type_index',
            KeyConditionExpression=Key('item_type').eq('participant')&Key('start_time').eq(start_time),
            FilterExpression= Attr('title').eq(title)
        )

        assert len(response_participants['Items'])<int(required_parti_num), "This event is full"

        response_host = table.query(
            KeyConditionExpression=Key('username').eq(username),
            FilterExpression=Attr('item_type').eq('host') | Attr('item_type').eq('participant'))
        for i in response_host["Items"]:
            if _is_conflict(int(i["start_time"]), int(i["end_time"]), start_time, end_time):
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
                'title': title,
                'address': address
            })
        return jsonify({
            'isSuccess': True
        })
    except ClientError as e:
        return jsonify({
            'isSuccess': False,
            'message': e.args
        })
    except AssertionError as e:
        return jsonify({
            'isSuccess': False,
            'message': e.args
        })


@bp.route('/rate', methods=['POST'])
@login_required
def rate():
    try: 
        username = request.form['username']
        self_username = request.cookies.get('username')
        rating = int(request.form['rating'])
        title = request.form['title']
        start_time = int(datetime.fromisoformat(request.form['start_time']).timestamp())
        
        assert self_username != username, "You cannot rate yourself."

        response = table.query(
            KeyConditionExpression=Key('username').eq(self_username) & Key('start_time').eq(start_time)
        )
        assert len(response['Items'])!=0, "You are not one of the participants of this event"

        response = table.query(
            KeyConditionExpression=Key('username').eq(username),
            FilterExpression = Attr('rater').eq(self_username) & Attr('title').eq(title)
        )
        assert len(response['Items'])==0, "You have already rated this host"

        table.put_item(
            Item={
                'username': username,
                'start_time': int(datetime.utcnow().strftime("%s")),
                'item_type': 'rating',
                'rater': self_username,
                'star': rating,
                'title': title
            })
        return jsonify({
            'isSuccess': True
        })
    except AssertionError as e:
        return jsonify({
            'isSuccess': False,
            'message': e.args
        })

@bp.route('/dropout', methods=['DELETE'])
@login_required
def dropout():
    try:
        print(request.get_json())
        table.delete_item(
            Key={
                'username': g.user,
                'start_time': int(request.get_json()['start_time'])
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
