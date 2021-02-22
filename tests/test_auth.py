import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    # client.get() делает запрос GET и возвращает объект Response (Flask)
    assert client.get('/auth/register').status_code == 200
    # client.post() - выполняет запрос POST, конвертируя данные словаря в данные формы
    response = client.post(
        '/auth/register',
        data={'username': 'a', 'password': 'a'}
    )
    # Представление register полсе удачной регистрации перенаправляет на представление входа
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
        ('', '', b'Username is required.'),
        ('a', '', b'Password is required.'),
        ('test', 'test', b'already registered'),
    )
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    # response.data содержит тело ответа (в байтовом виде)
    # Для сравнения в Юникоде нужно использовать get_data(as_text=True)
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
        ('a', 'test', b'Incorrect username.'),
        ('test', 'a', b'Incorrect password.'),
    )
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session