import json

import boto3
from boto3.dynamodb.conditions import Attr, Key
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

from app import webapp

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
bp = Blueprint("events", __name__, url_prefix='/events')


@bp.route('/', methods=['GET', 'POST'])
def events():
    table = dynamodb.Table('Events')
    response = table.put_item(
        Item={
            'host_id': 'eric',
            'date': '2020/03/02',
                    'title': 'tennis',
                    'type': 'sports',
                    'required_parti_num': 2,
                    'participants_id': [],
                    'address': 'st george',
                    'is_active': 1,
                    'reviews': []

        })
    # flash('Registration Success! Please login.', 'success')


@bp.route('/join', methods=['POST'])
def join_event():
    return 'join event'


@bp.route('/rate', methods=['POST'])
def rate_event():
    return 'rate events'

# if __name__== "__main__":
#   createEvent()
