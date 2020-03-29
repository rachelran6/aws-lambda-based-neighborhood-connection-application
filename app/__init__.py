from flask import Flask, render_template
from flask_dynamo import Dynamo

from app import auth, events, users

webapp = Flask(__name__, instance_relative_config=True)


webapp.register_blueprint(auth.bp)
webapp.register_blueprint(events.bp)
webapp.register_blueprint(users.bp)
dynamo = Dynamo()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['DYNAMO_TABLES'] = [{
        'TableName' : "Events",
        'KeySchema': [
            { 'AttributeName': "username", 'KeyType': "HASH"},    # Partition key
            { 'AttributeName': "date", 'KeyType': "RANGE" }   # Sort key
        ],
        'AttributeDefinitions': [
            # Users' info
            { 'AttributeName': "username", 'AttributeType': "S" },
            # { 'AttributeName': "password", 'AttributeType': "S"},
            # Events' info
            # { 'AttributeName': "title", 'AttributeType': "S"},
            # { 'AttributeName': "required_parti_num", 'AttributeType': "N"},
            # { 'AttributeName': "address", 'AttributeType': "S"},
            # { 'AttributeName': "is_active", 'AttributeType': "N"},
            { 'AttributeName': "date", 'AttributeType': "N" },
            # { 'AttributeName': "stars", 'AttributeType': "N"},
            # # User-Event pair
            # { 'AttributeName': "type", 'AttributeType': "S"}
        ],
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    }]


    dynamo.init_app(app)
    with app.app_context():
        dynamo.create_all()

    return app


@webapp.route('/', methods=['GET'])
def index():
    return render_template('index.html')
