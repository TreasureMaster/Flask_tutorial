"""Класс сообщения."""

from flask import session, current_app, flash
from markupsafe import Markup

from .widget import Widget

class Flash(Widget):
    # CATEGORY = 0
    # MESSAGE = 1

    def __init__(self, message, category='message'):
        self.message = Markup(message)
        self.category = category
        # current_app.logger.info(session['_flashes'])
        # current_app.logger.info(len(session['_flashes']))
        # self._id = len(session['_flashes'])

    # Вывод подготовленного HTML кода
    def __html__(self):
        # current_app.logger.info(session.get('_flashes'))#.pop(self._id))
        content = current_app.jinja_env.get_template('posts/flash.html')
        output = content.render(
            message  = self.message,
            category = self.category.title()
        )
        return output


def pflash(message, category):
    """Заменяет функция flask.flash() для более красивого вывода."""
    flash(Flash(message, category), category)


def is_category(category=None):
    """
    Проверяет есть ли указанная категория в списке flash.
    Если категория равна None, то подразумевается есть ли хоть какое-нибудь сообщение в списке flash.
    """
    flashes = session.get('_flashes')
    if flashes and category:
        return category in [c for c, m in flashes]
    elif flashes and category is None:
        return len(flashes) != 0
    else:
        False