from flask import Flask, request, jsonify
import auth

app = Flask(__name__)


def func_set_request(data):
    token = data.get('token')

    if not (auth.test_correct(token)):
        return 'Токен некорректный'


def func_auth_request(data):
    if data.get('token') is None:
        if (data.get('email') is not None) and (data.get('password') is not None):
            if data.get('registr'):
                if data.get('type') is not None:
                    return auth.add_user_to_database(data.get('email'), data.get('password'), data.get('type'))
                else:
                    return auth.add_user_to_database(data.get('email'), data.get('password'))
            else:
                return auth.auth_user(data.get('email'), data.get('password'))
    else:
        token = data.get('token')
        if auth.test_correct(token):
            return 'Токен корректный'
        else:
            return 'Токен некорректный'
    return {'result': data}


@app.route('/auth', methods=['POST'])
def auth_request():
    # проверяем, что запрос имеет формат json
    if request.headers['Content-Type'] == 'application/json':
        # получаем данные из запроса в формате json
        data = request.json
        # выполняем функцию get_request и получаем результат
        result = func_auth_request(data)
        # возвращаем результат в формате json
        return jsonify(result)
    else:
        # если запрос не имеет формат json, возвращаем ошибку
        return jsonify({'error': 'invalid request format'})


@app.route('/user', methods=['GET'])
def get_request():
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


@app.route('/set', methods=['POST'])
def set_request():
    # проверяем, что запрос имеет формат json
    if request.headers['Content-Type'] == 'application/json':
        # получаем данные из запроса в формате json
        data = request.json
        # выполняем функцию get_request и получаем результат
        result = func_set_request(data)
        # возвращаем результат в формате json
        print(result)
        return jsonify(result)
    else:
        # если запрос не имеет формат json, возвращаем ошибку
        return jsonify({'error': 'invalid request format'})


if __name__ == '__main__':
    # запускаем сервер
    app.run()

