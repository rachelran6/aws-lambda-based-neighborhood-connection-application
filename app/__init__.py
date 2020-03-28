from flask import Flask, render_template

webapp = Flask(__name__, instance_relative_config=True)


@webapp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@webapp.route('/user', methods=['GET', 'POST', 'PUT'])
def user():
    pass
