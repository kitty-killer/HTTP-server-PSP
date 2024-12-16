import socket
from handler import Handler
import sys

class Server:
    def __init__(self, port, directory):
        self.port = port
        self.directory = directory

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(5)
            print(f"Serving on port {self.port}")

            while True:
                client_socket, _ = server_socket.accept()
                handler = Handler(client_socket, self.directory)
                handler.start()
if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    directory = sys.argv[2] if len(sys.argv) > 2 else './www'
    server = Server(port, directory)
    server.start()
