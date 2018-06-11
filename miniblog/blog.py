from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session)
from werkzeug.exceptions import abort
from .auth import loginRequired
from .database import getDataBase

blueprint = Blueprint('blog', __name__)

@blueprint.route("/")
def index():
    database = getDataBase()
    posts = database.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC').fetchall()
    return render_template('blog/index.html', posts=posts)


@blueprint.route('/create', methods=('GET', 'POST'))
@loginRequired
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            database = getDataBase()
            database.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            database.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def getPost(id, check_author=True):
    post = getDataBase().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@blueprint.route('/<int:id>/update', methods=('GET', 'POST'))
@loginRequired
def update(id):
    post = getPost(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            database = getDataBase()
            database.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            database.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@blueprint.route('/<int:id>/delete', methods=('POST',))
@loginRequired
def delete(id):
    getPost(id)
    database = getDataBase()
    database.execute('DELETE FROM post WHERE id = ?', (id,))
    database.commit()
    return redirect(url_for('blog.index'))