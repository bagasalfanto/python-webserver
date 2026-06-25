# Dokumentasi Penggunaan Tugas Besar

Judul yang disarankan:

**Implementasi Sistem Client-Proxy-Server Sederhana Berbasis Socket Python dengan Proxy Cache dan QoS UDP**

## 1. Ringkasan Program

Program ini membuat sistem jaringan sederhana dengan arsitektur:

```text
Client -> Proxy Server -> Web Server
```

Sistem hanya menggunakan 3 file Python utama:

- `webserver.py`
- `proxy.py`
- `client.py`

Fitur utama:

- Web server TCP berjalan di port `8000`
- UDP echo server berjalan di port `9000`
- Proxy server berjalan di port `8080`
- Client mengakses halaman melalui proxy
- Proxy mendukung cache `HIT` dan `MISS`
- Client punya mode TCP dan UDP
- UDP digunakan untuk menghitung QoS: RTT, packet loss, throughput, dan jitter
- Webserver dan proxy mendukung multi-client dengan threading

## 2. Persiapan

Pastikan Python 3 sudah terpasang.

Masuk ke folder program:

```bash
cd "Tugas Besar"
```

Urutan menjalankan wajib:

```text
1. webserver.py
2. proxy.py
3. client.py
```

Jika urutan salah, biasanya muncul error:

```text
Connection refused
```

## 3. Menjalankan Web Server

Buka terminal pertama:

```bash
python3 webserver.py
```

Output yang diharapkan:

```text
UDP echo server running on 0.0.0.0:9000
HTTP server running on 0.0.0.0:8000
```

Fungsi `webserver.py`:

- menerima request HTTP GET dari proxy
- mengirim file HTML
- mengembalikan status `200 OK` jika file ada
- mengembalikan status `404 Not Found` jika file tidak ada
- menjalankan UDP echo server
- menangani lebih dari satu koneksi dengan threading

## 4. Menjalankan Proxy Server

Buka terminal kedua:

```bash
python3 proxy.py
```

Output yang diharapkan:

```text
Proxy listening on 0.0.0.0:8080, forwarding to 127.0.0.1:8000
```

Fungsi `proxy.py`:

- menerima request dari client
- meneruskan request ke webserver
- mengirim response kembali ke client
- menyimpan response sukses ke cache
- menampilkan status cache `MISS` untuk request pertama
- menampilkan status cache `HIT` untuk request berikutnya dengan URL sama

## 5. Menjalankan Client Mode TCP

Buka terminal ketiga:

```bash
python3 client.py --mode tcp --path /index.html
```

Output yang diharapkan:

```text
HTTP/1.1 200 OK
...
Response time: ... ms
```

Untuk menguji cache, jalankan command yang sama dua kali:

```bash
python3 client.py --mode tcp --path /index.html
python3 client.py --mode tcp --path /index.html
```

Pada terminal proxy, hasil yang diharapkan:

```text
cache=MISS
cache=HIT
```

## 6. Menguji Error 404

Jalankan:

```bash
python3 client.py --mode tcp --path /missing.html
```

Output yang diharapkan:

```text
HTTP/1.1 404 Not Found
<h1>404 Not Found</h1>
```

## 7. Menjalankan Client Mode UDP QoS

Jalankan:

```bash
python3 client.py --mode udp --count 10
```

Output yang diharapkan:

```text
Ping 1: RTT=... ms
Ping 2: RTT=... ms
...

UDP QoS Summary
Sent: 10
Received: 10
Packet Loss: ...%
Throughput: ... kbps
RTT Min: ... ms
RTT Avg: ... ms
RTT Max: ... ms
Jitter: ... ms
```

Parameter yang dianalisis:

- RTT minimum
- RTT rata-rata
- RTT maksimum
- packet loss
- throughput
- jitter

## 8. Menguji 5 Client Bersamaan

Jalankan:

```bash
python3 client.py --mode tcp --path /qos.html --concurrent 5
```

Output yang diharapkan:

```text
client-1: HTTP/1.1 200 OK ... ms
client-2: HTTP/1.1 200 OK ... ms
client-3: HTTP/1.1 200 OK ... ms
client-4: HTTP/1.1 200 OK ... ms
client-5: HTTP/1.1 200 OK ... ms
```

Pada terminal proxy dan webserver akan terlihat beberapa thread berjalan.

## 9. Pengujian Wireshark

Jalankan Wireshark pada interface jaringan yang digunakan.

Gunakan display filter:

```text
tcp.port==8000 || tcp.port==8080 || udp.port==9000
```

Yang perlu dibuktikan:

- TCP port `8080`: komunikasi client ke proxy
- TCP port `8000`: komunikasi proxy ke webserver
- UDP port `9000`: paket UDP ping/echo untuk QoS
- tidak ada HTTP langsung dari client ke webserver
- terlihat beberapa koneksi saat multi-client

## 10. Screenshot untuk Dokumentasi

Screenshot minimal:

- webserver berhasil berjalan
- proxy berhasil berjalan
- client berhasil request halaman
- log cache `MISS`
- log cache `HIT`
- hasil UDP QoS
- hasil 5 client bersamaan
- error `404 Not Found`
- capture Wireshark dengan filter port `8000`, `8080`, dan `9000`

## 11. Alur Demo Presentasi

Urutan demo yang disarankan:

1. Jelaskan arsitektur singkat: `Client -> Proxy -> Web Server`
2. Jalankan `webserver.py`
3. Jalankan `proxy.py`
4. Jalankan client TCP untuk `/index.html`
5. Jalankan request yang sama lagi untuk menunjukkan cache `HIT`
6. Jalankan request `/missing.html` untuk menunjukkan `404`
7. Jalankan client UDP untuk menunjukkan statistik QoS
8. Jalankan 5 client bersamaan
9. Tunjukkan hasil capture Wireshark
10. Simpulkan bahwa sistem berhasil menjalankan TCP, UDP, proxy cache, dan multithreading

## 12. Poin Penjelasan Saat Presentasi

Penjelasan singkat untuk tiap file:

`webserver.py`

- berperan sebagai server utama
- melayani file HTML melalui TCP
- menjalankan UDP echo untuk pengujian QoS
- menggunakan threading agar bisa menangani banyak koneksi

`proxy.py`

- berperan sebagai perantara antara client dan webserver
- meneruskan request ke webserver jika cache belum ada
- mengambil response dari cache jika URL sudah pernah diminta
- mencatat status `HIT` atau `MISS`

`client.py`

- mode TCP digunakan untuk meminta halaman melalui proxy
- mode UDP digunakan untuk menguji performa jaringan
- menghitung RTT, packet loss, throughput, dan jitter

## 13. Kesimpulan Singkat

Program berhasil mengimplementasikan sistem Client-Proxy-Server berbasis socket Python. Komunikasi HTTP berjalan menggunakan TCP, pengujian QoS berjalan menggunakan UDP, proxy dapat melakukan forwarding dan caching, serta sistem mampu menangani beberapa client secara bersamaan menggunakan threading.
