import sqlite3

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import BadRequestKeyError

from .auth import login_required
from .db import get_db




bp = Blueprint('trusted_users', __name__, url_prefix='/trusted_users')

@bp.route('/')
@login_required
def view():
    db = get_db()
    db.row_factory = None

    queries = db.execute("SELECT UserID2 FROM TrustedUsers WHERE UserID1 = ?", (g.user['ID'],)).fetchall()

    user_ids = [y for x in queries for y in x]

    db.row_factory = sqlite3.Row

    users = [db.execute('SELECT * from user WHERE id = ?', (x,)).fetchone() for x in user_ids]

    return render_template('trusted_users/view.html', users=users)

@bp.route('/remove', methods=('GET', 'POST'))
@login_required
def remove():

    if request.method == 'POST':
        db = get_db()
        error = None
        try:
            user_id = request.form['user_id']
        except BadRequestKeyError:
            error = "Nothing to remove."

        if error is None:
            db.execute('DELETE FROM TrustedUsers WHERE (UserID1 = ? AND UserID2 = ?)', (g.user['id'], user_id))
            db.commit()

            return redirect(url_for("trusted_users.view"))

        else:
            flash(error)

    db = get_db()

    db.row_factory = None

    queries = db.execute("SELECT UserID2 FROM TrustedUsers WHERE UserID1 = ?", (g.user['ID'],)).fetchall()

    user_ids = [y for x in queries for y in x]

    db.row_factory = sqlite3.Row

    users = [db.execute('SELECT * from user WHERE id = ?', (x,)).fetchone() for x in user_ids]
    return render_template('trusted_users/remove.html', users=users)

@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        db = get_db()
        error = None

        user_id = request.form['user_id']

        try:
            db.execute("INSERT INTO TrustedUsers (UserID1, UserID2) VALUES (?, ?)", (g.user['ID'], user_id))
            db.commit()
        except db.IntegrityError:
            error = "User already trusted."
        else:
            return redirect(url_for("trusted_users.view"))
        flash(error)


    db = get_db()
    query = db.execute('SELECT ID, FirstName, Surname FROM User WHERE ID != ?', (g.user['ID'],)).fetchall()

    return render_template('trusted_users/add.html', users=query)
