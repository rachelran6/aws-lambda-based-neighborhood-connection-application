from flask import Blueprint

bp = Blueprint("users", __name__, url_prefix='/users')


@bp.route('/', methods=['GET', 'POST'])
def users():
    return 'users index'


@bp.route('/messages', methods=['GET', 'POST'])
def messages():
    return 'user message'
