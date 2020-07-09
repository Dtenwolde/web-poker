from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flaskr import app
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('poker', __name__)

@app.route('/')
@login_required
def index():
    db = get_db()
    rooms = db.execute(
        'SELECT r.id, room, temp_password, created, author_id, username'
        ' FROM room r JOIN user u ON r.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('poker/index.html', rooms=rooms)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        roomName = request.form['roomName']
        password = request.form['password']
        error = None
        if not roomName:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO room (room, temp_password, author_id)'
                ' VALUES (?, ?, ?)',
                (roomName, password, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('poker/create.html')


def get_room(id, check_author=True):
    room = get_db().execute(
        'SELECT r.id, room, temp_password, created, author_id, username'
        ' FROM room r JOIN user u ON r.author_id = u.id'
        ' WHERE r.id = ?',
        (id,)
    ).fetchone()
    if room is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return room

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_room(id)

    if request.method == 'POST':
        title = request.form['password']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('poker.index'))

    return render_template('poker/update.html', room=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_room(id)
    db = get_db()
    db.execute('DELETE FROM room WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('poker.index'))


@bp.route('/<int:id>/join', methods=('GET', 'POST'))
@login_required
def join(id):
    room = get_room(id)
    return render_template('poker/room.html', room=room)

@bp.route('/<int:id>/lobbySettings', methods=('GET',))
@login_required
def lobby_settings(id):
    room = get_room(id)
    return render_template('poker/room.html', room=room)