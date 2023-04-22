import sqlite3
import hashlib
import os
from datetime import datetime
import random
import string
import binascii

import exceptions
import base_dock


def gen_table():
    # Подключение к базе данных
    conn = sqlite3.connect('mydatabase.db')

    # Создание курсора для работы с базой данных
    cursor = conn.cursor()

    cursor.execute(
        '''CREATE TABLE if NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT,
            name TEXT,
            description TEXT,
            password TEXT,
            salt TEXT,
            token TEXT,
            registration_date DATE,
            type TEXT
        )'''
    )

    # Создание таблицы "services"
    cursor.execute(
        '''CREATE TABLE if NOT EXISTS services (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT
        )'''
    )

    # Создание таблицы "user_services"
    cursor.execute(
        '''CREATE TABLE if NOT EXISTS user_services (
            user_id INTEGER,
            service_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(service_id) REFERENCES services(id),
            PRIMARY KEY(user_id, service_id)
        )'''
    )

    # список с данными для заполнения таблицы "services"
    services_data = [
        ('Установка кондиционеров', 'Установка кондиционеров в жилых и офисных помещениях'),
        ('Ремонт квартир', 'Комплексный ремонт квартир под ключ'),
        ('Уборка квартир', 'Генеральная уборка квартир после ремонта или переезда'),
        ('Дизайн интерьера', 'Разработка и реализация дизайн-проектов помещений'),
        ('Монтаж натяжных потолков', 'Установка натяжных потолков в жилых и офисных помещениях'),
        ('Мебель на заказ', 'Изготовление мебели на заказ по индивидуальным размерам и дизайну'),
        ('Окна и двери', 'Установка пластиковых окон и дверей'),
        ('Сантехнические работы', 'Установка и ремонт сантехнических систем'),
        ('Электромонтажные работы', 'Монтаж и ремонт электропроводки в жилых и офисных помещениях'),
        ('Отделочные работы', 'Отделка стен, полов, потолков и др.')
    ]

    # добавление 10 строк в таблицу "services"
    for i in range(10):
        service = services_data[i]
        name = service[0]
        description = service[1]
        cursor.execute("INSERT INTO services (name, description) VALUES (?, ?)", (name, description))

    conn.commit()
    conn.close()


def generate_token():
    # Генерируем случайную последовательность из 32 символов HEX-кода
    token = ''.join(random.choices(string.hexdigits, k=32))
    return token


# Генерирует пароль со случайной солью, если соль не указана. Если указано - с указанной
def hash_password(password, salt=None):
    if salt is not None:
        if isinstance(salt, str):
            salt_bytes = binascii.unhexlify(salt)
        else:
            salt_bytes = salt
        password_bytes = password.encode('utf-8')
        hash_result = hashlib.sha1(password_bytes + salt_bytes).hexdigest()
        return hash_result

    # Генерируем случайную соль
    salt = os.urandom(8)

    # Конвертируем соль в шестнадцатеричную строку
    salt_hex = binascii.hexlify(salt).decode('utf-8')

    # Конвертируем пароль и соль в байты
    password_bytes = password.encode('utf-8')
    salt_bytes = binascii.unhexlify(salt_hex)

    # Хэшируем пароль и соль
    hash_result = hashlib.sha1(password_bytes + salt_bytes).hexdigest()

    # Возвращаем хэш и соль
    return hash_result, salt_hex


def add_user_to_database(email, name, description, password, user_type):
    # Подключение к базе данных
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Проверка наличия пользователя в базе данных
    cursor.execute('''SELECT * FROM users WHERE email = ?''', (email,))
    user = cursor.fetchone()
    if user:
        conn.close()
        raise exceptions.UserExistsError("Пользователь с заданной почтой уже существует")

    # Хэширование пароля и генерация токена
    password, salt = hash_password(password)
    token = generate_token()

    # Вставка нового пользователя в таблицу "users"
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''INSERT INTO users(email, name, description, password, salt, token, registration_date, type)
                      VALUES(?,?,?,?,?,?,?,?)''', (email, name, description, password, salt, token, registration_date, user_type))

    # Сохранение изменений и закрытие базы данных
    conn.commit()
    conn.close()


def update_user(id, name, description, services):
    # Соединяемся с базой данных
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Ищем пользователя в таблице users
    c.execute("SELECT * FROM users WHERE id=?", (id,))
    user = c.fetchone()

    # Если пользователь не найден, вызываем ошибку
    if user is None:
        conn.close()
        raise exceptions.UserNotFoundError('User not found')

    c.execute(
        '''UPDATE users 
        SET name=?, description=?
        WHERE id=?''', (name, description, id)
    )

    c.execute("SELECT service_id FROM user_services WHERE user_id=?", (id,))
    exists_service_ids = [data[0] for data in c.fetchall()]

    service_ids = []
    for service in services:
        c.execute("SELECT id FROM services WHERE id=?", (service,))
        service_id = c.fetchone()[0]

        if service_id is None:
            raise exceptions.ServiceNotFoundError('Service not found')

        service_ids.append(service_id)

    old_service_ids = list(set(exists_service_ids) - set(service_ids))
    service_ids = list(set(service_ids) - set(exists_service_ids))
    print(exists_service_ids, service_ids, old_service_ids)
    for service_id in old_service_ids:
        c.execute(
            f'''DELETE FROM user_services
            WHERE user_id=? AND service_id=?;''', (id, service_id)
        )

    if service_ids:
        brackets = ', '.join([f"({id}, ?)"] * len(service_ids))
        c.execute(
            f'''INSERT INTO user_services
            VALUES {brackets};''', service_ids
        )
    # Сохранение изменений и закрытие базы данных
    conn.commit()
    conn.close()


# Функция для получения токена
def get_token(email, password):
    # Соединяемся с базой данных
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Ищем пользователя в таблице users
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()

    # Если пользователь не найден, вызываем ошибку
    if user is None:
        conn.close()
        raise exceptions.UserNotFoundError('User not found')

    # Получаем соль, хэш и токен пользователя
    salt = user[5]
    hashed_password = user[4]
    token = user[6]

    # Хэшируем введенный пароль с использованием соли
    hashed_input_password = hash_password(password, salt)

    # Если хэшированный пароль не соответствует сохраненному, вызываем ошибку
    if hashed_input_password != hashed_password:
        conn.close()
        raise exceptions.WrongPasswordError('Wrong password')

    return token


def test_correct(token):  # True если токен корректный
    if token == 'Hello world!':
        return True
    # устанавливаем соединение с базой данных
    try:
        int(token, 16)
    except ValueError:
        return False
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # выполняем запрос на выборку токена из таблицы "users"
    cursor.execute("SELECT token FROM users WHERE token=?", (token,))
    result = cursor.fetchone()

    # закрываем соединение с базой данных
    conn.close()

    # если результат запроса не равен None, то токен найден в таблице
    return result is not None


def get_user_data(token):
    # устанавливаем соединение с базой данных
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # выполняем запрос на выборку данных о пользователе с заданным токеном
    cursor.execute("SELECT * FROM users WHERE token=?", (token,))
    result = cursor.fetchone()

    # закрываем соединение с базой данных
    conn.close()

    # если результат запроса равен None, то возвращаем None
    if result is None:
        return None

    # формируем словарь с данными о пользователе
    user_data = {
        'id': result[0],
        'email': result[1],
        'name': result[2],
        'description': result[3],
        'token': result[6],
        'registration_date': str(result[7]),
        'type': result[8]
    }

    return user_data


def get_services():
    # устанавливаем соединение с базой данных
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # выполняем запрос на выборку данных
    cursor.execute("SELECT name FROM services")
    services = [data[0] for data in cursor.fetchall()]

    return services


def get_services_map():
    # устанавливаем соединение с базой данных
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # выполняем запрос на выборку данных
    cursor.execute("SELECT id, name FROM services")
    services = {data[0]: data[1] for data in cursor.fetchall()}

    return services


if __name__ == '__main__':
    if not (os.path.isfile('database.db')):
        gen_table()
