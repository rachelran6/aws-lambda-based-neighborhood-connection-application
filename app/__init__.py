from flask import Flask, render_template
from flask_dynamo import Dynamo

from app import auth, events, users
import boto3
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.register_blueprint(auth.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(users.bp)

    table_name = 'Events'
    table_names = [table.name for table in dynamodb.tables.all()]
    if table_name not in table_names:
        response = dynamodb.create_table(
            TableName='Events',
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'date',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'date',
                    'AttributeType': 'N'
                },

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    return app


# @app.route('/', methods=['GET'])
# def index():
#     return render_template('index.html')
