import decimal
import json
from datetime import datetime

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from flask import Blueprint, abort, jsonify, redirect, request, url_for

from .auth import login_required

bp = Blueprint("users", __name__, url_prefix='/users')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')
s3_client = boto3.client('s3')
BUCKET = "ece1779-a3-pic"


@bp.route('/', methods=['GET'])
@login_required
def users():
    return 'users index'


@bp.route('/messages', methods=['GET', 'POST', 'DELETE'])
@login_required
def messages():
    try:
        if request.method == 'GET':
            get_receiver = request.args.get('receiver')
            get_username = request.args.get('username')

            response = table.query(
                IndexName="item_type_index",
                KeyConditionExpression=Key('item_type').eq('account'),
                FilterExpression=Attr('username').eq(get_receiver)
            )

            if response["Items"]:
                for i in response["Items"]:
                    if str(i["profile_image"]) == "profile image":
                        image_url = "false"
                    else:
                        image_name = str(i["profile_image"])
                        image_url = s3_client.generate_presigned_url('get_object',
                                                                     Params={
                                                                         'Bucket': BUCKET,
                                                                         'Key': image_name,
                                                                     },
                                                                     ExpiresIn=3600)
            messages_dict = {}
            sorted_messages_dict = {}
            this_dict = {}
            response_sender = table.query(
                IndexName="item_type_index",
                KeyConditionExpression=Key('item_type').eq('message'),
                FilterExpression=Attr('username').eq(
                    get_username) & Attr('receiver').eq(get_receiver)
            )
            response_receiver = table.query(
                IndexName="item_type_index",
                KeyConditionExpression=Key('item_type').eq('message'),
                FilterExpression=Attr('username').eq(
                    get_receiver) & Attr('receiver').eq(get_username)
            )

            if response_sender["Items"]:
                for i in response_sender["Items"]:
                    this_time = json.dumps(i['start_time'], cls=DecimalEncoder)
                    this_dict.clear()
                    this_dict["message"] = str(i["message"])
                    this_dict["sender"] = str(i["username"])
                    this_dict["receiver"] = str(i["receiver"])
                    messages_dict[this_time] = json.dumps(this_dict)

            if response_receiver["Items"]:
                for i in response_receiver["Items"]:
                    this_time = json.dumps(i['start_time'], cls=DecimalEncoder)
                    this_dict.clear()
                    this_dict["message"] = str(i["message"])
                    this_dict["sender"] = str(i["username"])
                    this_dict["receiver"] = str(i["receiver"])
                    messages_dict[this_time] = json.dumps(this_dict)

            for key in sorted(messages_dict.keys(), reverse=False):
                sorted_messages_dict[key] = messages_dict[key]
            if len(sorted_messages_dict) == 0:
                return jsonify({
                    'isSuccess': False,
                })
            else:
                return jsonify({
                    'isSuccess': True,
                    'messages': sorted_messages_dict,
                    'image_url': image_url,
                })

        elif request.method == 'POST':
            data = request.get_json()
            send_message = data['message']
            send_receiver = data['receiver']
            send_username = data['username']
            start_time = int(datetime.utcnow().strftime("%s"))
            item_type = 'message'

            response = table.put_item(
                Item={
                    'username': send_username,
                    'start_time': start_time,
                    'message': send_message,
                    'item_type': item_type,
                    'receiver': send_receiver,
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


@bp.route('/messages_contacts', methods=['GET'])
@login_required
def messages_contacts():
    username = request.args.get('username')
    try:
        contact_list = []
        response_sender_all = table.query(
            IndexName="item_type_index",
            KeyConditionExpression=Key('item_type').eq('message'),
            FilterExpression=Attr('username').eq(username)
        )
        response_receiver_all = table.query(
            IndexName="item_type_index",
            KeyConditionExpression=Key('item_type').eq('message'),
            FilterExpression=Attr('receiver').eq(username)
        )
        if response_sender_all["Items"]:
            for i in response_sender_all["Items"]:
                contact_list.append(str(i["receiver"]))
        if response_receiver_all["Items"]:
            for i in response_receiver_all["Items"]:
                contact_list.append(str(i["username"]))
        contact_set = set(contact_list)

        url_list = []
        for each in contact_set:
            response = table.query(
                IndexName="item_type_index",
                KeyConditionExpression=Key('item_type').eq('account'),
                FilterExpression=Attr('username').eq(each)
            )

            if response["Items"]:
                for i in response["Items"]:
                    if str(i["profile_image"]) == "profile image":
                        image_url = "false"
                    else:
                        image_name = str(i["profile_image"])
                        image_url = s3_client.generate_presigned_url('get_object',
                                                                     Params={
                                                                         'Bucket': BUCKET,
                                                                         'Key': image_name,
                                                                     },
                                                                     ExpiresIn=3600)
                    url_list.append(image_url)

        if len(contact_set) == 0:
            return jsonify({
                'isSuccess': False,
            })
        else:
            return jsonify({
                'isSuccess': True,
                'contacts': str(list(contact_set)),
                'image_url': str(url_list),
            })

    except botocore.exceptions.ClientError as e:
        return jsonify({
            'isSuccess': False,
            'message': e.args
        })


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)
