import functools

from flaskr.lib.repository import user_repository
from flaskr.lib.user_session import session_user_set, session_is_authed
from flaskr.lib.models.models import UserModel
import bcrypt

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.lib.database import request_session
from werkzeug.exceptions import Unauthorized

def require_login():
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not session_is_authed():
                redirect(url_for('auth.login'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = request_session()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            usermodel = user_repository.get_user(username=username)  
            if usermodel is not None:
                error = 'User {} is already registered.'.format(username)
            else:
                usermodel = UserModel(username, password)
                db.add(usermodel)
                db.commit()
                session_user_set(usermodel)

                return redirect(url_for('index'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sqlalchemy_db = request_session()
        usermodel = user_repository.get_user(username=username)
        error = None
        if usermodel is None:
            error = 'Incorrect username.'
        elif not bcrypt.checkpw(password.encode(), usermodel.password):
            error = 'Incorrect password.'

        if error is None:
            session_user_set(usermodel)
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')



@bp.route('/logout')
@require_login()
def logout():
    session_user_set(None)
    return redirect(url_for('index'))


