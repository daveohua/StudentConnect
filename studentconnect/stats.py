from flask import (
    Blueprint, render_template
)

from .db import get_db

bp = Blueprint('stats', __name__, url_prefix='/stats')

@bp.route('/')
def view():
    db = get_db()

    params = {
    'total_users' : db.execute("SELECT COUNT(*) UserCount FROM User").fetchone(),

    'modal_subjects' : db.execute("""SELECT * 
                                     FROM Subject
                                     WHERE ID = 
                                          (SELECT SubjectID
                                           FROM (SELECT SubjectID,
                                                        COUNT(UserID) UserCount 
                                                 FROM Enrolment 
                                                 GROUP BY SubjectID) 
                                           WHERE UserCount = 
                                                (SELECT MAX(UserCount) 
                                                 FROM (SELECT SubjectID, 
                                                              COUNT(UserID) UserCount 
                                                       FROM Enrolment 
                                                       GROUP BY SubjectID)))""").fetchall(),

    'modal_trusted_users' :  db.execute("""SELECT * 
                                           FROM User 
                                           WHERE ID = 
                                                (SELECT UserID 
                                                 FROM (SELECT UserID2 UserID, 
                                                              COUNT(UserID2) UserCount 
                                                       FROM TrustedUsers 
                                                       GROUP BY UserID2) 
                                                 WHERE UserCount = 
                                                      (SELECT MAX(UserCount) 
                                                       FROM (SELECT UserID2 UserID, 
                                                             COUNT(UserID2) UserCount 
                                                             FROM TrustedUsers 
                                                             GROUP BY UserID2)))""").fetchall(),

    'total_d_users' : db.execute("""SELECT COUNT(*) UserCount 
                                    FROM User 
                                    WHERE FirstName 
                                          LIKE 'D%'""").fetchone()
    }

    return render_template('stats.html', **params)
