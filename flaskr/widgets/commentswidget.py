"""Выделение работы с лайками в отдельный виджет Likes."""

from flask import g
from werkzeug.exceptions import abort
from db import get_db
from.postwidget import PostWidget

class Comments(PostWidget):

    # Получает количество лайков и дизлайков для данного поста
    # def get_count_likes(self, post_id, check_author=True):
    #     likes = get_db().execute(
    #         'SELECT count(like) AS "like", count(dislike) AS "dislike"'
    #         ' FROM likes'
    #         ' WHERE post_id = ?',
    #         (post_id,)
    #     ).fetchone()

    #     if likes is None:
    #         abort(404, "Post id {0} doesn't exist.".format(id))

    #     # if check_author and post['author_id'] != g.user['id']:
    #     #     abort(403)

    #     return likes

    # Определяет оставлял ли текущий пользователь какой-либо лайк в данном посте
    # def is_regard_set(self, post_id):
    #     regard = get_db().execute(
    #         'SELECT *'
    #         ' FROM likes'
    #         ' WHERE post_id = ?'
    #         ' AND (like = ? OR dislike = ?)',
    #         (post_id, g.user['id'], g.user['id'])
    #     ).fetchone()

    #     return regard is not None

    # Получает комментарии для данного поста
    def get_comments(self, post_id):
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

    # Делает виджет вызываемым (дает возможность принимать значения)
    def __call__(self, post_id):
        self.post_id = post_id
        return self

    # Вывод подготовленного HTML кода
    def __html__(self):
        content = self.app.jinja_env.get_template('posts/comments.html')
        output = content.render(
            comments  = self.get_comments(self.post_id),
            # author  = self.is_author(self.post_id),
            post_id = self.post_id
        )
        return output