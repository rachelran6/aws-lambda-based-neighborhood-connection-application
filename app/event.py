from flask import render_template, session, flash, redirect, url_for, request
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# @webapp.route('/createEvent', methods=['GET', 'POST'])
def createEvent():
    table = dynamodb.Table('Events')
    response = table.put_item(
                Item={
                    'host_id': 'eric',
                    'date': '2020/03/02',
                    'title': 'tennis',
                    'type': 'sports',
                    'required_parti_num': 2,
                    'participants_id': [],
                    'address':'st george',
                    'is_active':1,
                    'reviews':[]

                })
    # flash('Registration Success! Please login.', 'success')

# if __name__== "__main__":
#   createEvent()