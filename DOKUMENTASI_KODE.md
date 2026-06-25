# Dokumentasi Kode Versi Paling Minimal

Kode utama hanya 3 file Python:

- `webserver.py`
- `proxy.py`
- `client.py`

Total sekitar 351 baris. Tidak memakai library eksternal. Semua memakai library bawaan Python.

## Library yang Dipakai

- `socket`: TCP dan UDP
- `threading`: multi-client
- `time`: RTT dan log waktu
- `mimetypes`: menentukan `Content-Type`
- `hashlib`: nama file cache
- `argparse`: argumen command line
- `statistics`: rata-rata dan jitter

## Flow Besar

```text
Client -> Proxy -> Webserver
```

Port:

```text
Proxy      : TCP 8080
Webserver  : TCP 8000
UDP Echo   : UDP 9000
```

## webserver.py

Tugas:

- membuka HTTP server di port `8000`
- membuka UDP echo server di port `9000`
- melayani request `GET`
- mengirim `200 OK` jika file ada
- mengirim `404 Not Found` jika file tidak ada
- memakai thread untuk tiap request HTTP

Function:

| Function | Fungsi |
|---|---|
| `log` | cetak log pendek |
| `response` | membuat HTTP response |
| `read_html_file` | baca file dari folder `HTML` |
| `handle_http` | proses satu request HTTP |
| `run_http` | menjalankan TCP server |
| `run_udp` | menjalankan UDP echo |

Flow HTTP:

```text
Terima request -> cek GET -> baca file -> kirim 200/404 -> tutup koneksi
```

Flow UDP:

```text
Terima paket -> kirim balik paket yang sama
```

## proxy.py

Tugas:

- membuka proxy di port `8080`
- menerima request client
- mengecek cache
- jika cache ada: `HIT`
- jika cache belum ada: `MISS`, lalu request ke webserver
- menyimpan response `200 OK` ke cache
- memakai thread untuk tiap client

Function:

| Function | Fungsi |
|---|---|
| `log` | cetak log pendek |
| `error` | membuat response error |
| `get_path` | mengambil path dari request |
| `ask_server` | meneruskan request ke webserver |
| `handle_client` | proses satu request client |
| `run` | menjalankan proxy |

Flow MISS:

```text
Client -> Proxy -> Webserver -> Proxy -> Client
```

Flow HIT:

```text
Client -> Proxy -> Client
```

## client.py

Tugas:

- mode TCP: request halaman lewat proxy
- mode UDP: mengirim paket ping dan menghitung QoS
- bisa menjalankan 5 client bersamaan

Function:

| Function | Fungsi |
|---|---|
| `tcp_get` | request HTTP ke proxy |
| `tcp_mode` | TCP single atau concurrent |
| `udp_mode` | UDP ping dan hitung QoS |
| `main` | membaca argumen dan memilih mode |

Mode TCP:

```bash
python3 client.py --mode tcp --path /index.html
```

Mode UDP:

```bash
python3 client.py --mode udp --count 10
```

Multi-client:

```bash
python3 client.py --mode tcp --path /qos.html --concurrent 5
```

## Demo

Terminal 1:

```bash
python3 webserver.py
```

Terminal 2:

```bash
python3 proxy.py
```

Terminal 3:

```bash
python3 client.py --mode tcp --path /index.html
python3 client.py --mode tcp --path /index.html
python3 client.py --mode tcp --path /missing.html
python3 client.py --mode udp --count 10
python3 client.py --mode tcp --path /qos.html --concurrent 5
```

Jika port `8080` bentrok:

```bash
PROXY_PORT=18080 python3 proxy.py
python3 client.py --mode tcp --proxy-port 18080 --path /index.html
```

## Wireshark

Filter normal:

```text
tcp.port==8000 || tcp.port==8080 || udp.port==9000
```

Jika pakai proxy port `18080`:

```text
tcp.port==8000 || tcp.port==18080 || udp.port==9000
```

Yang ditunjukkan:

- `MISS`: ada trafik client ke proxy dan proxy ke webserver
- `HIT`: cukup client ke proxy
- UDP `9000`: paket QoS

## Kalimat Presentasi

```text
Program ini membuat sistem Client-Proxy-Server menggunakan socket Python.
Client meminta halaman ke proxy, bukan langsung ke webserver.
Proxy mengecek cache. Jika belum ada, proxy meneruskan request ke webserver dan mencatat MISS.
Jika sudah ada, proxy langsung mengirim dari cache dan mencatat HIT.
UDP digunakan untuk menghitung RTT, packet loss, throughput, dan jitter.
Threading digunakan agar server dan proxy bisa menangani beberapa client sekaligus.
```
