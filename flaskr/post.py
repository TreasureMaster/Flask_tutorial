from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.blog import get_post as get_post_super
from flaskr import __version__

# Схема страницы блога INDEX
bp = Blueprint('post', __name__)

# Просмотр каждого сообщения
@bp.route('/<int:id>/view', endpoint='view')
def view_post(id):
    post = get_post(id)
    return render_template('posts/view.html', post=post)

# Лайки для сообщений
@bp.route('/<int:id>/regard/<string:regard>', endpoint='like')
@login_required
def set_regard(id, regard):
    error = None
    if is_author(id):
        error = 'The author cannot like his posts.'
    elif is_regard_set(id):
        error = "You've already liked it."

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO likes (post_id, %s)'
            ' VALUES (?, ?)' % regard,
            (id, g.user['id'])
        )
        db.commit()
    return render_template('posts/view.html', post=get_post(id))

@bp.route('/<int:id>/dislike', endpoint='dislike')
@login_required
def set_dislike(id):
    pass

# -------------------------- Вспомогательные функции ------------------------- #

# Получает количество лайков и дизлайков для данного поста
def get_count_likes(id, check_author=True):
    likes = get_db().execute(
        'SELECT count(like) AS "like", count(dislike) AS "dislike"'
        ' FROM likes'
        ' WHERE post_id = ?',
        (id,)
    ).fetchone()

    if likes is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    return likes

# Проверяет является ли текущий юзер автором данного поста
def is_author(post_id):
    user_id = get_db().execute(
        'SELECT author_id'
        ' FROM post'
        ' WHERE id = ?',
        (post_id,)
    ).fetchone()[0]
    return g.user is not None and user_id == g.user['id']

# Определяет оставлял ли текущий пользователь какой-либо отзыв в данном посте
def is_regard_set(post_id):
    regard = get_db().execute(
        'SELECT *'
        ' FROM likes'
        ' WHERE post_id = ?'
        ' AND (like = ? OR dislike = ?)',
        (post_id, g.user['id'], g.user['id'])
    ).fetchone()

    return regard is not None

# Переопределяет get_post из flaskr.blog, добавляя новые значения
def get_post(post_id):
    post = dict(get_post_super(post_id, False))
    post.update(get_count_likes(post_id))
    post['is_author'] = is_author(post_id)
    # current_app.logger.info(post)
    return post