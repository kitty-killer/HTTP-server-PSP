import datetime
import os

# MIME-типы содержимого с кодировкой UTF-8
CONTENT_TYPES = {
    'jpg': 'image/jpeg',
    'html': 'text/html; charset=utf-8',
    'json': 'application/json; charset=utf-8',
    'txt': 'text/plain; charset=utf-8',
    '': 'text/plain; charset=utf-8',
}

# Сообщение о ненайденном ресурсе
NOT_FOUND_MESSAGE = "NOT FOUND"

def get_request_url(request):
    # Извлекает URL из HTTP-запроса
    lines = request.split("\r\n")
    first_line = lines[0]
    return first_line.split(" ")[1]

def get_request_method(request):
    # Извлекает метод (GET, POST и т.д.) из HTTP-запроса
    lines = request.split("\r\n")
    first_line = lines[0]
    return first_line.split(" ")[0]

def get_file_extension(file_path):
    # Извлекает расширение файла
    _, ext = os.path.splitext(file_path)
    return ext[1:]

def send_header(client, status_code, status_text, content_type, length):
    # Формирует и отправляет HTTP-заголовки
    header = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {length}\r\n"
        f"Connection: close\r\n"
        f"Date: {datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        f"Server: PythonHTTP/0.1\r\n"
        "\r\n"
    )
    client.sendall(header.encode('utf-8'))
