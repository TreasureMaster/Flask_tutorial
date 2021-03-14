from os import error
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, session
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
    comments = get_comments(id)
    return render_template(
        'posts/view.html',
        post=post,
        comments=comments,
        # likes_widget=g.likes(id)
    )

# Тестовый декоратор, который требует автора
import functools
def author_required(view):
    @functools.wraps(view)
    def wrapped_view(id, *args, **kwargs):
        if not g.likes.is_author(id):
            # return redirect(url_for('auth.login'))
            # TODO либо добавить в error, но как возвращать?
            # либо проверять внутри декорируемой функции стек flash (как?)
            # flash('The author cannot like his posts.')
            pass

        return view(id, *args, **kwargs)

    return wrapped_view

# Лайки для сообщений
@bp.route('/<int:id>/regard/<string:regard>', endpoint='like')
@login_required
@author_required
def set_regard(id, regard):
    current_app.logger.info(session.get('_flashes'))
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
    return render_template(
        'posts/view.html',
        post=get_post(id),
        # likes_widget=g.likes(id),
        comments=get_comments(id)
    )

# Комментарии для сообщений
@bp.route('/<int:id>/comment', endpoint='comment', methods=['POST',])
@login_required
def write_comment(id):
    error = None
    # comments = get_comments(id)
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

# Получает количество лайков и дизлайков для данного поста
# def get_count_likes(id, check_author=True):
#     likes = get_db().execute(
#         'SELECT count(like) AS "like", count(dislike) AS "dislike"'
#         ' FROM likes'
#         ' WHERE post_id = ?',
#         (id,)
#     ).fetchone()

#     if likes is None:
#         abort(404, "Post id {0} doesn't exist.".format(id))

#     # if check_author and post['author_id'] != g.user['id']:
#     #     abort(403)

#     return likes

# Проверяет является ли текущий юзер автором данного поста
def is_author(post_id):
    user_id = get_db().execute(
        'SELECT author_id'
        ' FROM post'
        ' WHERE id = ?',
        (post_id,)
    ).fetchone()[0]
    return g.user is not None and user_id == g.user['id']

# Определяет оставлял ли текущий пользователь какой-либо лайк в данном посте
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