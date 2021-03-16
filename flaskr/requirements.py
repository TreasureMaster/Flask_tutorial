"""Попытка собрать декораторы требований к системе в один файл."""

import functools

from flask import flash, g, current_app

from .widgets.flashes import Flash, pflash


# ошибка существования виджета
class WidgetError(Exception):
    pass

# with_arguments декорирует другой декоратор, чтобы он мог принимать аргументы
def with_arguments(deco):
    @functools.wraps(deco)
    def wrapper(*dargs, **dkwargs):
        def decorator(func):
            result = deco(func, *dargs, **dkwargs)
            functools.update_wrapper(result, func)
            return result
        return decorator
    return wrapper

# Декоратор, который требует действие от автора виджета (лайк, комментарий и т.п.)
@with_arguments
def author_required(view, for_widget=None):
    @functools.wraps(view)
    def wrapped_view(id, *args, **kwargs):
        if for_widget and for_widget in g:
            # current_app.logger.info(for_widget)
            if not g.get(for_widget).is_author(id):
                pflash(Flash('Author required for this action.'), 'error')
        else:
            raise WidgetError("widget '%s' is not defined" % for_widget)
        return view(id, *args, **kwargs)
    return wrapped_view

# Декоратор, который запрещает автору виджета (лайк, комментарий и т.п.) выполнить действие
@with_arguments
def author_denied(view, for_widget=None):
    @functools.wraps(view)
    def wrapped_view(id, *args, **kwargs):
        if for_widget and for_widget in g:
            # current_app.logger.info(for_widget)
            # current_app.logger.info(id)
            # current_app.logger.info(g.get(for_widget))
            # current_app.logger.info(g.get(for_widget).is_author(id))
            if g.get(for_widget).is_author(id):
                pflash(Flash('Author denied for this action.'), 'error')
        else:
            raise WidgetError("widget '%s' is not defined" % for_widget)
        return view(id, *args, **kwargs)
    return wrapped_view