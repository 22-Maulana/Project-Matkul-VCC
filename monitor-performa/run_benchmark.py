#!/usr/bin/env python3
"""
================================================================================
Orchestrator Pengujian Otomatis Komparasi Performa:
uji-venv VS uji-global-env
================================================================================
Alur:
1. Bersihkan proses latar belakang lama.
2. Jalankan monitor.py.
3. Rekam BASELINE IDLE (10 detik) - kondisi sebelum run.
4. Jalankan UJI-VENV (30 detik) + simulasi beban CPU & RAM.
5. Hentikan UJI-VENV, jeda COOLDOWN (10 detik).
6. Jalankan UJI-GLOBAL-ENV (30 detik) + simulasi beban yang sama persis.
7. Hentikan UJI-GLOBAL-ENV, jeda FINAL COOLDOWN (10 detik).
8. Hentikan monitor.py dan tampilkan analisis lengkap.
================================================================================
"""

import os
import sys
import time
import subprocess
import signal
import requests
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(DIR, "logs")
TAG_FILE = "/tmp/benchmark_phase.tag"

def set_phase(phase_name):
    print(f"\n>>> [FASE]: \033[1;32m{phase_name}\033[0m <<<")
    with open(TAG_FILE, "w") as f:
        f.write(phase_name)

def kill_leftovers():
    print("[*] Membersihkan proses Python lama jika ada...")
    subprocess.run(["pkill", "-9", "-f", "uvicorn"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-9", "-f", "streamlit"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-9", "-f", "locust"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-9", "-f", "glances"], stderr=subprocess.DEVNULL)
    time.sleep(2)

def hit_api_workload(port, iterations=5):
    """Kirim beban komputasi berat ke endpoint /berat dan akses dashboard."""
    # Trigger Streamlit memory allocation
    streamlit_port = 8501 if port == 8000 else 8502
    try:
        requests.get(f"http://127.0.0.1:{streamlit_port}/", timeout=3)
    except Exception:
        pass

    # Trigger CPU stress pada FastAPI
    for i in range(iterations):
        try:
            res = requests.get(f"http://127.0.0.1:{port}/berat", timeout=10)
            if res.status_code == 200:
                print(f"    [Load] Request #{i+1} ke port {port}/berat sukses (CPU disiksa)")
        except Exception as e:
            print(f"    [Load Error]: {e}")
        time.sleep(1)

def main():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_output = os.path.join(LOGS_DIR, f"metrics_benchmark_{ts_now}.csv")

    kill_leftovers()

    # 1. Mulai Monitoring
    print(f"[*] Menjalankan monitor.py di background (Output: {csv_output})...")
    monitor_proc = subprocess.Popen([
        sys.executable,
        os.path.join(DIR, "monitor.py"),
        "--output", csv_output,
        "--tag-file", TAG_FILE,
        "--phase", "1_BASELINE_IDLE",
        "--quiet"
    ])

    try:
        # FASE 1: BASELINE IDLE (Sebelum run program apapun)
        set_phase("1_BASELINE_IDLE")
        print("[+] Merekam baseline sistem tanpa beban selama 10 detik...")
        time.sleep(10)

        # FASE 2: RUN UJI-VENV
        set_phase("2_RUN_VENV")
        print("[+] Memulai layanan uji-venv (FastAPI: 8000, Streamlit: 8501, Glances: 61208)...")
        p_v_api = subprocess.Popen(["/home/vcc1/uji-venv/env-fastapi/bin/uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
                                   cwd="/home/vcc1/uji-venv", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p_v_st = subprocess.Popen(["/home/vcc1/uji-venv/env-streamlit/bin/streamlit", "run", "dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.headless", "true"],
                                  cwd="/home/vcc1/uji-venv", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p_v_gl = subprocess.Popen(["/home/vcc1/uji-venv/env-glances/bin/glances", "-w", "-p", "61208"],
                                  cwd="/home/vcc1/uji-venv", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("[+] Menunggu 5 detik agar semua layanan venv siap...")
        time.sleep(5)

        print("[+] Mengirimkan simulasi beban kerja ke uji-venv...")
        hit_api_workload(8000, iterations=8)
        time.sleep(5)

        print("[+] Menghentikan layanan uji-venv...")
        for p in [p_v_api, p_v_st, p_v_gl]:
            p.terminate()
            try:
                p.wait(timeout=2)
            except Exception:
                p.kill()
        kill_leftovers()

        # FASE 3: COOLDOWN VENV
        set_phase("3_COOLDOWN_VENV")
        print("[+] Masa pemulihan memori (cooldown) setelah venv selama 10 detik...")
        time.sleep(10)

        # FASE 4: RUN UJI-GLOBAL-ENV
        set_phase("4_RUN_GLOBAL_ENV")
        print("[+] Memulai layanan uji-global-env (FastAPI: 8001, Streamlit: 8502, Glances: 61209)...")
        p_g_api = subprocess.Popen(["python3", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"],
                                   cwd="/home/vcc1/uji-global-env", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p_g_st = subprocess.Popen(["python3", "-m", "streamlit", "run", "dashboard.py", "--server.port", "8502", "--server.address", "0.0.0.0", "--server.headless", "true"],
                                  cwd="/home/vcc1/uji-global-env", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p_g_gl = subprocess.Popen(["python3", "-m", "glances", "-w", "-p", "61209"],
                                  cwd="/home/vcc1/uji-global-env", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("[+] Menunggu 5 detik agar semua layanan global siap...")
        time.sleep(5)

        print("[+] Mengirimkan simulasi beban kerja yang sama ke uji-global-env...")
        hit_api_workload(8001, iterations=8)
        time.sleep(5)

        print("[+] Menghentikan layanan uji-global-env...")
        for p in [p_g_api, p_g_st, p_g_gl]:
            p.terminate()
            try:
                p.wait(timeout=2)
            except Exception:
                p.kill()
        kill_leftovers()

        # FASE 5: FINAL COOLDOWN
        set_phase("5_FINAL_COOLDOWN")
        print("[+] Masa pemulihan akhir selama 10 detik...")
        time.sleep(10)

    finally:
        print("[*] Menghentikan monitor.py...")
        monitor_proc.send_signal(signal.SIGINT)
        try:
            monitor_proc.wait(timeout=3)
        except Exception:
            monitor_proc.kill()
        kill_leftovers()

    print("\n" + "=" * 80)
    print("        EKSPERIMEN OTOMATIS SELESAI! MENJALANKAN ANALISIS DATA...")
    print("=" * 80 + "\n")

    subprocess.run([sys.executable, os.path.join(DIR, "analyze_log.py"), "-f", csv_output])

if __name__ == "__main__":
    main()
