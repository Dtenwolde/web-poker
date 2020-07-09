import os
from flask_socketio import SocketIO

from flask import Flask


global app
global sio


def create_app(test_config=None):
    global app
    global sio
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    sio = SocketIO(app, async_mode='gevent')
    from flaskr import mysocket

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    from flaskr import db
    db.init_app(app)

    from flaskr import auth
    app.register_blueprint(auth.bp)

    from flaskr import poker
    app.register_blueprint(poker.bp)
    app.add_url_rule('/', endpoint='index')

create_app()