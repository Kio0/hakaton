import requests
import json


def send_user(user):
    # конвертируем данные в формат json
    json_data = json.dumps(user)

    # устанавливаем заголовок Content-Type для отправки запроса в формате json
    headers = {'Content-Type': 'application/json'}
    # отправляем POST-запрос на API сервер
    response = requests.post(f'http://lkjhytre.pythonanywhere.com/auth', data=json_data, headers=headers)

    # получаем ответ в формате json
    result = response.json()
    # возвращаем ответ
    return result


def send_token(token):
    # устанавливаем заголовок Content-Type для отправки запроса в формате json
    # и токен
    headers = {'Content-Type': 'application/json', 'token': token}
    # отправляем POST-запрос на API сервер
    response = requests.get(f'http://lkjhytre.pythonanywhere.com/user', headers=headers)

    # получаем ответ в формате json
    result = response.json()
    # возвращаем ответ
    return result


user = {'email': 'John@gmial.co,', 'password': '25gggg', 'registr': False, 'type': 'person'}
token = send_user(user)
print(token)

user = send_token(token)
print(user)
