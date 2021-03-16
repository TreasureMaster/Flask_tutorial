import os
from flask import Flask, session, g
from pkg_resources import get_distribution

from .widgets.likeswidget import Likes
from .widgets.commentswidget import Comments


__version__ = get_distribution('flaskr').version

def create_app(test_config=None):
    """Фабричная функция. Создает и настраивает приложение."""

    # TERMS instance_relative_config=True - использовать относительный экземпляр приложения по умолчанию
    # сообщает приложению, что файлы конфигурации относятся к папке экземпляра
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # загрузить конфигурацию экземпляра, если она существует только, если не тестируем приложение
        # TERMS silent=True указывает, что при отсутствии файла сбой загрузки будет проигнорирован.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # загрузить тестовую конфигурацию, если она передана в приложение
        app.config.from_mapping(test_config)

    # убеждаемся, что папка экземпляра существует
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # инициализация logger
    from . import setlogger
    setlogger.init_logger(app)

    # app.logger.info(session)

    # создаем простую страницу
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # добавить функцию закрытия БД и команду инициализации БД из модуля db пакета flaskr
    from . import db
    db.init_app(app)

    # Регистрация схемы auth в приложении
    from . import auth
    app.register_blueprint(auth.bp)

    # Регистрация схемы blog в приложении
    from . import blog
    app.register_blueprint(blog.bp)
    # TERMS add_url_rule() связывает конечную точку 'index' с URL '/' в данном случае
    # Это делает одинаковым вызовы url_for('index') и url_for('blog.index')
    app.add_url_rule('/', endpoint='index')

    # Регистрация схемы post в приложении
    from . import post
    app.register_blueprint(post.bp)

    # Загрузка версии приложения
    @app.before_request
    def load_version():
        if 'version' not in session:
            session['version'] = __version__

    # Загрузка виджетов
    @app.before_request
    def load_widgets():
        g.likes = Likes(app)
        g.comments = Comments(app)
        app.logger.info(session)

    return app