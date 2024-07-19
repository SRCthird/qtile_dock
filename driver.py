import os
import sys
import socket
import threading
from PyQt5 import QtWidgets
import json
from .desktop_files import DesktopFiles
from .ui import DockUI

stop_flag = threading.Event()

PORT = 44947


def is_another_instance_running():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect(('127.0.0.1', PORT))
        except (socket.timeout, ConnectionRefusedError):
            return False
        else:
            return True


def handle_client(client_socket, dock):
    with client_socket:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            elif message == "toggle":
                dock.toggle_visibility()
            elif message == "stop":
                print("Stopping the server and application...")
                stop_flag.set()
                dock.stop_signal.emit()
                break
            else:
                print(f"Received message: {message}")


def run_server(dock):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", PORT))
    server.listen(5)
    print("Server started, waiting for messages...")

    client_threads = []

    try:
        while not stop_flag.is_set():
            try:
                server.settimeout(1)
                client_socket, _ = server.accept()
                client_handler = threading.Thread(
                    target=handle_client, args=(client_socket, dock))
                client_handler.start()
                client_threads.append(client_handler)
            except socket.timeout:
                continue
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server.close()
        print("Server stopped.")
        for thread in client_threads:
            thread.join()


def start_application(search_apps=[], show=False, config=None):
    app = QtWidgets.QApplication(sys.argv)

    icons = DesktopFiles(search_apps).get()

    dock = DockUI(icons, config)
    if show:
        dock.toggle_visibility()

    server_thread = threading.Thread(target=run_server, args=(dock,))
    server_thread.start()

    app.exec_()

    stop_flag.set()
    server_thread.join()


def call(command=""):
    if is_another_instance_running():
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", PORT))
        client.send(command.encode())
        client.close()
        return


def list(search_apps=[]):
    items = DesktopFiles(search_apps).get()
    print(json.dumps(items, indent=4))


def launch(search_apps=[], show=False, config=None):
    if is_another_instance_running():
        return
    if config is None:
        config = os.path.join(os.path.dirname(__file__), 'styles.css')
    start_application(search_apps, show, config)
