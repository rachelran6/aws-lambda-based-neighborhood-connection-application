import decimal
import functools
import logging
import re
from datetime import datetime
import bcrypt
import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError
from flask import (Blueprint, g, jsonify, redirect, render_template, request,
                   session, url_for)

import app

bp = Blueprint("auth", __name__, url_prefix='/auth')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Events')


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        logger = logging.getLogger('manager')
        if g.user is None:
            logger.info("user yet logged in, redirecting log-in page")
            return redirect(url_for("auth.login"))
        logger.info('user already logged in')
        return view(**kwargs)
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():

    username = session.get('username')

    if username is None:
        g.user = None

    g.user = username


def _authenticate(username, password):

    assert username is not None, "invalid username"
    assert password is not None, "invalid password"

    response = table.get_item(
        KeyConditionExpression=Key('username').eq(username)
    )

    user = response['items'][0]

    assert user is not None, "invalid credential"
    assert bcrypt.checkpw(password.encode('utf-8'),
                          user['password'].encode('utf-8')), "invalid credential"


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    try:
        username = request.form['username']
        password = request.form['password']

        _authenticate(username, password)

        session.clear()
        session.permanent = True

        session['username'] = username

        return jsonify({
            'isSuccess': True,
            'url': url_for('dashboard')
        })

    except AssertionError as e:
        return jsonify({
            'isSuccess': False,
            'message': e.args
        })


@bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html')

    try:

        username = request.form['username']
        password = request.form['password']

        assert username is not None, "Please enter username"
        assert password is not None, "Please enter password"

        result_name = r'^[A-Za-z0-9._-]{2,100}$'
        result_password = r'^.{6,}$'

        assert re.match(result_name, username, re.M | re.I)
        "Username should have 2 to 100 characters, and only contains letter, number, underline and dash."
        assert re.match(result_password, password)
        "Password should have 6 to 18 characters"

        response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        assert len(response['Items']) == 0, "username exists"

        response = table.put_item(
            Item={
                'username': username,
                'start_time': int(datetime.utcnow().strftime('%s')),
                'password': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()),
                'item_type': 'account'
            }
        )
        return jsonify({
            'isSuccess': True
        })

    except (botocore.exceptions.ClientError, AssertionError) as e:
        return jsonify({
            'isSuccess': False,
            'message': e.args
        })
