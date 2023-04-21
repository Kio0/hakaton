import requests
import json


def send_request(data, route='auth'):
    # конвертируем данные в формат json
    json_data = json.dumps(data)

    # устанавливаем заголовок Content-Type для отправки запроса в формате json
    headers = {'Content-Type': 'application/json'}
    # отправляем POST-запрос на API сервер
    response = requests.post(f'http://lkjhytre.pythonanywhere.com/{route}', data=json_data, headers=headers)

    # получаем ответ в формате json
    result = response.json()
    # возвращаем ответ
    return result


user = {'email': 'John@gmial.co,', 'password': '25gggg', 'registr': False, 'type': 'person'}
token = send_request(user, 'auth')
print(token)  # выведет {'result': {'name': 'John', 'age': 25}}

user = send_request({'token': token}, 'get')
print(user)
