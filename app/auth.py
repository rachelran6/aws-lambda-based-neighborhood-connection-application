from flask import Blueprint,Flask, render_template, request
from botocore.exceptions import ClientError
import app
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr

bp = Blueprint("auth", __name__, url_prefix='/auth')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        username = 'username'
        password = 'password'

        response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        if response["Items"]:
            for i in response["Items"]:
                if password==i["password"]:
                    return "login successfully"
        else:
            return "username or password wrong"
    return "login page"


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # hardcoding
    if request.method == "POST":
        username = 'username'
        password = 'password'
        start_time = 000000 # member since
        item_type = 'account'

        response = table.query(
            KeyConditionExpression=Key('username').eq(username) & Key('start_time').eq(start_time)
        )
        if response[u'Items']:
            return "username exists"
        response = table.put_item(
            Item={
                'username': username,
                'start_time': start_time,
                'password' : password,
                'item_type' : item_type
            }
        )

        return response

