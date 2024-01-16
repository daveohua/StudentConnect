from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import BadRequestKeyError
from .auth import login_required
from .db import get_db

blocks = {
'A': (
   ((("Monday",1),("Monday",2)),(("Tuesday",3),("Tuesday",4)),(("Wednesday",5),))
),
'B': (
    ((("Tuesday",1),("Tuesday",2)),(("Wednesday",3),),(("Thursday",5),("Thursday",6)))
),
'C': (
    ((("Wednesday",2),),(("Thursday",3),("Thursday",4)),(("Friday",5),("Friday",6)))
),
'D': (
    ((("Monday",5),("Monday",6)),(("Thursday",1),("Thursday",2)),(("Friday",3),("Friday",4)))
),
'E': (
    ((("Monday",3),("Monday",4)),(("Tuesday",5),("Tuesday",6)),(("Friday",1),("Friday",2)))
),
'G': ((),)
}

def validate_lesson(lesson=None, block=None):
    if block is None:
        return True
    if lesson is None:
        return True
    return any(lesson in day for day in blocks[block])


class Timetable:
    """A class facilitating the easy creation, modification,
     storing, retrieving and formatting of timetables."""

    def __init__(self, user, db):
        self.table = {
            "Monday":[""]*6,
            "Tuesday":[""]*6,
            "Wednesday":["Academic Mentoring", "", "", "Enhancement", "", ""],
            "Thursday":[""]*6,
            "Friday":[""]*6
        }
        self.num_table = {
            "Monday":[0]*6,
            "Tuesday":[0]*6,
            "Wednesday":[1, 0, 0, 1, 0, 0],
            "Thursday":[0]*6,
            "Friday":[0]*6
        }
        self.dict = []

        query = db.execute("""SELECT Subject.Name, 
                                     Enrolment.Block,
                                     SingleLesson.Day, 
                                     SingleLesson.Period
                              FROM Enrolment
                              INNER JOIN Subject ON Subject.ID = Enrolment.SubjectID 
                              LEFT JOIN SingleLesson ON SingleLesson.EnrolmentID = Enrolment.ID
                              WHERE Enrolment.UserID = ?""", (user['ID'],)).fetchall()

        for record in query:
            class_ = {
                'subject': record['Name'],
                'block': record['Block'],
                'single_lesson': (record['Day'], record['Period'])
            }

            for day in blocks[record['Block']]:
                if (record['Day'], record['Period']) in day or record['Block'] == 'G':
                    self.table[record['Day']][record['Period'] - 1] = record['Name']
                    continue
                for lesson_day, lesson_period in day:
                    self.table[lesson_day][lesson_period - 1] = record['Name']

            for day in blocks[record['Block']]:
                if (record['Day'], record['Period']) in day or record['Block'] == 'G':
                    self.num_table[record['Day']][record['Period'] - 1] = 1
                    continue
                for lesson_day, lesson_period in day:
                    self.num_table[lesson_day][lesson_period - 1] = 1

            self.dict.append(class_)


def compare_timetable(*args):
    tables = [arg.num_table for arg in args]
    table = {}
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        table[day] = [(1 - (z / len(tables))) * 50 
                       for z in [sum(x) 
                                 for x in zip(*[y[day] 
                                                for y in tables])]]
    return table

bp = Blueprint('timetable', __name__, url_prefix='/timetable')

@bp.route('/view')
@login_required
def view():
    db = get_db()
    timetable = Timetable(g.user, db)
    return render_template('timetable/view.html', timetable=timetable.table)

@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST': 
        db = get_db() 
        error = None 
        subject_id = request.form['subject_id']

        if subject_id == '1':
            block = 'G'
        else:
            block = request.form['block'] 

        if block in ['D','E','G']: 
            single_lesson_day = request.form['single_lesson_day']
            single_lesson_period = request.form['single_lesson_period']
            single_lesson = (single_lesson_day, single_lesson_period)
        else:
            single_lesson_day = single_lesson_period = single_lesson = None 

        subject = db.execute(
            'SELECT * FROM Subject WHERE ID = ?', (subject_id,)
        ).fetchone()
        if subject is None: 
            error = "Invalid subject."

        if block not in ["A","B","C","D","E","G"]: 
            error = "Invalid lesson block."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO Enrolment (UserID, SubjectID, Block) VALUES (?, ?, ?)",
                    (g.user['id'], subject_id, block)
                )
                db.commit()

                if block in ['D','E','G']: 
                    enrolment_id = db.execute(
                        "SELECT ID FROM Enrolment WHERE UserID = ? AND SubjectID = ?",
                        (g.user['id'], subject_id)
                    ).fetchone()
                    db.execute(
                        "INSERT INTO SingleLesson (EnrolmentID, Day, Period) VALUES (?, ?, ?)",
                        (enrolment_id['ID'],
                         request.form['single_lesson_day'], 
                         request.form['single_lesson_period'])
                    )
                db.commit()
            except db.IntegrityError:
                error = "This class has already been added."

            else:
                return redirect(url_for("timetable.view"))

        flash(error)

    db = get_db()
    subjects = db.execute("SELECT * FROM subject").fetchall()
    return render_template('timetable/add.html', subjects=subjects)


@bp.route('/remove', methods=('GET', 'POST'))
@login_required
def remove():
    if request.method == 'POST':
        db = get_db()
        error = None
        try:
            enrolment_id = request.form['enrolment_id']
        except BadRequestKeyError:
            error = "Nothing to remove."

        if error is None:
            db.execute('DELETE FROM enrolment WHERE ID = ?', (enrolment_id,))
            db.commit()
            return redirect(url_for("timetable.view"))

        else:
            flash(error)

    db = get_db()
    query = db.execute('''SELECT Enrolment.ID, 
                                 Subject.Qualification, 
                                 Subject.Name 
                          FROM Enrolment 
                          INNER JOIN Subject 
                          ON Enrolment.SubjectID = Subject.ID 
                          WHERE Enrolment.UserID = ?''',(g.user['ID'],)).fetchall()
    return render_template('timetable/remove.html', query=query)

@bp.route('/compare', methods=('GET', 'POST'))
@login_required
def compare():
    if request.method == 'POST':
        errors = []
        db = get_db()
        user_ids = request.form['users']

        users = [db.execute('SELECT * from user WHERE id = ?', x).fetchone() 
                 for x in user_ids]

        def in_trusted_users(user):
            query = db.execute('''SELECT * 
                                  FROM TrustedUsers 
                                  WHERE UserID1 = ? AND UserID2 = ?''',
                               (user['ID'], g.user['ID'])).fetchone()
            return bool(query)

        def authorised(user):
            if user['Private'] == 0:
                return True
            if user['Private'] == 1:
                return False
            if user['Private'] == 2:
                return in_trusted_users(user)

        if any([not authorised(user) for user in users]):
            errors = errors + [f"You are not trusted by {user['FirstName']} {user['Surname']}."
                                 for user in users if not authorised(user)]

        if errors is False:
            users.append(g.user)
            user_timetables = [Timetable(user, db) for user in users]
            compared_table = compare_timetable(*user_timetables)
            return render_template('timetable/compare_result.html', timetable=compared_table)
        else:
            for error in errors:
                flash(error)



    db = get_db()
    query = db.execute('''SELECT ID,
                                 FirstName, 
                                 Surname 
                          FROM User 
                          WHERE ID != ?''', (g.user['ID'],)).fetchall()
    return render_template('timetable/compare.html', query=query)



