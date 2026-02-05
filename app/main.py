import os
import sys
import threading
import time
import socket
import webview

# Carpeta raíz del proyecto (donde está servidor.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import servidor  # importa tu servidor.py


def wait_port(host="127.0.0.1", port=5000, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def start_backend():
    # Waitress (bloquea), por eso va en hilo
    servidor.run_server(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    # 1) arrancar backend en segundo plano (se apagará al cerrar la app)
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()

    # 2) esperar a que el servidor esté listo
    if not wait_port(port=5000, timeout=20):
        raise RuntimeError("No se pudo iniciar el servidor local en 127.0.0.1:5000")

    # 3) abrir ventana propia (sin navegador)
    webview.create_window(
        title="CORE_SYNC",
        url="http://127.0.0.1:5000/",
        width=1200,
        height=750,
        resizable=True
    )
    webview.start()
