import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """Возвращает соединение с базой данных sqlite3.
    
    Если соединение отсутствует, то оно создается.
    Иначе - возвращается уже существующее.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """Закрывает существующее соединение с БД."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Создает новую базу данных."""
    db = get_db()

    # TERMS open_resource() - открывает файл, относящийся к текущему пакету приложения
    # это удобно, т.к. позже не будет известно, куда установлено само приложение.
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


# TERMS click.command определяет команду командной строки init-db
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Очищает существующие данные и создает новые таблицы."""
    init_db()
    # TERMS click.echo() - выводит сообщение в командную строку
    click.echo('Initialized the database.')


def init_app(app):
    """Выполняет регистрацию функций в приложении.

    Регистрирует функции close_db() и init_db_command() в текущем приложении.
    """
    # TERMS teardown_appcontext() сообщает Flask вызвать функцию при очистке после возврата ответа
    app.teardown_appcontext(close_db)
    # TERMS app.cli.add_command() добавляет новую команду, которую можно вызвать с помощью команды flask
    app.cli.add_command(init_db_command)