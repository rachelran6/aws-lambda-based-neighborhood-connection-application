from flask import Flask, render_template

from app import auth, events, users

webapp = Flask(__name__, instance_relative_config=True)


webapp.register_blueprint(auth.bp)
webapp.register_blueprint(events.bp)
webapp.register_blueprint(users.bp)


@webapp.route('/', methods=['GET'])
def index():
    return render_template('index.html')
