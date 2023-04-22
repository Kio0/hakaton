import sqlite3
import os
import io
import base64
import hashlib


def save_file(filename, file_data, sender_id=-1, recipient_id=-1):
    # Проверяем, что папка documents существует. Если нет, то создаем ее
    if not os.path.exists('documents'):
        os.makedirs('documents')

    # Если передана строка base64, декодируем ее в байтовую строку
    if isinstance(file_data, str):
        file_data = base64.b64decode(file_data)

    # Добавляем запись в таблицу documents базы данных
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Создаем таблицу, если она не существует
    c.execute('''CREATE TABLE IF NOT EXISTS documents 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT NOT NULL, 
                  size INTEGER NOT NULL,
                  sender_id INTEGER NOT NULL,
                  recipient_id INTEGER NOT NULL,
                  md5 TEXT NOT NULL)''')

    # Вычисляем размер файла в байтах
    size = len(file_data)

    # Вычисляем md5 хэш от файла
    md5 = hashlib.md5(file_data).hexdigest()

    # Вставляем запись в таблицу и получаем ее ID
    c.execute("INSERT INTO documents (name, size, sender_id, recipient_id, md5) VALUES (?, ?, ?, ?, ?)",
              (filename, size, sender_id, recipient_id, md5))
    file_id = c.lastrowid

    # Сохраняем файл в папке documents
    with io.open(os.path.join('documents', f'{file_id}_{filename}'), 'wb') as f:
        f.write(file_data)

    # Сохраняем изменения в базе данных
    conn.commit()

    # Закрываем соединение с базой данных
    conn.close()


def read_file_byte(filename, sender_id=-1, recipient_id=-1):
    # Проверяем, что файл существует
    if not os.path.isfile(filename):
        print(f'Ошибка: файл {filename} не найден.')
        return

    # Считываем файл в виде байтов
    with open(filename, 'rb') as f:
        file_data = f.read()

    # Вызываем функцию save_file для сохранения файла и добавления записи в базу данных
    save_file(filename, file_data, sender_id, recipient_id)


def read_file_base64(filename, sender_id=-1, recipient_id=-1):
    # Проверяем, что файл существует
    if not os.path.isfile(filename):
        print(f'Ошибка: файл {filename} не найден.')
        return None

    # Считываем файл в виде байтов
    with open(filename, 'rb') as f:
        file_data = f.read()

    # Кодируем содержимое файла в строку base64
    file_data_base64 = base64.b64encode(file_data).decode('utf-8')

    save_file(filename, file_data_base64, sender_id, recipient_id)


#Возвращает файл

def get_file(file):
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    # Определяем тип входных данных
    if isinstance(file, int):
        # Если входной параметр является числом, то это и есть ID файла
        file_id = file
        c.execute("SELECT name FROM documents WHERE id=?", (file_id,))
        filename = c.fetchone()[0]
    elif isinstance(file, str):
        # Если входной параметр является строкой, то определяем, является ли он HEX-кодом
        try:
            file_id = int(file, 16)
            c.execute("SELECT name FROM documents WHERE id=?", (file_id,))
            filename = c.fetchone()[0]
        except ValueError:
            # Если не является HEX-кодом, то это и есть название файла

            c.execute("SELECT id, name FROM documents WHERE name=?", (file,))
            result = c.fetchone()
            if not result:
                # Если файл с таким именем не найден, бросаем исключение
                raise ValueError(f"Файл с именем {file} не найден")
            file_id, filename = result
        else:
            # Если является HEX-кодом, то ищем файл с таким ID в базе данных
            conn = sqlite3.connect('mydatabase.db')
            c = conn.cursor()
            c.execute("SELECT name FROM documents WHERE id=?", (file_id,))
            result = c.fetchone()
            if not result:
                # Если файл с таким ID не найден, бросаем исключение
                raise ValueError(f"Файл с ID {file} не найден")
            filename = result[0]    
    else:
        raise ValueError("Некорректный тип входных данных")
    
    # Считываем файл из папки documents
    with open(os.path.join('documents', f"{file_id}_{filename}"), 'rb') as f:
        file_data = f.read()
    conn.close()
    # Перекодируем файл в base64 и возвращаем результат
    return base64.b64encode(file_data).decode('utf-8')

#print(get_file('11331'))




#read_file_base64('11331.xlsx')
