# Dokumentasi Panduan: Lingkungan Pengujian `uji-venv`

Direktori ini (`/home/vcc1/uji-venv`) berisi arsitektur pengujian performa sistem (stres komputasi CPU dan memori RAM) pada server AWS EC2 dengan mengimplementasikan arsitektur **Multi-Virtual Environment** (masing-masing modul memiliki *virtual environment* Python terisolasi sendiri).

---

## 1. Daftar Isi
- [1. Daftar Isi](#1-daftar-isi)
- [2. Struktur Direktori](#2-struktur-direktori)
- [3. Cara Kerja Sistem (Arsitektur & Komponen)](#3-cara-kerja-sistem-arsitektur--komponen)
  - [A. Diagram Interaksi Antar Layanan](#a-diagram-interaksi-antar-layanan)
  - [B. Rincian Cara Kerja per Komponen](#b-rincian-cara-kerja-per-komponen)
  - [C. Arsitektur Multi-Virtual Environment](#c-arsitektur-multi-virtual-environment)
- [4. Pemetaan Port \& URL Akses](#4-pemetaan-port--url-akses)
- [5. Cara Menjalankan Program](#5-cara-menjalankan-program)
  - [Metode 1: Menjalankan Otomatis (Direkomendasikan)](#metode-1-menjalankan-otomatis-direkomendasikan)
  - [Metode 2: Menjalankan Manual per Layanan (Multi-Terminal)](#metode-2-menjalankan-manual-per-layanan-multi-terminal)
- [6. Cara Melakukan Stress Test (Uji Beban)](#6-cara-melakukan-stress-test-uji-beban)
  - [A. Melalui Panel Web UI FastAPI](#a-melalui-panel-web-ui-fastapi)
  - [B. Melalui Locust Load Testing (Beban Tinggi)](#b-melalui-locust-load-testing-beban-tinggi)
  - [C. Melalui Dashboard Streamlit (Uji Memori RAM)](#c-melalui-dashboard-streamlit-uji-memori-ram)
  - [D. Melalui Perintah Terminal (cURL)](#d-melalui-perintah-terminal-curl)
- [7. Cara Memantau Pemakaian Resource (Monitoring)](#7-cara-memantau-pemakaian-resource-monitoring)
- [8. Cara Menghentikan Seluruh Layanan](#8-cara-menghentikan-seluruh-layanan)
- [9. Catatan Penting \& Troubleshooting](#9-catatan-penting--troubleshooting)

---

## 2. Struktur Direktori

```text
/home/vcc1/uji-venv/
├── api.py              # Backend FastAPI (Web UI kontrol & Endpoint Uji CPU)
├── dashboard.py        # Frontend Streamlit (AI Vector Simulator & Uji RAM)
├── locustfile.py       # Skenario pengujian beban pengguna bersamaan (Locust)
├── start_all.sh        # Skrip otomatis menjalankan 4 layanan di background
├── stop_all.sh         # Skrip otomatis menghentikan seluruh layanan
├── status.sh           # Skrip pengecekan port dan status aktif proses
├── env-fastapi/        # Virtual Environment khusus FastAPI & Uvicorn (~108 MB)
├── env-streamlit/      # Virtual Environment khusus Streamlit, Pandas, NumPy (~479 MB)
├── env-locust/         # Virtual Environment khusus Locust (~73 MB)
└── env-glances/        # Virtual Environment khusus Glances System Monitor (~42 MB)
```

---

## 3. Cara Kerja Sistem (Arsitektur & Komponen)

### A. Diagram Interaksi Antar Layanan

```
                        +----------------------------+
                        |     Browser Pengguna       |
                        +--------------+-------------+
                                       |
           +---------------------------+---------------------------+
           | (Port 8000)               | (Port 8501)               | (Port 61208)
           v                           v                           v
+----------------------+    +----------------------+    +----------------------+
|    FastAPI (Uvicorn) |    |  Streamlit Dashboard |    |    Glances Monitor   |
|   [Backend & CPU]    |    |     [RAM Stress]     |    |   [Live CPU/RAM UI]  |
+----------^-----------+    +----------------------+    +----------------------+
           |
           | HTTP GET /berat (Beban Request)
+----------+-----------+
|     Locust Worker    |
|   (Web UI: 8089)     |
+----------------------+
```

### B. Rincian Cara Kerja per Komponen

1. **`api.py` (FastAPI Server):**
   - **Rute `/` (Web Panel):** Menyajikan antarmuka visual berbasis HTML dengan tombol *"Jalankan Komputasi Berat"*. Ketika tombol ditekan, skrip Javascript di browser mengirimkan panggilan AJAX/fetch ke endpoint `/berat`.
   - **Rute `/berat` (CPU Stres Engine):** Menjalankan komputasi CPU intensif satu thread (*single core saturation*) dengan menghitung seluruh bilangan prima dari `2` hingga `20.000` menggunakan algoritma *trial division*:
     ```python
     primes = [x for x in range(2, 20000) if all(x % y != 0 for y in range(2, int(x**0.5) + 1))]
     ```
   - Algoritma ini memaksa CPU EC2 melakukan puluhan ribu operasi perulangan modulo matematika dalam hitungan detik.

2. **`dashboard.py` (Streamlit Dashboard):**
   - Berfungsi sebagai **simulator beban memori RAM** (*AI Vector Simulator*).
   - Memanfaatkan library `numpy` dan `pandas` untuk mengalokasikan matriks berdimensi tinggi sebanyak **100.000 baris $\times$ 8 kolom angka *floating point*** ke dalam memori RAM secara instan:
     ```python
     pd.DataFrame(np.random.randn(100000, 8), columns=[f"Dimensi {i}" for i in range(1, 9)])
     ```
   - Alokasi ini langsung meningkatkan konsumsi memori RAM proses hingga > 150 MB dan menyajikannya dalam grafik interaktif (*area chart*).

3. **`locustfile.py` (Locust Load Tester):**
   - Mendefinisikan skenario pengguna virtual (*virtual user*) bernama `APIUser`.
   - Melakukan *looping* permintaan HTTP GET ke endpoint `/berat` dengan jeda tunggu acak 1 hingga 2 detik (`wait_time = between(1, 2)`).
   - Digunakan untuk membanjiri server FastAPI dengan ratusan/ribuan request bersamaan guna mengamati titik jenuh CPU dan stabilitas koneksi jaringan.

4. **Glances (System Monitor):**
   - Aplikasi monitoring sistem berbasis web yang membaca utilisasi *hardware* (CPU total, CPU per core, RAM used/free, Swap, Disk I/O, Network Bandwidth, dan daftar proses paling rakus sumber daya).

### C. Arsitektur Multi-Virtual Environment
Lingkungan ini memisahkan setiap modul ke dalam folder virtual environment independen:
- **`env-fastapi`**: Mengisolasi `fastapi`, `uvicorn`, `pydantic`, `starlette`.
- **`env-streamlit`**: Mengisolasi `streamlit`, `pandas`, `numpy`, `pyarrow`, `altair`.
- **`env-locust`**: Mengisolasi `locust`, `gevent`, `flask`.
- **`env-glances`**: Mengisolasi `glances`, `psutil`.

> [!NOTE]
> **Total Kapasitas Penyimpanan:** Pemisahan ini membutuhkan ruang disk sebesar **~700 MB**. Setiap virtual environment memiliki file binary interpreter Python dan folder `site-packages` sendiri.

---

## 4. Pemetaan Port & URL Akses

| Layanan | Port | Virtual Env Terkait | URL Akses Lokal | URL Eksternal (IP EC2) |
| :--- | :---: | :--- | :--- | :--- |
| **FastAPI** | `8000` | `env-fastapi/` | `http://localhost:8000/` | `http://<IP_EC2>:8000/` |
| **Streamlit** | `8501` | `env-streamlit/` | `http://localhost:8501/` | `http://<IP_EC2>:8501/` |
| **Locust** | `8089` | `env-locust/` | `http://localhost:8089/` | `http://<IP_EC2>:8089/` |
| **Glances** | `61208` | `env-glances/` | `http://localhost:61208/`| `http://<IP_EC2>:61208/` |

---

## 5. Cara Menjalankan Program

### Metode 1: Menjalankan Otomatis (Direkomendasikan)
Telah disediakan *helper script* untuk mengelola keempat layanan sekaligus di background:

1. **Jalankan semua layanan:**
   ```bash
   cd /home/vcc1/uji-venv
   ./start_all.sh
   ```
2. **Periksa status apakah semua port sudah aktif:**
   ```bash
   ./status.sh
   ```
3. **Hentikan semua layanan jika sudah selesai:**
   ```bash
   ./stop_all.sh
   ```

---

### Metode 2: Menjalankan Manual per Layanan (Multi-Terminal)
Jika Anda ingin melihat *output log* langsung di layar terminal secara interaktif, buka 4 terminal terpisah:

#### Terminal 1: Jalankan Glances (Monitoring)
```bash
cd /home/vcc1/uji-venv
source env-glances/bin/activate
glances -w -p 61208
```

#### Terminal 2: Jalankan FastAPI Backend
```bash
cd /home/vcc1/uji-venv
source env-fastapi/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000
```

#### Terminal 3: Jalankan Dashboard Streamlit
```bash
cd /home/vcc1/uji-venv
source env-streamlit/bin/activate
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

#### Terminal 4: Jalankan Locust Load Tester
```bash
cd /home/vcc1/uji-venv
source env-locust/bin/activate
locust -f locustfile.py --web-host 0.0.0.0 --web-port 8089 --host http://localhost:8000
```

---

## 6. Cara Melakukan Stress Test (Uji Beban)

### A. Melalui Panel Web UI FastAPI
1. Buka browser: `http://<IP_EC2>:8000/`.
2. Klik tombol hijau **"Jalankan Komputasi Berat"**.
3. Browser akan menerima respon JSON berisi jumlah bilangan prima yang berhasil ditemukan:
   ```json
   {
     "status": "Selesai",
     "total_prima": 2262,
     "pesan": "CPU EC2 Anda baru saja disiksa!"
   }
   ```

### B. Melalui Locust Load Testing (Beban Tinggi)
1. Buka browser: `http://<IP_EC2>:8089/`.
2. Masukkan parameter pengujian:
   - **Number of users**: `50` (misal 50 pengguna virtual).
   - **Spawn rate**: `5` (menambah 5 user setiap detik).
   - **Host**: `http://localhost:8000` (atau biarkan default).
3. Klik **Start Swarming**.
4. Pantau grafik RPS (*Requests Per Second*), Failure Rate, dan Response Time di panel Locust.

### C. Melalui Dashboard Streamlit (Uji Memori RAM)
1. Buka browser: `http://<IP_EC2>:8501/`.
2. Halaman akan menampilkan spinner *"Memuat 100.000 vektor fitur ke dalam memori..."*.
3. Perhatikan lonjakan pemakaian RAM di Glances saat data dimuat dan dirender ke grafik.

### D. Melalui Perintah Terminal (cURL)
Jika ingin melakukan pengujian cepat tanpa browser:
```bash
# Menjalankan 1 kali request komputasi berat
curl -s http://127.0.0.1:8000/berat

# Menjalankan 10 request beruntun untuk membebani CPU
for i in {1..10}; do curl -s http://127.0.0.1:8000/berat > /dev/null && echo "Request #$i Selesai"; done
```

---

## 7. Cara Memantau Pemakaian Resource (Monitoring)

1. **Via Glances Web UI:**
   Akses `http://<IP_EC2>:61208/` pada browser Anda untuk melihat grafik CPU, RAM, dan daftar proses.
2. **Via Monitor Real-time Khusus:**
   Gunakan alat pemantau performa yang ada di folder tetangga:
   ```bash
   python3 /home/vcc1/monitor-performa/monitor.py
   ```

---

## 8. Cara Menghentikan Seluruh Layanan

Jika dijalankan menggunakan `./start_all.sh`:
```bash
cd /home/vcc1/uji-venv
./stop_all.sh
```

Jika dijalankan manual di terminal latar belakang, matikan proses menggunakan:
```bash
killall glances uvicorn streamlit locust python3
```

---

## 9. Catatan Penting & Troubleshooting

1. **Error `Address already in use`:**
   - Terjadi jika port 8000, 8501, 8089, atau 61208 masih digunakan oleh proses lama.
   - Solusi: Jalankan `./stop_all.sh` atau perintah `fuser -k <PORT>/tcp`.
2. **Batas Memori EC2 (RAM 2 GB):**
   - Instance t2/t3.small memiliki batas memori 2 GB.
   - Jangan menjalankan load test Locust dengan lebih dari 200 pengguna virtual sekaligus agar server tidak mengalami *Kernel Out-of-Memory (OOM) Panic*.
3. **Perbandingan dengan `uji-global-env`:**
   - Program di `uji-venv` berjalan pada port **8000, 8501, 8089, 61208**.
   - Program di `uji-global-env` berjalan pada port **8001, 8502, 8090, 61209**.
   - Kedua direktori dapat dijalankan bersamaan untuk eksperimen komparasi langsung.
