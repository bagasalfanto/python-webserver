import hashlib
import os
import socket
import threading
import time
from pathlib import Path


HOST = "0.0.0.0"
PROXY_PORT = int(os.getenv("PROXY_PORT", "8080"))
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
CACHE = Path(__file__).parent / "cache"
LOCK = threading.Lock()


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def error(status):
    body = f"<h1>{status}</h1>".encode()
    header = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return header.encode() + body


def get_path(request):
    try:
        method, path, _version = request.decode(errors="ignore").splitlines()[0].split()
        if method != "GET":
            return None
        return "/index.html" if path == "/" else path.split("?", 1)[0]
    except Exception:
        return None


def ask_server(path):
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {SERVER_HOST}:{SERVER_PORT}\r\n"
        "Connection: close\r\n\r\n"
    ).encode()
    reply = b""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((SERVER_HOST, SERVER_PORT))
        s.sendall(request)
        while True:
            data = s.recv(4096)
            if not data:
                break
            reply += data

    return reply


def handle_client(conn, addr):
    start = time.perf_counter()
    path = "-"
    cache_status = "-"
    status = "-"

    try:
        conn.settimeout(5)
        request = conn.recv(65536)
        path = get_path(request)

        if path is None:
            reply = error("400 Bad Request")
        else:
            cache_name = hashlib.sha256(path.encode()).hexdigest() + ".cache"
            cache_file = CACHE / cache_name

            with LOCK:
                if cache_file.exists():
                    reply = cache_file.read_bytes()
                    cache_status = "HIT"
                else:
                    cache_status = "MISS"
                    try:
                        reply = ask_server(path)
                    except socket.timeout:
                        reply = error("504 Gateway Timeout")
                    except OSError:
                        reply = error("502 Bad Gateway")

                    if reply.startswith(b"HTTP/1.1 200") or reply.startswith(b"HTTP/1.0 200"):
                        CACHE.mkdir(exist_ok=True)
                        cache_file.write_bytes(reply)

        conn.sendall(reply)
        status = reply.split(b"\r\n", 1)[0].decode(errors="ignore")
    finally:
        conn.close()
        ms = (time.perf_counter() - start) * 1000
        log(f"{addr[0]} {path} {cache_status} {status} {ms:.2f}ms")


def run():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PROXY_PORT))
    s.listen()
    log(f"Proxy on port {PROXY_PORT}, server {SERVER_HOST}:{SERVER_PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    run()
