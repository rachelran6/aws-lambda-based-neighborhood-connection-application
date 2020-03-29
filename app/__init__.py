from flask import Flask, render_template

from app import auth, events, users
from datetime import datetime
import boto3
# from apscheduler.schedulers.background import BackgroundScheduler

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
# scheduler = BackgroundScheduler()


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
                    'AttributeName': 'start_time',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'start_time',
                    'AttributeType': 'N'
                },

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    update_table()
    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/profile', methods=['GET'])
    def profile():
        profile = {
            'username': 'maxxx580',
            'self': True,
            'joined_events': [{
                'title': 'event title 1',
                'address': '215 queen',
                'start_time': datetime.utcnow(),
                'end_time': '123345667',
                'rating': '4'
            }],
            'hosted_events': [{
                'title': 'event title 2',
                'address': '225 queen',
                'start_time': datetime.utcnow(),
                'end_time': '123345667',
                'rating': '4'
            }],
            'messages': [
                {
                    'from': 'user 1',
                    'time': datetime.utcnow(),
                    'text': 'message 1'
                },
                {
                    'from': 'user 2',
                    'time': datetime.utcnow(),
                    'text': 'message 2'
                }
            ]
        }
        return render_template('profile.html', profile=profile)
    return app


def update_table():
    try:
        resp = dynamodb_client.update_table(
            TableName="Events",
            # Any attributes used in your new global secondary index must be declared in AttributeDefinitions
            AttributeDefinitions=[
                {
                    "AttributeName": "item_type",
                    "AttributeType": "S"
                },
            ],
            # This is where you add, update, or delete any global secondary indexes on your table.
            GlobalSecondaryIndexUpdates=[
                {
                    "Create": {
                        # You need to name your index and specifically refer to it when using it for queries.
                        "IndexName": "item_type",
                        # Like the table itself, you need to specify the key schema for an index.
                        # For a global secondary index, you can use a simple or composite key schema.
                        "KeySchema": [
                            {
                                "AttributeName": "item_type",
                                "KeyType": "HASH"
                            }
                        ],
                        # You can choose to copy only specific attributes from the original item into the index.
                        # You might want to copy only a few attributes to save space.
                        "Projection": {
                            "ProjectionType": "ALL"
                        },
                        # Global secondary indexes have read and write capacity separate from the underlying table.
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 1,
                            "WriteCapacityUnits": 1,
                        }
                    }
                }
            ],
        )
        print("Secondary index added!")
    except Exception as e:
        print("Error updating table:")
        print(e)
