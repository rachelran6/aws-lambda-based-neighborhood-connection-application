from flask import Blueprint,Flask, render_template, request
from botocore.exceptions import ClientError
import app
import boto3
import json
import decimal

bp = Blueprint("auth", __name__, url_prefix='/auth')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')

@bp.route('/login', methods=['GET', 'POST'])
def login():



    return 'login page'


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # hardcoding
    # if request.method == "POST":
    #     username = 'username'
    #     password = 'password'
    #     date = -1
    #
    #     try:
    #         response = table.get_item(
    #             Key={
    #                 'username': username,
    #                 'date': date
    #             }
    #         )
    #     except ClientError as e:
    #         print(e.response['Error']['Message'])
    #     else:
    #         item = response['Item']
    #         print("GetItem succeeded:")
    #         print(json.dumps(item, indent=4, cls=DecimalEncoder))



        return "register"
