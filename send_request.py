import requests
import json

def send_request(data,Type='auth'):
    # конвертируем данные в формат json
    
    json_data = json.dumps(data)
    
    # устанавливаем заголовок Content-Type для отправки запроса в формате json
    headers = {'Content-Type': 'application/json'}
    # отправляем POST-запрос на локальный API сервер на порту 5000
    response = requests.post(f'http://localhost:5000/{Type}', data=json_data, headers=headers)
    
    # получаем ответ в формате json
    result = response
    # возвращаем ответ
    return result



data = {'email': 'John@gmial.co,', 'password': '25gggg', 'registr':True, 'type':'person'}

token = send_request(data,'get')

print(token)  # выведет {'result': {'name': 'John', 'age': 25}}
