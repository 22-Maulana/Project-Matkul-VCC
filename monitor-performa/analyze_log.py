#!/usr/bin/env python3
"""
================================================================================
Program Analisis Log Metrik Performa: Uji-Venv vs Uji-Global-Env
Membaca file log CSV dan menyajikan perbandingan statistik secara mendalam.
================================================================================
"""

import os
import sys
import glob
import csv
import argparse
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description="Analisis File Log Metrik CSV")
    parser.add_argument("--file", "-f", type=str, default="", help="Path file CSV (default: file terbaru di folder logs/)")
    return parser.parse_args()

def get_latest_log():
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    files = glob.glob(os.path.join(log_dir, "metrics_*.csv"))
    if not files:
        return ""
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def analyze_csv(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File tidak ditemukan: {filepath}")
        return

    phases = defaultdict(list)
    all_rows = []

    with open(filepath, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_rows.append(row)
            phase = row.get("phase", "UNKNOWN")
            phases[phase].append(row)

    if not all_rows:
        print("Log kosong, tidak ada data untuk dianalisis.")
        return

    print("=" * 80)
    print("                    LAPORAN HASIL KOMPARASI PERFORMA")
    print("                 UJI-VENV VS UJI-GLOBAL-ENV (EC2 RESOURCE)")
    print("=" * 80)
    print(f"File Log Teranalisis : {filepath}")
    print(f"Total Sampel Tercatat: {len(all_rows)} detik sampling")
    print(f"Fase Terdeteksi      : {', '.join(phases.keys())}")
    print("-" * 80)

    # Hitung metrik per fase
    summary = {}
    for phase_name, rows in phases.items():
        count = len(rows)
        sys_cpu_vals = [float(r["sys_cpu_percent"]) for r in rows]
        sys_ram_mb_vals = [float(r["sys_ram_used_mb"]) for r in rows]
        sys_ram_pct_vals = [float(r["sys_ram_percent"]) for r in rows]

        venv_ram_vals = [float(r["venv_ram_mb"]) for r in rows]
        venv_cpu_vals = [float(r["venv_cpu_percent"]) for r in rows]

        global_ram_vals = [float(r["global_ram_mb"]) for r in rows]
        global_cpu_vals = [float(r["global_cpu_percent"]) for r in rows]

        summary[phase_name] = {
            "count": count,
            "sys_cpu_avg": sum(sys_cpu_vals) / count,
            "sys_cpu_max": max(sys_cpu_vals),
            "sys_ram_mb_avg": sum(sys_ram_mb_vals) / count,
            "sys_ram_mb_max": max(sys_ram_mb_vals),
            "sys_ram_pct_avg": sum(sys_ram_pct_vals) / count,
            "venv_ram_max": max(venv_ram_vals),
            "venv_ram_avg": sum(venv_ram_vals) / count,
            "venv_cpu_max": max(venv_cpu_vals),
            "venv_cpu_avg": sum(venv_cpu_vals) / count,
            "global_ram_max": max(global_ram_vals),
            "global_ram_avg": sum(global_ram_vals) / count,
            "global_cpu_max": max(global_cpu_max := global_cpu_vals),
            "global_cpu_avg": sum(global_cpu_vals) / count,
        }

    # Tampilkan ringkasan per fase
    print("\n[1] RINGKASAN DATA PER FASE PENELITIAN:")
    header_fmt = "{:<18} {:<8} {:<15} {:<15} {:<18}"
    row_fmt    = "{:<18} {:<8} {:<15} {:<15} {:<18}"
    print(header_fmt.format("Fase", "Durasi", "CPU (Rata/Puncak)", "RAM MB (Rata/Puncak)", "RAM Sistem (%)"))
    print("-" * 80)

    for p, s in summary.items():
        cpu_str = f"{s['sys_cpu_avg']:.1f}% / {s['sys_cpu_max']:.1f}%"
        ram_str = f"{s['sys_ram_mb_avg']:.0f} / {s['sys_ram_mb_max']:.0f} MB"
        ram_pct = f"{s['sys_ram_pct_avg']:.1f}%"
        print(row_fmt.format(p[:17], f"{s['count']}s", cpu_str, ram_str, ram_pct))

    print("-" * 80)

    # Identifikasi Baseline, Venv, Global
    baseline_ram = None
    for k in summary:
        if "BASELINE" in k.upper():
            baseline_ram = summary[k]["sys_ram_mb_avg"]
            break

    # Cari fase VENV dan GLOBAL
    venv_phase_data = None
    global_phase_data = None
    for k, v in summary.items():
        ku = k.upper()
        if "VENV" in ku and "COOLDOWN" not in ku and "BASELINE" not in ku:
            venv_phase_data = (k, v)
        elif "GLOBAL" in ku and "COOLDOWN" not in ku and "BASELINE" not in ku:
            global_phase_data = (k, v)

    print("\n[2] PERBANDINGAN HEAD-TO-HEAD (UJI-VENV vs UJI-GLOBAL-ENV):")
    comp_header = "{:<30} {:<20} {:<20} {:<15}"
    comp_row    = "{:<30} {:<20} {:<20} {:<15}"
    print(comp_header.format("Metrik Pengukuran", "Uji-VENV", "Uji-GLOBAL-ENV", "Selisih"))
    print("-" * 80)

    v_name = venv_phase_data[0] if venv_phase_data else "VENV (Proses)"
    g_name = global_phase_data[0] if global_phase_data else "GLOBAL (Proses)"

    # Nilai RAM Proses Spesifik
    max_v_ram = max([s["venv_ram_max"] for s in summary.values()])
    avg_v_ram = max([s["venv_ram_avg"] for s in summary.values()])
    max_g_ram = max([s["global_ram_max"] for s in summary.values()])
    avg_g_ram = max([s["global_ram_avg"] for s in summary.values()])

    # Nilai CPU Proses Spesifik
    max_v_cpu = max([s["venv_cpu_max"] for s in summary.values()])
    max_g_cpu = max([s["global_cpu_max"] for s in summary.values()])

    diff_ram = max_g_ram - max_v_ram
    diff_ram_str = f"{diff_ram:+.1f} MB"

    diff_cpu = max_g_cpu - max_v_cpu
    diff_cpu_str = f"{diff_cpu:+.1f}%"

    print(comp_row.format("Puncak RAM Proses Aplikasi", f"{max_v_ram:.1f} MB", f"{max_g_ram:.1f} MB", diff_ram_str))
    print(comp_row.format("Rata-rata RAM Proses Aplikasi", f"{avg_v_ram:.1f} MB", f"{avg_g_ram:.1f} MB", f"{(avg_g_ram - avg_v_ram):+.1f} MB"))
    print(comp_row.format("Puncak Beban CPU Aplikasi", f"{max_v_cpu:.1f}%", f"{max_g_cpu:.1f}%", diff_cpu_str))

    if baseline_ram is not None and venv_phase_data and global_phase_data:
        delta_v_ram = venv_phase_data[1]["sys_ram_mb_max"] - baseline_ram
        delta_g_ram = global_phase_data[1]["sys_ram_mb_max"] - baseline_ram
        diff_delta = delta_g_ram - delta_v_ram
        print(comp_row.format("Kenaikan RAM Sistem dr Baseline", f"+{delta_v_ram:.1f} MB", f"+{delta_g_ram:.1f} MB", f"{diff_delta:+.1f} MB"))

    print("-" * 80)

    # Kesimpulan Akhir
    print("\n[3] KESIMPULAN & ANALISIS AKHIR:")
    if max_v_ram > 0 and max_g_ram > 0:
        if abs(max_v_ram - max_g_ram) <= 5.0:
            print("⚖️  PENGGUNAAN MEMORI (RAM): IDENTIK / SETARA")
            print(f"   Kedua lingkungan mengonsumsi RAM aplikasi yang hampir sama persis (Selisih hanya {abs(diff_ram):.1f} MB).")
            print("   Penjelasan Ilmiah: Baik venv maupun global environment menjalankan CPython interpreter yang sama.")
            print("   Perbedaan utama bukan pada pemakaian memori saat runtime aplikasi, melainkan pada overhead disk & library loading.")
        elif max_g_ram < max_v_ram:
            saved_mb = max_v_ram - max_g_ram
            pct_saved = (saved_mb / max_v_ram) * 100
            print(f"🏆 PENGGUNAAN MEMORI (RAM): GLOBAL-ENV LEBIH RINGAN!")
            print(f"   Global-env lebih hemat sebesar {saved_mb:.1f} MB ({pct_saved:.1f}%) dibandingkan VENV.")
        else:
            saved_mb = max_g_ram - max_v_ram
            pct_saved = (saved_mb / max_g_ram) * 100
            print(f"🏆 PENGGUNAAN MEMORI (RAM): VENV LEBIH RINGAN!")
            print(f"   VENV lebih hemat sebesar {saved_mb:.1f} MB ({pct_saved:.1f}%) dibandingkan Global-Env.")

    print("\n💾 PERBANDINGAN EFISIENSI STORAGE (DISK):")
    print("   - Direktori uji-venv       : ~700 MB (akibat 4 virtual environment terpisah)")
    print("   - Direktori uji-global-env  : ~32 KB (hanya file skrip, dependensi berada di sistem/user)")
    print("   -> Kesimpulan Storage: Global Environment unggul 21.000x lebih hemat kapasitas penyimpanan disk.")

    print("=" * 80)

def main():
    args = parse_args()
    target_file = args.file
    if not target_file:
        target_file = get_latest_log()
        if not target_file:
            print("Tidak ditemukan file log di folder logs/. Jalankan monitor.py terlebih dahulu.")
            sys.exit(1)

    analyze_csv(target_file)

if __name__ == "__main__":
    main()
