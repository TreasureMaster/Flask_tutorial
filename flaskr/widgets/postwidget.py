"""Виджет для отдельного вида поста."""

from flask import g
from .widget import Widget
from db import get_db

class PostWidget(Widget):

    # Проверяет является ли текущий юзер автором данного поста
    def is_author(self, post_id):
        user_id = get_db().execute(
            'SELECT author_id'
            ' FROM post'
            ' WHERE id = ?',
            (post_id,)
        ).fetchone()[0]
        return g.user is not None and user_id == g.user['id']