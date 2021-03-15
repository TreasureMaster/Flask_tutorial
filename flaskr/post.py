from os import error
from flask import (
    Blueprint, flash, g, render_template, request
)
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.blog import get_post as get_post_super
from flaskr import __version__

from flaskr.requirements import author_denied
from .widgets.flashes import is_category, pflash


# Схема страницы блога INDEX
bp = Blueprint('post', __name__)

# Просмотр каждого сообщения
@bp.route('/<int:id>/view', endpoint='view')
def view_post(id):
    post = get_post(id)
    comments = get_comments(id)
    return render_template(
        'posts/view.html',
        post=post,
        comments=comments
    )

# Лайки для сообщений
@bp.route('/<int:id>/regard/<string:regard>', endpoint='like')
@login_required
@author_denied(for_widget='likes')
def set_regard(id, regard):
    if g.likes.is_regard_set(id):
        pflash("You've already liked it.", 'error')

    if not is_category('error'):
        db = get_db()
        db.execute(
            'INSERT INTO likes (post_id, %s)'
            ' VALUES (?, ?)' % regard,
            (id, g.user['id'])
        )
        db.commit()

    return render_template(
        'posts/view.html',
        post=get_post(id),
        comments=get_comments(id)
    )

# Комментарии для сообщений
@bp.route('/<int:id>/comment', endpoint='comment', methods=['POST',])
@login_required
def write_comment(id):
    error = None
    if request.method == 'POST':
        comment = request.form['comment']

        if not comment:
            error = 'Comment text required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comments (post_id, user_id, comment)'
                ' VALUES (?, ?, ?)',
                (id, g.user['id'], comment)
            )
            db.commit()
    return render_template('posts/view.html', post=get_post(id), comments=get_comments(id))

# Редактирование комментария
@bp.route('/<int:id>/<int:post>/update_comment', endpoint='update')
@login_required
def update_comment(id, post):
    # id - номер комментария
    # post - номер (идентификатор) поста
    error = 'Comment Update Not Implemented Yet.'
    flash(error)
    return render_template('posts/view.html', post=get_post(post), comments=get_comments(post))


# -------------------------- Вспомогательные функции ------------------------- #

# Переопределяет get_post из flaskr.blog, добавляя новые значения
def get_post(post_id):
    # post = dict(get_post_super(post_id, False))
    post = get_post_super(post_id, False)
    # post.update(get_count_likes(post_id))
    # post['is_author'] = is_author(post_id)
    # current_app.logger.info(post)
    return post

# Получает комментарии для данного поста
def get_comments(post_id):
    comments = get_db().execute(
        'SELECT c.id, p.id AS "post", comment, c.created, c.user_id, username'
        ' FROM post p JOIN comments c ON p.id = c.post_id'
        ' JOIN user u ON c.user_id = u.id'
        ' WHERE p.id = ?'
        ' ORDER BY c.created DESC',
        (post_id,)
    ).fetchall()
    # for comment in comments:
    #     current_app.logger.info(dict(comment))
    return comments or []