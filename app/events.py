import json

import boto3
from boto3.dynamodb.conditions import Attr, Key
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
import app


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')
# table_client = dynamodb_client.table('Events')
bp = Blueprint("events", __name__, url_prefix='/events')


@bp.route('/', methods=['GET', 'POST'])
def events():
    if request.method == "POST":
        response = table.put_item(
            Item={
                'username': 'eric',
                'date': 1585462294,  # timestamp
                'title': 'tennis',
                'required_parti_num': 10,
                'address': 'st george',
                'is_active': 1,
                'item_type': 'host',
                'endtime': 100000, #seconds
                'event_type': "sports"
            }
        )
        return response

    # flash('Registration Success! Please login.', 'success')


@bp.route('/join', methods=['POST'])
def join_event():
    if request.method == "POST":

        response = table.put_item(
            Item={
                'username': 'sara',
                'date': 158546224,  # current timestamp
                'title': 'tennis',
                'item_type': 'participant'
            })

        return response


@bp.route('/rate', methods=['POST'])
def rate_event():
    response = table.update_item(
        Key={
            'username': 'sara',
            'date': 158546224,  # current timestamp
        },
        UpdateExpression="SET stars= :var1",
        ExpressionAttributeValues={
                ':var1': 1
                },
        ReturnValues="UPDATED_NEW"

            )
    return 'rate events'

# if __name__== "__main__":
#   createEvent()
