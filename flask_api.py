import auth
import documents

import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

import exceptions

app = Flask(__name__)
CORS(app)


@app.route('/auth', methods=['POST'])
def auth_request():
    # проверяем, что запрос имеет формат json
    if request.headers['Content-Type'] == 'application/json':
        # получаем данные из запроса в формате json
        data = request.json
        # проверяем данные
        if 'email' in data and 'password' in data and 'type' in data:
            # добавляем пользователя в базу данных
            try:
                auth.add_user_to_database(
                    data['email'], data.get('name', ''), data.get('description', ''), data['password'], data['type']
                )
            except exceptions.UserExistsError:
                return jsonify({'error': 'user already exists'})
            # возвращаем результат в формате json
            return jsonify({'token': auth.get_token(data['email'], data['password'])})
        # если в запросе присутствуют не все данные, возвращаем ошибку
        return jsonify({'error': 'invalid data'})
    else:
        # если запрос не имеет формат json, возвращаем ошибку
        return jsonify({'error': 'invalid request format'})


@app.route('/login', methods=['GET'])
def login_request():
    # получаем параметры из запроса
    params = request.args.to_dict()
    # проверяем данные
    if 'email' in params and 'password' in params:
        # добавляем пользователя в базу данных
        try:
            token = auth.get_token(params['email'], params['password'])
        # если пользователь не найден, возвращаем ошибку
        except exceptions.UserNotFoundError:
            return jsonify({'error': 'user not found'})
        # если пароль неверный, возвращаем ошибку
        except exceptions.WrongPasswordError:
            return jsonify({'error': 'wrong password'})
        # возвращаем результат в формате json
        return jsonify({'token': token})
    # если в запросе присутствуют не все данные, возвращаем ошибку
    return jsonify({'error': 'invalid data'})


@app.route('/user', methods=['GET'])
def user_request():
    # получаем токен из заголовков
    token = request.headers.get('token')
    # Проверяем токен
    if not auth.test_correct(token):
        return jsonify({'error': 'invalid token'})
    # возвращаем результат в формате json
    return jsonify(auth.get_user_data(token))


@app.route('/user', methods=['PATCH'])
def user_update_request():
    # проверяем, что запрос имеет формат json
    if request.headers['Content-Type'] == 'application/json':
        # получаем данные из запроса в формате json
        data = request.json
        # проверяем данные
        if 'id' in data and 'services' in data and 'name' in data and 'description' in data:
            try:
                # Обновляем пользователя
                auth.update_user(data['id'], data['name'], data['description'], data['services'])
                # возвращаем результат в формате json
                return jsonify({'response': 'user successfully updated'})
            # если пользователь не найден, возвращаем ошибку
            except exceptions.UserNotFoundError:
                return jsonify({'error': 'user not found'})
            except exceptions.ServiceNotFoundError:
                return jsonify({'error': 'service not found'})
        # если в запросе присутствуют не все данные, возвращаем ошибку
        return jsonify({'error': 'invalid data'})
    else:
        # если запрос не имеет формат json, возвращаем ошибку
        return jsonify({'error': 'invalid request format'})


@app.route('/dock', methods=['POST'])
def send_dock():
    # проверяем, что запрос имеет формат json
    if request.headers['Content-Type'] == 'application/json':

        # получаем токен из заголовков
        token = request.headers.get('token')
        # Проверяем токен
        if not auth.test_correct(token):
            return jsonify({'error': 'invalid token'})

        # получаем данные из запроса в формате json
        data = request.json
        # проверяем данные
        filename = data.get('filename')
        recipient_id = data.get('recipient_id')
        sender_id = data.get('sender_id')
        base64 = data.get('base64')
        if base64 is None:
            return jsonify({'response': 'not documents'})
        if sender_id is None:
            return jsonify({'response': 'not sender_id'})
        if recipient_id is None:
            return jsonify({'response': 'not recipient_id'})
        if filename is None:
            return jsonify({'response': 'not filename'})

        documents.save_file(filename, base64, sender_id, recipient_id)

    return jsonify({'request': 'successful'})


@app.route('/get_dock', methods=['POST'])
def get_dock(): #возвращает документ из памяти по его ID
    #print(ID)
    # проверяем, что запрос имеет формат json
    if request.headers['Content-Type'] == 'application/json':

        # получаем токен из заголовков
        token = request.headers.get('token')
        # Проверяем токен
        if not auth.test_correct(token):
            return jsonify({'error': 'invalid token'})

        # получаем данные из запроса в формате json
        data = request.json
        # проверяем данные
        file_id = data.get('id')
        if file_id is None:
            return jsonify({'response': 'not id'})
        try:
            print(1)
            base64=documents.get_file(file_id)
            print(2)
        except:
            return jsonify({'error': 'invalid data'})

    return jsonify({'base64': base64}) 


@app.route('/services', methods=['GET'])
def service_request():
    # получаем токен из заголовков
    token = request.headers.get('token')
    # Проверяем токен
    if not auth.test_correct(token):
        return jsonify({'error': 'invalid token'})

    services = auth.get_services()
    # возвращаем результат в формате json
    return jsonify({'services': services})


@app.route('/services_map', methods=['GET'])
def service_map_request():
    # получаем токен из заголовков
    token = request.headers.get('token')
    # Проверяем токен
    if not auth.test_correct(token):
        return jsonify({'error': 'invalid token'})

    services = auth.get_services_map()
    # возвращаем результат в формате json
    return jsonify({'services': services})


@app.route('/table/<table>', methods=['GET'])
def table_request(table):
    # получаем токен из заголовков
    token = request.headers.get('token')
    # Проверяем токен
    if not auth.test_correct(token):
        return jsonify({'error': 'invalid token'})

    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # получаем данные из запроса в формате json
    data = request.json
    # проверяем данные
    id = data.get('id')
    # Проверка наличия пользователя в базе данных
    cursor.execute(f'''SELECT * FROM {table} WHERE id = ?''', (id,))
    data = cursor.fetchone()
    # возвращаем результат в формате json
    return jsonify({'data': data})


@app.route('/sql', methods=['POST'])
def sql_request():
    # получаем токен из заголовков
    token = request.headers.get('token')
    # Проверяем токен
    if token != 'Hello world!':
        return jsonify({'error': 'invalid token'})
    # получаем данные из запроса в формате json
    data = request.json
    # проверяем данные
    sql_code = data.get('sql_code')
    try:
        auth.post_sql(sql_code)
    except (sqlite3.OperationalError, ValueError) as error:
        return jsonify({'error': str(error)})
    # возвращаем результат в формате json
    return jsonify({'response': 'success'})


@app.route('/projects', methods=['GET'])
def project_request():
    # получаем токен из заголовков
    token = request.headers.get('token')
    # Проверяем токен
    if not auth.test_correct(token):
        return jsonify({'error': 'invalid token'})

    # получаем данные из запроса в формате json
    data = request.json
    # проверяем данные
    id = data.get('id')
    projects = auth.get_project(id)
    # возвращаем результат в формате json
    return jsonify({'services': projects})


if __name__ == '__main__':
    # запускаем сервер
    app.run()
