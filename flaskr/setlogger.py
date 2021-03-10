# Logger setup
import logging
from logging.handlers import RotatingFileHandler

def init_logger(app):
    # if not app.debug:
    # RotatingFileHandler устанавливает лимит - сохраняются только 10 последних файлов (не более 1 Мб)
    file_handler = RotatingFileHandler('tmp/flaskr_logger.log', 'a', 1*1024*1024, 10, encoding='utf-8')
    # Formatter задает произвольный формат записей в логе
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s' # [in %(pathname)s:%(lineno)d]'
    ))
    # Установка уровня логгирования - INFO
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('-------------------------------------------------')
    app.logger.info('flaskr_logger initialized')


# def save_info(attr):
#     app.logger.info('"app.' + str(attr) + '":')
#     app.logger.info(getattr(app, attr))