import sqlite3


conn = sqlite3.connect('mydatabase.db')


import random
import sqlite3

def create_database():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Создание таблицы state_contract
    c.execute('''CREATE TABLE state_contract (
                id INTEGER PRIMARY KEY,
                title TEXT,
                date DATE,
                title_place_id INTEGER REFERENCES place(id) ,
                contract_number INTEGER REFERENCES contract_number(id),
                bank_details_id INTEGER REFERENCES bank_details(id),
                description TEXT,
                customer TEXT,
                contructor TEXT,
                signature TEXT,
                address TEXT,
                contacts TEXT,
                firstname TEXT,
                lastname TEXT,
                patronymic TEXT,
                empployee_id INTEGER REFERENCES employee(id),
                object_title TEXT,
                stamp TEXT)''')

    # Создание таблицы place
    c.execute('''CREATE TABLE place (
                id INTEGER PRIMARY KEY,
                address TEXT)''')

    # Создание таблицы bank_details
    c.execute('''CREATE TABLE bank_details (
                id INTEGER PRIMARY KEY,
                title TEXT,
                bik TEXT)''')

    # Создание таблицы employee
    c.execute('''CREATE TABLE employee (
                id INTEGER PRIMARY KEY,
                lastname TEXT,
                firstname TEXT,
                position_id INTEGER)''')

    # Создание таблицы contract_number
    c.execute('''CREATE TABLE contract_number (
                id INTEGER PRIMARY KEY,
                legal_department_id INTEGER)''')

    conn.commit()
    conn.close()




def populate_database():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Заполнение таблицы place
    places = [('Москва, ул. Ленина, 10',),
              ('Санкт-Петербург, Невский пр., 20',),
              ('Казань, ул. Кремлевская, 5',),
              ('Екатеринбург, ул. Ленина, 1',)]
    c.executemany('INSERT INTO place (address) VALUES (?)', places)

    # Заполнение таблицы bank_details
    bank_details = [('Сбербанк', '044525225'),
                    ('Альфа-банк', '044525593'),
                    ('ВТБ', '044525400'),
                    ('Газпромбанк', '044525333')]
    c.executemany('INSERT INTO bank_details (title, bik) VALUES (?, ?)', bank_details)

    # Заполнение таблицы employee
    employees = [('Иванов', 'Иван', 1),
                 ('Петров', 'Петр', 2),
                 ('Сидоров', 'Сидор', 3),
                 ('Кузнецов', 'Алексей', 4)]
    c.executemany('INSERT INTO employee (lastname, firstname, position_id) VALUES (?, ?, ?)', employees)

    # Заполнение таблицы contract_number
    contract_numbers = [(10001, 1),
                        (10002, 2),
                        (10003, 3),
                        (10004, 4)]
    #c.executemany('INSERT INTO contract_number (id, legal_department_id) VALUES (?, ?)', contract_numbers)

    # Заполнение таблицы state_contract
    for i in range(1, 101):
        contract = (i, 'Договор ' + str(i), '2023-04-22', random.randint(1, 4), random.randint(10001, 10004), random.randint(1, 4), 'Описание договора ' + str(i), 'Заказчик ' + str(i), 'Исполнитель ' + str(i), 'Подпись ' + str(i), 'Адрес ' + str(i), 'Контакты ' + str(i), 'Имя ' + str(i), 'Фамилия ' + str(i), 'Отчество ' + str(i), random.randint(1, 4), 'Объект ' + str(i), 'Печать ' + str(i))
        #c.execute('INSERT INTO state_contract (id, title, date, title_place_id, contract_number, bank_details_id, description, customer, contructor, signature, address, contacts, firstname, lastname, patronymic, empployee_id, object_title, stamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', contract)

    conn.commit()
    conn.close()

try:
    create_database()
    populate_database()
except:
    pass

# Добавляем данные в таблицу
def add_state_contract(ID, title, date, place, contract_number, description, customer, contructor, stamp, signature, address, contacts, firstname, lastname, employee_position, patronymic):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO state_contract (id, title, date, place, contract_number, description, customer, contructor, stamp, signature, address, contacts, firstname, lastname, employee_position, patronymic)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ID, title, date, place, contract_number, description, customer, contructor, stamp, signature, address, contacts, firstname, lastname, employee_position, patronymic))

    # Сохраняем изменения в базе данных
    conn.commit()

#add_table()
#add_state_contract(12, "Новый договор", "2023-04-23", "Санкт-Петербург", "5678-9012-3456", "Описание нового договора", "Заказчик", "Исполнитель", "Печать", "Подпись", "Адрес", "Контакты", "Имя", "Фамилия", "Должность", "Отчество")


#conn.close()
