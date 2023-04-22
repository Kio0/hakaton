import sqlite3
import os
import io
import base64

def save_file(filename, file_data, sender_id=-1, recipient_id=-1):
    # Проверяем, что папка documents существует. Если нет, то создаем ее
    if not os.path.exists('documents'):
        os.makedirs('documents')
    
    # Если передана строка base64, декодируем ее в байтовую строку
    if isinstance(file_data, str):
        file_data = base64.b64decode(file_data)
    
    # Сохраняем файл в папке documents
    with io.open(os.path.join('documents', filename), 'wb') as f:
        f.write(file_data)
    
    # Добавляем запись в таблицу documents базы данных
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    
    # Создаем таблицу, если она не существует
    c.execute('''CREATE TABLE IF NOT EXISTS documents 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT NOT NULL, 
                  size INTEGER NOT NULL,
                  sender_id INTEGER NOT NULL,
                  recipient_id INTEGER NOT NULL)''')
    
    # Вычисляем размер файла в байтах
    size = len(file_data)
    
    # Вставляем запись в таблицу
    c.execute("INSERT INTO documents (name, size, sender_id, recipient_id) VALUES (?, ?, ?, ?)", (filename, size, sender_id, recipient_id))
    
    # Сохраняем изменения
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




#read_file_base64('6.  заявка на г-образные опоры.xlsx')












