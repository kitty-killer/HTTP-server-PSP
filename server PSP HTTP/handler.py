import os
from threading import Thread
from utils import CONTENT_TYPES, NOT_FOUND_MESSAGE, get_request_url, get_request_method, get_file_extension, send_header
from logger import write_log  # Импортируем функцию записи логов

class Handler(Thread):
    def __init__(self, client_socket, directory):
        super().__init__()
        self.client_socket = client_socket
        self.directory = directory

    def run(self):
        try:
            with self.client_socket as client:
                request = client.recv(1024).decode('utf-8')
                url = get_request_url(request)
                method = get_request_method(request)
                file_path = os.path.join(self.directory, url.strip('/'))

                # Запись логов для каждого запроса
                write_log(f"Received {method} request for {url}")

                if method == 'GET':
                    self.handle_get(client, file_path)
                elif method == 'POST':
                    self.handle_post(client, file_path, request)
                elif method == 'PUT':
                    self.handle_put(client, file_path, request)
                elif method == 'DELETE':
                    self.handle_delete(client, file_path)
                else:
                    send_header(client, 405, "Method Not Allowed", 'text/plain', 0)
                    write_log(f"Method {method} not allowed for {url}")
        except Exception as e:
            error_message = f"Error handling request: {e}"
            write_log(error_message)
            print(error_message)

    def handle_get(self, client, file_path):
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            extension = get_file_extension(file_path)
            content_type = CONTENT_TYPES.get(extension, 'text/plain')
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            send_header(client, 200, "OK", content_type, len(file_bytes))
            client.sendall(file_bytes)
            write_log(f"Served file {file_path}")
        else:
            content_type = CONTENT_TYPES.get('text')
            send_header(client, 404, "Not Found", content_type, len(NOT_FOUND_MESSAGE))
            client.sendall(NOT_FOUND_MESSAGE.encode('utf-8'))
            write_log(f"File not found: {file_path}")

    def handle_post(self, client, file_path, request):
        if os.path.exists(file_path):
            send_header(client, 409, "Conflict", 'text/plain', 0)
            write_log(f"Conflict: File {file_path} already exists")
        else:
            body = request.split("\r\n\r\n", 1)[1]
            with open(file_path, 'wb') as f:
                f.write(body.encode('utf-8'))
            send_header(client, 201, "Created", 'text/plain', 0)
            write_log(f"Created file {file_path}")

    def handle_put(self, client, file_path, request):
        body = request.split("\r\n\r\n", 1)[1]
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                existing_content = f.read().decode('utf-8')
            if existing_content == body:
                send_header(client, 304, "Not Modified", 'text/plain', 0)
                write_log(f"Not modified: File {file_path} content unchanged")
            else:
                with open(file_path, 'wb') as f:
                    f.write(body.encode('utf-8'))
                send_header(client, 200, "OK", 'text/plain', 0)
                write_log(f"Updated file {file_path}")
        else:
            with open(file_path, 'wb') as f:
                f.write(body.encode('utf-8'))
            send_header(client, 201, "Created", 'text/plain', 0)
            write_log(f"Created file {file_path}")

    def handle_delete(self, client, file_path):
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            os.remove(file_path)
            send_header(client, 200, "OK", 'text/plain', 0)
            write_log(f"Deleted file {file_path}")
        else:
            content_type = CONTENT_TYPES.get('text')
            send_header(client, 404, "Not Found", content_type, len(NOT_FOUND_MESSAGE))
            client.sendall(NOT_FOUND_MESSAGE.encode('utf-8'))
            write_log(f"File not found: {file_path}")
