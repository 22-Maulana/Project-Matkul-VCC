# Project-Matkul-VCC

Komparasi Performa & Analisis Sumber Daya Sistem: **Python Virtual Environment (`uji-venv`)** vs **Python Global Environment (`uji-global-env`)** pada AWS EC2.

Proyek ini mengevaluasi dampak pemilihan arsitektur *environment* Python terhadap utilisasi CPU, RAM, dan penyimpanan disk pada instance cloud AWS EC2 dengan berbagai beban kerja (*FastAPI*, *Streamlit*, *Locust*, dan *Glances*).

---

## Struktur Repositori

```text
.
├── dokumentasi.md          # Laporan komprehensif hasil pengujian dan analisis performa
├── README.md               # Ringkasan informasi repositori
├── requirements.txt        # Daftar dependensi pustaka Python
├── monitor-performa/       # Suite monitoring sistem & benchmark runner
│   ├── monitor.py          # Real-time metrics logger (CPU, RAM) ke CSV
│   ├── analyze_log.py      # Pengolah statistik data log metrik
│   ├── run_benchmark.py    # Skrip pengujian beban otomatis
│   ├── dokumentasi.md      # Salinan dokumentasi teknis
│   └── logs/               # Dataset metrik hasil benchmark (.csv)
├── uji-global-env/         # Pengujian menggunakan Python Global Environment
│   ├── api.py              # Backend REST API (FastAPI) & komputasi intensif CPU
│   ├── dashboard.py        # Dashboard analitik matriks AI (Streamlit)
│   ├── locustfile.py       # Skenario load testing HTTP (Locust)
│   ├── start_all.sh        # Skrip menjalankan seluruh daemon latar belakang
│   ├── status.sh           # Skrip pemantauan status proses
│   └── stop_all.sh         # Skrip penghentian seluruh daemon
├── uji-venv/               # Pengujian menggunakan Multi-Virtual Environment
│   ├── api.py              # Backend REST API (FastAPI)
│   ├── dashboard.py        # Dashboard analitik (Streamlit)
│   ├── locustfile.py       # Skenario load testing (Locust)
│   ├── start_all.sh        # Skrip menjalankan daemon dalam venv masing-masing
│   ├── status.sh           # Skrip pemantauan status proses
│   └── stop_all.sh         # Skrip penghentian seluruh daemon
└── uji-performa/           # Direktori baseline pengujian awal
    ├── api.py
    ├── dashboard.py
    └── locustfile.py
```

---

## Ringkasan Hasil Eksperimen

1. **Efisiensi RAM (Runtime Memory):**
   - **Virtual Environment (`uji-venv`) lebih hemat 31.4% RAM.**
   - Puncak penggunaan RAM pada `uji-venv` adalah **401.8 MB**, sedangkan pada `uji-global-env` mencapai **585.9 MB** (selisih penghematan 184.1 MB).
2. **Utilisasi CPU:**
   - Multi-core processing pada `uji-venv` mampu memanfaatkan alokasi 2 vCPU secara optimal (puncak 130.4% vs 119.2% pada global environment) tanpa hambatan *shared-library lock contention*.
3. **Efisiensi Penyimpanan Disk (Storage):**
   - **Global Environment jauh lebih hemat kapasitas disk.**
   - `uji-global-env` hanya membutuhkan ruang disk **~32 KB - 128 KB**, sedangkan `uji-venv` memakan **~700 MB** akibat isolasi pustaka pada 4 lingkungan terpisah.

Detail lengkap pengujian, metodologi, dan grafik komparasi dapat dilihat di [dokumentasi.md](dokumentasi.md).

---

## Instalasi Dependensi

Untuk mereplikasi lingkungan pengujian:

```bash
pip install -r requirements.txt
```

Atau menggunakan virtual environment terisolasi:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
