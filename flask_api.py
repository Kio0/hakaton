import auth

from flask import Flask, request, jsonify


app = Flask(__name__)


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
                    data['email'], data['password'], data['type']
                )
            except auth.UserExistsError:
                return jsonify({'error': 'user already exists'})
            # возвращаем результат в формате json
            return jsonify({'response': 'user successfully registered'})
        # если в запросе присутствуют не все данные, возвращаем ошибку
        return jsonify({'error': 'invalid data'})
    else:
        # если запрос не имеет формат json, возвращаем ошибку
        return jsonify({'error': 'invalid request format'})


@app.route('/login', methods=['GET'])
def login_request():
    # проверяем, что запрос имеет формат json
    if request.headers['Content-Type'] == 'application/json':
        # получаем данные из запроса в формате json
        data = request.json
        # проверяем данные
        if 'email' in data and 'password' in data:
            # добавляем пользователя в базу данных
            token = auth.get_token(data['email'], data['password'])
            # возвращаем результат в формате json
            return jsonify({'token': token})
        # если в запросе присутствуют не все данные, возвращаем ошибку
        return jsonify({'error': 'invalid data'})
    else:
        # если запрос не имеет формат json, возвращаем ошибку
        return jsonify({'error': 'invalid request format'})


@app.route('/user', methods=['GET'])
def user_request():
    # проверяем, что запрос имеет формат json
    if request.headers['Content-Type'] == 'application/json':
        # получаем токен из заголовков
        token = request.headers.get('token')
        # Проверяем токен
        if not (auth.test_correct(token)):
            return jsonify({'error': 'invalid token'})
        # возвращаем результат в формате json
        return jsonify(auth.get_user_data(token))
    else:
        # если запрос не имеет формат json, возвращаем ошибку
        return jsonify({'error': 'invalid request format'})


if __name__ == '__main__':
    # запускаем сервер
    app.run(port=5000)
