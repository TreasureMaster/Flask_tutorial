from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.blog import get_post
from flaskr import __version__

# Схема страницы блога INDEX
bp = Blueprint('post', __name__)

# Получает количество лайков и дизлайков для данного поста
def get_count_likes(id, check_author=True):
    likes = get_db().execute(
        'SELECT count(like) AS "like", count(dislike) AS "dislike"'
        ' FROM likes'
        ' WHERE post_id = ?',
        (id,)
    ).fetchone()

    # TERMS abort() вызывает специальное исключение, которое возвращает код состояния HTTP
    if likes is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    return likes

# Проверяет не ставит ли лайк автор
def is_author(post_id):
    user_id = get_db().execute(
        'SELECT author_id'
        ' FROM post'
        ' WHERE id = ?',
        (post_id,)
    ).fetchone()[0]

    return user_id == g.user['id']

# Определяет есть ли лайк или дизлайк от данного пользователя
def get_like(post_id, regard):
    query = (
        'SELECT *'
        ' FROM likes'
        ' WHERE post_id = ? AND %s = ?'
    ) % regard
    like = get_db().execute(
        query,
        (post_id, g.user['id'])
    ).fetchone()

    return like is not None

# Определяет оставил ли пользователь лайк(дизлайк)
def get_regards(post_id):
    return get_like(post_id, 'like') and get_like(post_id, 'dislike')

# Просмотр каждого сообщения
@bp.route('/<int:id>/view', endpoint='view')
def view_post(id):
    post = get_post(id, False)
    likes = get_count_likes(id)
    return render_template('posts/view.html', post=post, likes=likes, author=is_author(id))

# Лайки для сообщений
@bp.route('/<int:id>/like', endpoint='like')
@login_required
def set_like(id):
    error = ''
    if is_author(id):
        error = 'The author cannot like his posts.'
    elif get_regards(id):
        error = "You've already liked it."

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO likes (post_id, like)'
            ' VALUES (?, ?)',
            (id, g.user['id'])
        )
        db.commit()
    # TODO передать параметры или переделать ?
    # TODO собрать likes и author в post
    # TODO сделать декоратор-сборщик данных в post?
        return redirect(url_for('post.view', id=id))
    return render_template('posts/view.html')

@bp.route('/<int:id>/dislike', endpoint='dislike')
@login_required
def set_dislike(id):
    pass