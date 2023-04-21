import requests
import json


def auth_user(user):
    # конвертируем данные в формат json
    json_data = json.dumps(user)

    # устанавливаем заголовок Content-Type для отправки запроса в формате json
    headers = {'Content-Type': 'application/json'}
    # отправляем POST-запрос на API сервер
    response = requests.post(f'http://lkjhytre.pythonanywhere.com/auth', data=json_data, headers=headers)
    # response = requests.post(f'http://localhost:5000/auth', data=json_data, headers=headers)

    # получаем ответ в формате json
    result = response.json()
    # возвращаем ответ
    return result


def get_token(user):
    # конвертируем данные в формат json
    json_data = json.dumps(user)

    # устанавливаем заголовок Content-Type для отправки запроса в формате json
    headers = {'Content-Type': 'application/json'}
    # отправляем POST-запрос на API сервер
    response = requests.get(f'http://lkjhytre.pythonanywhere.com/login', data=json_data, headers=headers)
    # response = requests.get(f'http://localhost:5000/login', data=json_data, headers=headers)

    # получаем ответ в формате json
    result = response.json()
    # возвращаем ответ
    return result


def get_user(token):
    # устанавливаем заголовок token
    headers = {'token': token}
    # отправляем POST-запрос на API сервер
    response = requests.get(f'http://lkjhytre.pythonanywhere.com/user', headers=headers)
    # response = requests.get(f'http://localhost:5000/user', headers=headers)

    # получаем ответ в формате json
    user = response.json()
    # возвращаем ответ
    return user


user = {'email': 'Josh123@gmial.com', 'password': '2533gggg', 'type': 'person'}
print(auth_user(user))

user.pop('type')
response = get_token(user)
print(response)
token = response.get('token')

user = get_user(token)
print(user)
