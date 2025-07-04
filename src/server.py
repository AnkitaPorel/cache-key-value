import socket
import threading
import json
import os
from store import Store

class Server:
    def __init__(self, host: str = 'localhost', config_file: str = "config/config.json"):
        self._host = host
        self._port = self._load_port_from_config(config_file)
        self._store = Store()

    def _load_port_from_config(self, config_file: str) -> int:
        """Load port from config file, default to 6379 if file is missing or invalid."""
        default_port = 6379
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return int(config.get('port', default_port))
            else:
                print(f"Config file {config_file} not found, using default port {default_port}")
                return default_port
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error reading config file {config_file}: {e}, using default port {default_port}")
            return default_port

    def handle_client(self, client_socket: socket.socket):
        """Handle client connection and process commands."""
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    break

                parts = data.split()
                if not parts:
                    client_socket.send(b"ERROR: Empty command\n")
                    continue

                command = parts[0].upper()
                if command == "SET" and len(parts) == 3:
                    key, value = parts[1], parts[2]
                    self._store.set(key, value)
                    client_socket.send(b"OK\n")
                elif command == "GET" and len(parts) == 2:
                    key = parts[1]
                    value = self._store.get(key)
                    if value is None:
                        client_socket.send(b"NULL\n")
                    else:
                        client_socket.send(f"{value}\n".encode('utf-8'))
                elif command == "DEL" and len(parts) == 2:
                    key = parts[1]
                    if self._store.delete(key):
                        client_socket.send(b"OK\n")
                    else:
                        client_socket.send(b"NULL\n")
                else:
                    client_socket.send(b"ERROR: Invalid command\n")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def start(self):
        """Start the server and listen for connections."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self._host, self._port))
        server.listen(5)
        print(f"Server listening on {self._host}:{self._port}")

        try:
            while True:
                client_socket, addr = server.accept()
                print(f"Connected to {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            server.close()

if __name__ == "__main__":
    server = Server()
    server.start()