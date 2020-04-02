import decimal

from flask import Blueprint, request, jsonify, abort, url_for, redirect
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
import botocore
import boto3
import json

bp = Blueprint("users", __name__, url_prefix='/users')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')


@bp.route('/', methods=['GET'])
def users():
    return 'users index'


@bp.route('/messages', methods=['GET', 'POST', 'DELETE'])
def messages():
    try:
        if request.method == 'GET':
            get_receiver = request.args.get('receiver')
            get_username = request.args.get('username')
            print("~~~~~~~~~ receiver: "+get_receiver)
            print("~~~~~~~~~ username: "+get_username)
            messages_dict = {}
            sorted_messages_dict = {}
            this_dict = {}
            response_sender = table.query(
                IndexName="item_type_index",
                KeyConditionExpression=Key('item_type').eq('message'),
                FilterExpression=Attr('username').eq(get_username) & Attr('receiver').eq(get_receiver)
            )
            response_receiver = table.query(
                IndexName="item_type_index",
                KeyConditionExpression=Key('item_type').eq('message'),
                FilterExpression=Attr('username').eq(get_receiver) & Attr('receiver').eq(get_username)
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
        if len(contact_set) == 0:
            return jsonify({
                'isSuccess': False,
            })
        else:
            return jsonify({
                'isSuccess': True,
                'contacts': str(list(contact_set)),
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
