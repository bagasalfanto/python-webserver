import mimetypes
import socket
import threading
import time
from pathlib import Path
from urllib.parse import unquote


HOST = "0.0.0.0"
HTTP_PORT = 8000
UDP_PORT = 9000
ROOT = Path(__file__).parent
HTML_DIR = ROOT / "HTML"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def response(status, body, content_type="text/html; charset=utf-8"):
    if isinstance(body, str):
        body = body.encode()
    header = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return header.encode() + body


def read_html_file(url_path):
    path = unquote(url_path.split("?", 1)[0])
    if path == "/":
        path = "/index.html"
    path = path.lstrip("/")

    if ".." in path:
        return None, None

    content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    if content_type.startswith("text/"):
        content_type += "; charset=utf-8"

    file_path = HTML_DIR / path
    if file_path.exists():
        return file_path.read_bytes(), content_type

    return None, None


def handle_http(conn, addr):
    status = "500 Internal Server Error"
    path = "-"
    try:
        request = conn.recv(4096).decode(errors="ignore")
        method, path, _version = request.splitlines()[0].split()

        if method != "GET":
            status = "400 Bad Request"
            data = response(status, "<h1>400 Bad Request</h1>")
        else:
            body, content_type = read_html_file(path)
            if body is None:
                status = "404 Not Found"
                data = response(status, "<h1>404 Not Found</h1>")
            else:
                status = "200 OK"
                data = response(status, body, content_type)

        conn.sendall(data)
    except Exception as e:
        conn.sendall(response(status, f"<h1>500 Internal Server Error</h1><p>{e}</p>"))
    finally:
        conn.close()
        log(f"HTTP {addr[0]} {path} {status}")


def run_http():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, HTTP_PORT))
    s.listen()
    log(f"HTTP server on port {HTTP_PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_http, args=(conn, addr), daemon=True).start()


def run_udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, UDP_PORT))
    log(f"UDP echo on port {UDP_PORT}")

    while True:
        data, addr = s.recvfrom(4096)
        s.sendto(data, addr)
        log(f"UDP echo {addr[0]}:{addr[1]}")


if __name__ == "__main__":
    threading.Thread(target=run_udp, daemon=True).start()
    run_http()
