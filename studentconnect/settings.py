from flask import (
    Blueprint, flash, g, render_template, request
)

from .auth import login_required, load_logged_in_user
from .db import get_db

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def settings():
    if request.method == 'POST':
        error = None
        db = get_db()
        items = [(key, value) for key, value in request.form.items() 
                 if not (value == str(g.user[key]) or value ==  '')]
        try:
            for attr in ['Email', 'FirstName', 'Surname', 'YearGroup', 'Private']:
                params = [(value, g.user['ID']) for key, value in items if key == attr]
                if params:
                    db.execute(f"UPDATE User SET {attr} = ? WHERE ID = ?", *params)
            db.commit()
        except db.IntegrityError:
            error = "Email address already registered"
            flash(error)
        load_logged_in_user()

    return render_template('settings.html', user=g.user)

