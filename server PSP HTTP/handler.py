import os
from threading import Thread
from utils import CONTENT_TYPES, NOT_FOUND_MESSAGE, get_request_url, get_request_method, get_file_extension, send_header
from logger import write_log  # Импортируем функцию записи логов

class Handler(Thread):
    def __init__(self, client_socket, directory):
        super().__init__()
        self.client_socket = client_socket  # Сохраняем клиентский сокет
        self.directory = directory  # Директория для поиска файлов

    def run(self):
        # Главная функция обработки запроса
        try:
            with self.client_socket as client:
                # Получаем и декодируем запрос от клиента
                request = client.recv(1024).decode('utf-8')
                url = get_request_url(request)  # Извлекаем URL из запроса
                method = get_request_method(request)  # Извлекаем метод запроса (GET, POST и т.д.)
                file_path = os.path.join(self.directory, url.strip('/'))  # Формируем путь к запрашиваемому файлу

                # Запись логов для каждого запроса
                write_log(f"Received {method} request for {url}")

                # Обработка запроса в зависимости от метода
                if method == 'GET':
                    self.handle_get(client, file_path)
                elif method == 'POST':
                    self.handle_post(client, file_path, request)
                elif method == 'PUT':
                    self.handle_put(client, file_path, request)
                elif method == 'DELETE':
                    self.handle_delete(client, file_path)
                else:
                    # Если метод не поддерживается, отправляем статус 405
                    send_header(client, 405, "Method Not Allowed", 'text/plain', 0)
                    write_log(f"Method {method} not allowed for {url}")
        except Exception as e:
            # Логируем и выводим ошибку при обработке запроса
            error_message = f"Error handling request: {e}"
            write_log(error_message)
            print(error_message)

    def handle_get(self, client, file_path):
        # Обработка GET-запроса
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            # Если файл существует и это не директория, отправляем файл клиенту
            extension = get_file_extension(file_path)  # Извлекаем расширение файла
            content_type = CONTENT_TYPES.get(extension, 'text/plain')  # Определяем MIME-тип файла
            with open(file_path, 'rb') as f:
                file_bytes = f.read()  # Читаем содержимое файла
            send_header(client, 200, "OK", content_type, len(file_bytes))  # Отправляем заголовки ответа
            client.sendall(file_bytes)  # Отправляем содержимое файла
            write_log(f"Served file {file_path}")
        else:
            # Если файл не найден, отправляем статус 404
            content_type = CONTENT_TYPES.get('text')
            send_header(client, 404, "Not Found", content_type, len(NOT_FOUND_MESSAGE))
            client.sendall(NOT_FOUND_MESSAGE.encode('utf-8'))
            write_log(f"File not found: {file_path}")

    def handle_post(self, client, file_path, request):
        # Обработка POST-запроса
        if os.path.exists(file_path):
            # Если файл уже существует, отправляем статус 409
            send_header(client, 409, "Conflict", 'text/plain', 0)
            write_log(f"Conflict: File {file_path} already exists")
        else:
            # Создаем новый файл с переданными данными
            body = request.split("\r\n\r\n", 1)[1]
            with open(file_path, 'wb') as f:
                f.write(body.encode('utf-8'))
            send_header(client, 201, "Created", 'text/plain', 0)
            write_log(f"Created file {file_path}")

    def handle_put(self, client, file_path, request):
        # Обработка PUT-запроса
        body = request.split("\r\n\r\n", 1)[1]
        if os.path.exists(file_path):
            # Обновляем файл, если он уже существует
            with open(file_path, 'rb') as f:
                existing_content = f.read().decode('utf-8')
            if existing_content == body:
                # Если содержимое не изменилось, отправляем статус 304
                send_header(client, 304, "Not Modified", 'text/plain', 0)
                write_log(f"Not modified: File {file_path} content unchanged")
            else:
                with open(file_path, 'wb') as f:
                    f.write(body.encode('utf-8'))
                send_header(client, 200, "OK", 'text/plain', 0)
                write_log(f"Updated file {file_path}")
        else:
            # Создаем новый файл, если он не существует
            with open(file_path, 'wb') as f:
                f.write(body.encode('utf-8'))
            send_header(client, 201, "Created", 'text/plain', 0)
            write_log(f"Created file {file_path}")

    def handle_delete(self, client, file_path):
        # Обработка DELETE-запроса
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            # Удаляем файл, если он существует
            os.remove(file_path)
            send_header(client, 200, "OK", 'text/plain', 0)
            write_log(f"Deleted file {file_path}")
        else:
            # Если файл не найден, отправляем статус 404
            content_type = CONTENT_TYPES.get('text')
            send_header(client, 404, "Not Found", content_type, len(NOT_FOUND_MESSAGE))
            client.sendall(NOT_FOUND_MESSAGE.encode('utf-8'))
            write_log(f"File not found: {file_path}")
