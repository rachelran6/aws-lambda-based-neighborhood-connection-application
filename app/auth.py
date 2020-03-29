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
            # TODO: add password check
            # ProjectionExpression="#yr, title, info.genres, info.actors[0]",
            # ExpressionAttributeNames={"#yr": "year"},  # Expression Attribute Names for Projection Expression only.
            KeyConditionExpression=Key('username').eq(username)
        )
        if response["Items"]:
            for i in response["Items"]:
                if password==i["password"]:
                    return "login page"
        else:
            return "username or password wrong"

    return 'login page'


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # hardcoding
    if request.method == "POST":
        username = 'username'
        password = 'password'
        date = 000000 # member since
        item_type = 'account'

        response = table.query(
            KeyConditionExpression=Key('username').eq(username) & Key('date').eq(date)
        )
        if response[u'Items']:
            return "username exists"
        response = table.put_item(
            Item={
                'username': username,
                'date': date,
                'password' : password,
                'item_type' : item_type
            }
        )

        return response

#Convert dynamodb item to JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)