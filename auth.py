import sqlite3
import hashlib
import os
from datetime import datetime
import random
import string
import binascii


class UserExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class WrongPasswordError(Exception):
    pass


class ServiceNotFoundError(Exception):
    pass


def gen_table():
    # Подключение к базе данных
    conn = sqlite3.connect('mydatabase.db')

    # Создание курсора для работы с базой данных
    cursor = conn.cursor()

    cursor.execute(
        '''CREATE TABLE if NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT,
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
    salt_hex = binascii.hexlify(salt).decode('utf-8')[:6]

    # Конвертируем пароль и соль в байты
    password_bytes = password.encode('utf-8')
    salt_bytes = binascii.unhexlify(salt_hex)

    # Хэшируем пароль и соль
    hash_result = hashlib.sha1(password_bytes + salt_bytes).hexdigest()

    # Возвращаем хэш и соль
    return hash_result, salt_hex


def add_user_to_database(email, password, user_type):
    # Подключение к базе данных
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Проверка наличия пользователя в базе данных
    cursor.execute('''SELECT * FROM users WHERE email = ?''', (email,))
    user = cursor.fetchone()
    if user:
        conn.close()
        raise UserExistsError("Пользователь с заданной почтой уже существует")

    # Хэширование пароля и генерация токена
    password, salt = hash_password(password)
    token = generate_token()

    # Вставка нового пользователя в таблицу "users"
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''INSERT INTO users(email, password, salt, token, registration_date, type)
                      VALUES(?,?,?,?,?,?)''', (email, password, salt, token, registration_date, user_type))

    # Сохранение изменений и закрытие базы данных
    conn.commit()
    conn.close()


def update_user(id, email, services):
    # Соединяемся с базой данных
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Ищем пользователя в таблице users
    c.execute("SELECT * FROM users WHERE id=?", (id,))
    user = c.fetchone()

    # Если пользователь не найден, вызываем ошибку
    if user is None:
        conn.close()
        raise UserNotFoundError('User not found')

    c.execute(
        '''UPDATE users 
        SET email=?
        WHERE id=?''', (email, id)
    )

    service_ids = []
    for service in services:
        c.execute("SELECT id FROM services WHERE name=?", (service,))
        service_id = c.fetchone()

        if service_id is None:
            raise ServiceNotFoundError('Service not found')

        service_ids.append(service_id)

    c.execute(
        f'''INSERT INTO user_services
        VALUES
            {', '.join(f"(?,{id})"),};''', service_ids
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
        raise UserNotFoundError('User not found')

    # Получаем соль, хэш и токен пользователя
    salt = user[3]
    hashed_password = user[2]
    token = user[4]

    # Хэшируем введенный пароль с использованием соли
    hashed_input_password = hash_password(password, salt)

    # Если хэшированный пароль не соответствует сохраненному, вызываем ошибку
    if hashed_input_password != hashed_password:
        conn.close()
        raise WrongPasswordError('Wrong password')

    return token


def test_correct(token):  # True если токен корректный
    # устанавливаем соединение с базой данных
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
        # 'password': result[2],
        # 'salt': result[3],
        'token': result[4],
        'registration_date': str(result[5]),
        'type': result[6]
    }

    return user_data


if __name__ == '__main__':
    if not (os.path.isfile('database.db')):
        gen_table()
