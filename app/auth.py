from flask import Blueprint,Flask, render_template
from flask_dynamo import Dynamo
import app

bp = Blueprint("auth", __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    return 'login page'


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # hardcoding
    username = 'username'
    password = 'password'

    app.dynamo.tables['Events'].put_item(data={
        'username': username,
        'password': password,
    })


    return 'register page'
