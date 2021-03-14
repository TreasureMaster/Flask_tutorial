"""Базовый класс Widget для всех виджетов."""

class Widget:

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # Должен работать как синглтон ?
        if self.app is None:
            self.app = app