import socket
import json
import os

class Client:
    def __init__(self, host: str = 'localhost', config_file: str = "config/config.json"):
        self._host = host
        self._port = self._load_port_from_config(config_file)

    def _load_port_from_config(self, config_file: str) -> int:
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

    def send_command(self, command: str) -> str:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self._host, self._port))
            client.send(command.encode('utf-8'))
            response = client.recv(1024).decode('utf-8').strip()
            return response
        finally:
            client.close()

    def run(self):
        while True:
            command = input("> ").strip()
            if command.lower() == "quit":
                break
            if command:
                print(self.send_command(command))

if __name__ == "__main__":
    client = Client()
    client.run()