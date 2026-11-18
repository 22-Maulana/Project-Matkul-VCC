# Panduan Eksperimen: Python Global Environment vs Virtual Environment (Venv)

Folder ini (`/home/vcc1/uji-global-env`) berisi implementasi program yang sama persis dengan yang ada di `uji-venv`, tetapi dikonfigurasi dan dijalankan menggunakan **Python Global Environment**.

---

## 1. Perbandingan Alokasi Port

Agar eksperimen perbandingan performa antara `uji-venv` dan `uji-global-env` dapat berjalan bersamaan (simultan) tanpa terjadi *port conflict* (`Address already in use`), port telah dipetakan sebagai berikut:

| Layanan / Program | Port `uji-venv` | Port `uji-global-env` | Endpoint / Keterangan |
| :--- | :---: | :---: | :--- |
| **FastAPI** (`api.py`) | `8000` | `8001` | `http://<IP>:8001/` & `http://<IP>:8001/berat` |
| **Streamlit** (`dashboard.py`) | `8501` | `8502` | `http://<IP>:8502/` (AI Vector Simulator) |
| **Locust** (`locustfile.py`) | `8089` | `8090` | `http://<IP>:8090/` (Target test: `http://localhost:8001`) |
| **Glances** (Monitoring) | `61208` | `61209` | `http://<IP>:61209/` (System Dashboard) |

---

## 2. Cara Menjalankan Layanan

### A. Menggunakan Helper Script (Otomatis di Background)

- **Menjalankan semua layanan:**
  ```bash
  cd ~/uji-global-env
  ./start_all.sh
  ```
- **Memeriksa status proses & port:**
  ```bash
  ./status.sh
  ```
- **Menghentikan semua layanan:**
  ```bash
  ./stop_all.sh
  ```

### B. Menjalankan Manual per Layanan (Foreground)

Karena menggunakan **Global Environment**, Anda tidak perlu melakukan `source env-xxx/bin/activate`:

1. **FastAPI**:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8001
   ```
2. **Streamlit**:
   ```bash
   streamlit run dashboard.py --server.port 8502 --server.address 0.0.0.0
   ```
3. **Locust**:
   ```bash
   locust -f locustfile.py --web-host 0.0.0.0 --web-port 8090 --host http://localhost:8001
   ```
4. **Glances**:
   ```bash
   glances -w -p 61209
   ```

---

## 3. Poin-Poin Analisis Komparasi (Venv vs Global Env)

| Aspek | Virtual Environment (`uji-venv`) | Global Environment (`uji-global-env`) |
| :--- | :--- | :--- |
| **Ukuran Disk** | **~700 MB** (ada 4 venv terpisah) | **~16 KB** (hanya file skrip, dependensi di global) |
| **Isolasi Modul** | Sangat terisolasi antar aplikasi | Berbagi pustaka (`site-packages` terpusat) |
| **Startup / Aktivasi** | Memerlukan aktivasi (`source .../bin/activate`) | Langsung dieksekusi via `python3` / binary global |
| **Risiko Konflik Versi** | Sangat Rendah | Berpotensi terjadi konflik jika 2 aplikasi butuh versi dependensi berbeda |
| **Overhead CPU / RAM** | Performa eksekusi Python runtime identik, namun overhead manajemen proses berbeda |
