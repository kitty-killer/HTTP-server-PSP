import socket
from handler import Handler
import sys
from logger import write_log  # Импортируем функцию записи логов

class Server:
    def __init__(self, port, directory):
        # Инициализация сервера с указанным портом и директорией
        self.port = port
        self.directory = directory

    def start(self):
        # Логируем информацию о порте и директории
        write_log(f"Сервер запускается на порту {self.port} с использованием директории {self.directory}")
        
        # Запуск сервера и прослушивание подключений
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(5)
            print(f"Serving on port {self.port}")

            while True:
                # Принятие входящего подключения
                client_socket, _ = server_socket.accept()
                # Создание и запуск обработчика для каждого подключения
                handler = Handler(client_socket, self.directory)
                handler.start()

if __name__ == "__main__":
    # Получение порта и директории из аргументов командной строки или использование значений по умолчанию
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    directory = sys.argv[2] if len(sys.argv) > 2 else './www'
    # Создание экземпляра сервера и его запуск
    server = Server(port, directory)
    server.start()
