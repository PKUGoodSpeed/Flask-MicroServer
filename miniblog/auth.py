import functools
from .database import getDataBase
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

blueprint = Blueprint('auth', __name__, url_prefix='/auth')

# The first view: register
@blueprint.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        usr_db = getDataBase()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif usr_db.execute(
            "SELECT id FROM user where username = ?", (username, )
        ).fetchone() is not None:
            error = "User {} is already registered.".format(username)

        if not error:
            usr_db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password))
            )
            usr_db.commit()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')

# The second view: login
@blueprint.route("/login", methods=('GET', 'POST'))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        usr_db = getDataBase()
        error = None

        user = usr_db.execute(
            "SELECT * FROM user WHERE username = ?", (username, )
        ).fetchone()

        if not user:
            error = "Incorrect username"
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password"

        if not error:
            session.clear()
            session['user_id'] = user["id"]
            return redirect(url_for('index'))

        flash(error)
    return render_template('auth/login.html')

# handle logged in users
@blueprint.before_app_request
def loadLoggedInUser():
    user_id = session.get('user_id')

    if not user_id:
        g.user = None
    else:
        g.user = getDataBase().execute(
            "SELECT * FROM user WHERE id = ?", (user_id, )).fetchone


# Logout
@blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Authentication views
def loginRequired(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view