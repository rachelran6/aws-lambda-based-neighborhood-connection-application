import json

import boto3
from boto3.dynamodb.conditions import Attr, Key
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
import app

# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
bp = Blueprint("events", __name__, url_prefix='/events')


@bp.route('/', methods=['GET', 'POST'])
def events():
    table = app.dynamodb.Table('Events')
    table.put_item(
        data={
            'username': 'eric',
            'date': '1585462294', #timestamp
            'title': 'tennis',
            'required_parti_num': 10,
            'address': 'st george',
            'is_active': 1,
            'stars': 5,
            'type': 'host'
        })
    # flash('Registration Success! Please login.', 'success')


@bp.route('/join', methods=['POST'])
def join_event():
    table = app.dynamodb.Table('Events')
    table.put_item(
        data={
            'username': 'eric',
            'date': '1585462294',  # timestamp
            'title': 'tennis',
            'type': 'participant'
        })

    return 'join event'


@bp.route('/rate', methods=['POST'])
def rate_event():
    table = app.dynamodb.Table('Events')
    response = table.update_item(
        Key={
            'username': 'eric',
            'date': '1585462294',  # timestamp
            'title': 'tennis',
            'type': 'participant'
        },
        UpdateExpression="set star = :r",
        ExpressionAttributeValues={
            ':r': 3,
        },
        ReturnValues="UPDATED_NEW"
    )

    return 'rate events'

# if __name__== "__main__":
#   createEvent()
