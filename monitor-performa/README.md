# Suite Monitoring & Benchmark Performa: Uji-Venv vs Uji-Global-Env

Suite program ini dirancang untuk memantau penggunaan RAM dan CPU secara **real-time**, merekam log lengkap dengan timestamp berpresisi tinggi, serta menyajikan analisis statistik perbandingan untuk menentukan apakah **Python Global Environment** atau **Virtual Environment (`venv`)** yang lebih ringan di server EC2.

---

## 1. Komponen Program

1. **`monitor.py`** (Real-time Monitor & CSV Logger):
   - Menampilkan visualisasi utilisasi CPU dan RAM secara real-time di terminal (lengkap dengan progress bar).
   - Membedakan proses `uji-venv` vs `uji-global-env` secara otomatis.
   - Menyimpan seluruh sampel data ke dalam file CSV di folder `logs/` dengan rincian kolom:
     * `timestamp` (`YYYY-MM-DD HH:MM:SS`) & `epoch`
     * `phase` (Fase eksperimen: `BASELINE`, `RUN_VENV`, `RUN_GLOBAL`, dll.)
     * `sys_cpu_percent`, `sys_ram_used_mb`, `sys_ram_percent`, `sys_ram_available_mb`
     * `venv_proc_count`, `venv_cpu_percent`, `venv_ram_mb`
     * `global_proc_count`, `global_cpu_percent`, `global_ram_mb`

2. **`analyze_log.py`** (Generator Laporan & Komparator):
   - Membaca file CSV hasil monitoring.
   - Mengelompokkan data berdasarkan fase eksperimen.
   - Menghitung statistik Rata-rata (*Average*), Nilai Puncak (*Peak/Max*), dan Kenaikan RAM dari Baseline (*Delta RAM*).
   - Menghasilkan tabel perbandingan head-to-head dan kesimpulan ilmiah mengenai lingkungan mana yang lebih ringan.

3. **`run_benchmark.py`** (Automated Benchmark Runner):
   - Menjalankan seluruh alur eksperimen secara otomatis:
     1. Merekam Baseline RAM & CPU sebelum pengujian (10 detik).
     2. Menjalankan layanan `uji-venv` dan memberikan beban kerja (CPU stress di `/berat` & RAM stress di Streamlit).
     3. Menghentikan `uji-venv` dan menunggu masa pemulihan (cooldown 10 detik).
     4. Menjalankan layanan `uji-global-env` dan memberikan beban kerja yang identik.
     5. Menghentikan `uji-global-env` dan menunggu masa pemulihan akhir.
     6. Menghentikan monitor dan langsung mencetak laporan komparasi.

---

## 2. Cara Penggunaan

### A. Pengujian Otomatis (Direkomendasikan)
Cukup jalankan satu perintah:
```bash
python3 /home/vcc1/monitor-performa/run_benchmark.py
```

### B. Pengujian Manual / Interaktif
1. Jalankan monitor di satu terminal:
   ```bash
   python3 /home/vcc1/monitor-performa/monitor.py
   ```
2. Di terminal lain, ubah label fase pengujian saat Anda beralih tahap:
   ```bash
   # Contoh mengubah fase:
   echo "RUN_VENV" > /tmp/benchmark_phase.tag
   # (Jalankan uji-venv Anda)

   echo "COOLDOWN" > /tmp/benchmark_phase.tag
   # (Hentikan uji-venv)

   echo "RUN_GLOBAL" > /tmp/benchmark_phase.tag
   # (Jalankan uji-global-env Anda)
   ```
3. Tekan `Ctrl+C` pada `monitor.py` untuk mengakhiri.
4. Jalankan analisis terhadap file log yang dihasilkan:
   ```bash
   python3 /home/vcc1/monitor-performa/analyze_log.py
   ```
