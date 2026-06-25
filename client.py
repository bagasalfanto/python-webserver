import argparse
import socket
import statistics
import threading
import time


def tcp_get(host, port, path, simple=False):
    if not path.startswith("/"):
        path = "/" + path

    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Connection: close\r\n\r\n"
    ).encode()

    start = time.perf_counter()
    reply = b""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((host, port))
        s.sendall(request)
        while True:
            data = s.recv(65536)
            if not data:
                break
            reply += data

    ms = (time.perf_counter() - start) * 1000
    status = reply.split(b"\r\n", 1)[0].decode(errors="ignore")

    if simple:
        print(f"{threading.current_thread().name}: {status} {ms:.2f}ms")
    else:
        print(reply.decode(errors="ignore"))
        print(f"\nResponse time: {ms:.2f}ms")


def tcp_mode(args):
    if args.concurrent <= 1:
        tcp_get(args.proxy_host, args.proxy_port, args.path)
        return

    threads = []
    for i in range(args.concurrent):
        t = threading.Thread(
            target=tcp_get,
            args=(args.proxy_host, args.proxy_port, args.path, True),
            name=f"client-{i + 1}",
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


def udp_mode(args):
    rtts = []
    received = 0
    total_bytes = 0
    test_start = time.perf_counter()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(args.timeout)

        for i in range(1, args.count + 1):
            msg = f"Ping {i} {time.time()}".encode()
            start = time.perf_counter()
            s.sendto(msg, (args.server_host, args.server_udp_port))

            try:
                data, _addr = s.recvfrom(4096)
                rtt = (time.perf_counter() - start) * 1000
                rtts.append(rtt)
                received += 1
                total_bytes += len(data)
                print(f"Ping {i}: RTT={rtt:.2f}ms")
            except socket.timeout:
                print(f"Ping {i}: Request timed out")

            time.sleep(args.interval)

    duration = max(time.perf_counter() - test_start, 0.000001)
    loss = ((args.count - received) / args.count) * 100
    throughput = (total_bytes * 8 / duration) / 1000
    diffs = [abs(rtts[i] - rtts[i - 1]) for i in range(1, len(rtts))]
    jitter = statistics.stdev(diffs) if len(diffs) > 1 else (diffs[0] if diffs else 0)

    print("\nUDP QoS Summary")
    print(f"Sent: {args.count}")
    print(f"Received: {received}")
    print(f"Packet Loss: {loss:.2f}%")
    print(f"Throughput: {throughput:.2f} kbps")
    print(f"RTT Min: {min(rtts):.2f}ms" if rtts else "RTT Min: -")
    print(f"RTT Avg: {statistics.mean(rtts):.2f}ms" if rtts else "RTT Avg: -")
    print(f"RTT Max: {max(rtts):.2f}ms" if rtts else "RTT Max: -")
    print(f"Jitter: {jitter:.2f}ms" if rtts else "Jitter: -")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["tcp", "udp"], default="tcp")
    p.add_argument("--proxy-host", default="127.0.0.1")
    p.add_argument("--proxy-port", type=int, default=8080)
    p.add_argument("--server-host", default="127.0.0.1")
    p.add_argument("--server-udp-port", type=int, default=9000)
    p.add_argument("--path", default="/index.html")
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--timeout", type=float, default=1)
    p.add_argument("--interval", type=float, default=0.2)
    p.add_argument("--concurrent", type=int, default=1)
    args = p.parse_args()

    if args.mode == "tcp":
        tcp_mode(args)
    else:
        udp_mode(args)


if __name__ == "__main__":
    main()
