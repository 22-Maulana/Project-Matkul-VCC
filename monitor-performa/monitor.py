#!/usr/bin/env python3
"""
================================================================================
Program Monitoring Real-time RAM & CPU + Logger Ber-Timestamp
Dirancang untuk Pengujian Komparasi: uji-venv vs uji-global-env
================================================================================
"""

import os
import sys
import time
import signal
import argparse
import csv
from datetime import datetime
import psutil

# File tag default untuk mengubah fase secara dinamis antar-proses
DEFAULT_TAG_FILE = "/tmp/benchmark_phase.tag"

def parse_args():
    parser = argparse.ArgumentParser(description="Real-time CPU & RAM Monitor dengan CSV Logger")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval sampling dalam detik (default: 1.0)")
    parser.add_argument("--output", type=str, default="", help="Path file CSV output (default: logs/metrics_TIMESTAMP.csv)")
    parser.add_argument("--phase", type=str, default="BASELINE", help="Label fase awal (default: BASELINE)")
    parser.add_argument("--tag-file", type=str, default=DEFAULT_TAG_FILE, help="Path file indikator fase eksternal")
    parser.add_argument("--duration", type=int, default=0, help="Durasi otomatis dalam detik (0 = berjalan terus)")
    parser.add_argument("--quiet", action="store_true", help="Jangan tampilkan UI terminal (khusus background)")
    return parser.parse_args()

def get_current_phase(default_phase, tag_file):
    """Membaca fase aktif dari file tag jika tersedia, atau gunakan nilai default."""
    if os.path.exists(tag_file):
        try:
            with open(tag_file, "r") as f:
                tag = f.read().strip()
                if tag:
                    return tag
        except Exception:
            pass
    return default_phase

def get_process_metrics(my_pid):
    """
    Memindai dan mengelompokkan penggunaan CPU & RAM untuk proses-proses
    yang berasal dari 'uji-venv' dan 'uji-global-env'.
    """
    venv_metrics = {"count": 0, "cpu": 0.0, "ram_mb": 0.0}
    global_metrics = {"count": 0, "cpu": 0.0, "ram_mb": 0.0}

    for p in psutil.process_iter(['pid', 'cmdline', 'cwd', 'cpu_percent', 'memory_info']):
        try:
            pid = p.info['pid']
            if pid == my_pid:
                continue

            cmdline = " ".join(p.info['cmdline'] or [])
            cwd = p.info['cwd'] or ""

            # Abaikan jika ini skrip monitoring itu sendiri
            if "monitor.py" in cmdline:
                continue

            mem_mb = (p.info['memory_info'].rss / (1024 * 1024)) if p.info['memory_info'] else 0.0
            cpu_pct = p.info['cpu_percent'] or 0.0

            is_venv = ("uji-venv" in cmdline or "uji-venv" in cwd or "env-fastapi" in cmdline or "env-streamlit" in cmdline or "env-locust" in cmdline or "env-glances" in cmdline)
            is_global = ("uji-global-env" in cmdline or "uji-global-env" in cwd or ":8001" in cmdline or ":8502" in cmdline or ":8090" in cmdline or ":61209" in cmdline)

            if is_venv and not is_global:
                venv_metrics["count"] += 1
                venv_metrics["cpu"] += cpu_pct
                venv_metrics["ram_mb"] += mem_mb
            elif is_global and not is_venv:
                global_metrics["count"] += 1
                global_metrics["cpu"] += cpu_pct
                global_metrics["ram_mb"] += mem_mb

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return venv_metrics, global_metrics

def make_bar(percent, length=20):
    """Membuat visual progress bar sederhana."""
    filled = int(length * min(max(percent, 0), 100) / 100)
    bar = "█" * filled + "░" * (length - filled)
    return bar

def main():
    args = parse_args()
    my_pid = os.getpid()

    # Siapkan folder log
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    if not args.output:
        start_ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = os.path.join(log_dir, f"metrics_{start_ts_str}.csv")
    else:
        csv_file = args.output

    # Inisialisasi file tag
    with open(args.tag_file, "w") as f:
        f.write(args.phase)

    # Inisialisasi CPU psutil
    psutil.cpu_percent(interval=None)

    # Siapkan file CSV
    fieldnames = [
        "timestamp",
        "epoch",
        "phase",
        "sys_cpu_percent",
        "sys_ram_used_mb",
        "sys_ram_total_mb",
        "sys_ram_percent",
        "sys_ram_available_mb",
        "venv_proc_count",
        "venv_cpu_percent",
        "venv_ram_mb",
        "global_proc_count",
        "global_cpu_percent",
        "global_ram_mb"
    ]

    write_header = not os.path.exists(csv_file)
    f_csv = open(csv_file, "a", newline="", buffering=1)
    writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
    if write_header:
        writer.writeheader()

    running = True
    def signal_handler(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    start_time = time.time()
    total_samples = 0

    if not args.quiet:
        print("\033[2J\033[H", end="") # Bersihkan layar

    try:
        while running:
            loop_start = time.time()
            now = datetime.now()
            ts_str = now.strftime("%Y-%m-%d %H:%M:%S")
            epoch = loop_start

            # Ambil data sistem
            sys_cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            sys_ram_used_mb = mem.used / (1024 * 1024)
            sys_ram_total_mb = mem.total / (1024 * 1024)
            sys_ram_avail_mb = mem.available / (1024 * 1024)
            sys_ram_pct = mem.percent

            # Ambil fase terkini
            current_phase = get_current_phase(args.phase, args.tag_file)

            # Ambil metrik spesifik aplikasi
            venv_m, global_m = get_process_metrics(my_pid)

            # Catat ke CSV
            row = {
                "timestamp": ts_str,
                "epoch": f"{epoch:.3f}",
                "phase": current_phase,
                "sys_cpu_percent": f"{sys_cpu:.1f}",
                "sys_ram_used_mb": f"{sys_ram_used_mb:.1f}",
                "sys_ram_total_mb": f"{sys_ram_total_mb:.1f}",
                "sys_ram_percent": f"{sys_ram_pct:.1f}",
                "sys_ram_available_mb": f"{sys_ram_avail_mb:.1f}",
                "venv_proc_count": venv_m["count"],
                "venv_cpu_percent": f"{venv_m['cpu']:.1f}",
                "venv_ram_mb": f"{venv_m['ram_mb']:.1f}",
                "global_proc_count": global_m["count"],
                "global_cpu_percent": f"{global_m['cpu']:.1f}",
                "global_ram_mb": f"{global_m['ram_mb']:.1f}"
            }
            writer.writerow(row)
            total_samples += 1

            # Render ke terminal
            if not args.quiet:
                cpu_bar = make_bar(sys_cpu, 20)
                ram_bar = make_bar(sys_ram_pct, 20)

                output_lines = [
                    "\033[H", # Gerakkan kursor ke posisi awal (0,0)
                    "================================================================================",
                    f"       🔴 MONITORING REALTIME RESOURCE EC2: VENV VS GLOBAL-ENV",
                    "================================================================================",
                    f" Waktu          : {ts_str} (Sampel ke: {total_samples})",
                    f" Fase Pengujian : \033[1;33m[{current_phase}]\033[0m",
                    f" File Log CSV   : {csv_file}",
                    "--------------------------------------------------------------------------------",
                    f" Total Sistem CPU  : [{cpu_bar}] {sys_cpu:5.1f}%",
                    f" Total Sistem RAM  : [{ram_bar}] {sys_ram_used_mb:6.1f} MB / {sys_ram_total_mb:.0f} MB ({sys_ram_pct:4.1f}%)",
                    f" Sisa RAM Tersedia : {sys_ram_avail_mb:6.1f} MB",
                    "--------------------------------------------------------------------------------",
                    " RINCIAN PER KELOMPOK PROGRAM:",
                    f" 🔹 UJI-VENV       : {venv_m['count']:2d} proses | CPU: {venv_m['cpu']:5.1f}% | RAM: {venv_m['ram_mb']:6.1f} MB",
                    f" 🔸 UJI-GLOBAL-ENV : {global_m['count']:2d} proses | CPU: {global_m['cpu']:5.1f}% | RAM: {global_m['ram_mb']:6.1f} MB",
                    "================================================================================",
                    " Tips:",
                    f" - Ubah fase dinamis: echo 'NAMA_FASE' > {args.tag_file}",
                    " - Tekan [Ctrl+C] untuk berhenti & generate laporan perbandingan.",
                    "================================================================================"
                ]
                print("\n".join(output_lines), flush=True)

            # Cek batasan durasi
            if args.duration > 0 and (time.time() - start_time) >= args.duration:
                break

            # Sleep terukur
            elapsed = time.time() - loop_start
            sleep_time = max(0.05, args.interval - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        pass
    finally:
        f_csv.close()
        if not args.quiet:
            print("\n\n[✓] Monitoring selesai dihentikan.")
            print(f"[✓] Data tersimpan di: {csv_file}")
            print(f"[✓] Menjalankan ringkasan analisis...")

if __name__ == "__main__":
    main()
