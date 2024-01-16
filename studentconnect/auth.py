import functools
from secrets import token_hex

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .pwdless import (
    generate_token, send_token, verify_token, jwt
)

from .db import get_db



bp = Blueprint('auth', __name__)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['FirstName']
        surname = request.form['surname']
        year_group = request.form['YearGroup']
        private = 0
        secret = token_hex(32)
        db = get_db()
        error = None

        if not email:
            error = 'Email address is required.'

        if any(x not in email for x in ['@', '.']):
            error = 'Invalid email address.'


        if not first_name:
            error = 'First name is required.'

        if not surname:
            error = 'Surname is required.'

        if not year_group:
            error = 'Year group is required.'

        if all(x != year_group for x in ['F', '1', '2']):
            error = 'Invalid year group.'

        if error is None:
            try:
                db.execute(
                        """INSERT INTO user (email, FirstName, surname,
                                             YearGroup, private, secret)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (email, first_name, surname,
                         year_group, private, secret),
                )
                db.commit()
            except db.IntegrityError:
                error = "This email address is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/token')
def token():
    db = get_db()
    error = None
    args = request.args
    token_arg = args["token"]

    try:
        user_id = verify_token(token_arg, db)
    except jwt.exceptions.ExpiredSignatureError:
        error = 'Token has expired.'

    if user_id is None:
        error = 'Invalid token.'

    if error is None:
        session.clear()
        session['user_id'] = user_id
        return redirect(url_for('timetable.view'))

    flash(error)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email address.'

        if error is None:
            user_token = generate_token(user)
            send_token(user_token, user, url_for("auth.token"))

        if error:
            flash(error)
        else:
            flash("Please check your inbox for an email containing a login link.")

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * from user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
