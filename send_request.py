import requests
import json
import os
import base64


def auth_user(user):
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


def get_token(user):
    # отправляем POST-запрос на API сервер
    response = requests.get(f'http://lkjhytre.pythonanywhere.com/login', params=user)

    # получаем ответ в формате json
    result = response.json()
    # возвращаем ответ
    return result


def get_user(token):
    # устанавливаем заголовок token
    headers = {'token': token}
    # отправляем POST-запрос на API сервер
    response = requests.get(f'http://lkjhytre.pythonanywhere.com/user', headers=headers)

    # получаем ответ в формате json
    user = response.json()
    # возвращаем ответ
    return user


def send_document_api(filename, token, recipient_id=-1, sender_id=-1):
    # Проверяем, что файл существует
    if not os.path.isfile(filename):
        print(f'Ошибка: файл {filename} не найден.')
        return
    
    # Считываем файл в виде байтов и кодируем его содержимое в строку base64
    with open(filename, 'rb') as f:
        file_data = f.read()
    file_data_base64 = base64.b64encode(file_data).decode('utf-8')
    
    # Формируем json-переменную с данными для отправки
    data = {
        'filename': filename,
        'recipient_id': recipient_id,
        'sender_id': sender_id,
        'base64': file_data_base64
    }
    
    # Формируем заголовок с токеном
    headers = {'token': token,'Content-Type': 'application/json'}
    
    # Отправляем запрос POST с данными и заголовком
    response = requests.post('http://lkjhytre.pythonanywhere.com/dock', json=data, headers=headers)
    
    # Возвращаем статус-код ответа
    return response.json()


user = {'email': 'Josh123@gmial.com', 'password': '2533gggg', 'type': 'person'}
print(auth_user(user))

user.pop('type')
response = get_token(user)
print(response)
token = response.get('token')

user = get_user(token)
print(user)

dock = send_document_api('11331.xlsx', token)
print(dock)
