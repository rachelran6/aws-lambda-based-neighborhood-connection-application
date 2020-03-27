from flask import Flask

webapp = Flask(__name__, instance_relative_config=True)


@webapp.route('/')
def index():
    return "hello world"
