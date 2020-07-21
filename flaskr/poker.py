from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flaskr import app
from werkzeug.exceptions import abort

from flaskr.auth import require_login

from flaskr.lib.database import request_session
from flaskr.lib.models.models import RoomModel
from flaskr.lib.repository import room_repository
from flaskr.lib.user_session import session_user

bp = Blueprint('poker', __name__)


@app.route('/')
@require_login()
def index():
    rooms = room_repository.get_rooms()

    return render_template('poker/index.html', rooms=rooms)


@app.route('/store')
@require_login()
def store():
    return render_template('poker/store.html')


@bp.route('/create', methods=('GET', 'POST'))
@require_login()
def create():
    if request.method == 'POST':
        room_name = request.form['roomName']
        password = request.form.get("password", "")

        error = None
        if not room_name:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = request_session()
            room = RoomModel(room_name, session_user(), password)
            db.add(room)
            db.commit()
            return redirect(url_for('index'))

    return render_template('poker/create.html')


def get_room(room_id, check_author=False):
    room = room_repository.get_room(room_id)

    if check_author and room.author != session_user():
        abort(401, "Room id {0} doesn't belong to you.".format(room_id))
    if room is None:
        abort(404, "Room id {0} doesn't exist.".format(room_id))

    return room


@bp.route('/<int:room_id>/join', methods=('GET', 'POST'))
@require_login()
def join(room_id):
    room = get_room(room_id)
    return render_template('poker/room.html', room=room)


@bp.route('/<int:room_id>/roomSettings', methods=('GET',))
@require_login()
def room_settings(room_id):
    room = get_room(room_id)
    return render_template('poker/room_settings.html', room=room)


@bp.route('/<int:room_id>/game', methods=('GET',))
@require_login()
def game(room_id):
    room = get_room(room_id)

    return render_template('poker/game.html', room=room)
