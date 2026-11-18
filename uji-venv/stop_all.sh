#!/usr/bin/env bash
# ==============================================================================
# Script Menghentikan Layanan di uji-venv
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

echo "=== Menghentikan Layanan Python (uji-venv) ==="

for app in glances fastapi streamlit locust; do
    pid_file="$DIR/$app.pid"
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "[-] Menghentikan $app (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 0.5
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null || true
            fi
        else
            echo "[!] PID $pid ($app) sudah tidak aktif."
        fi
        rm -f "$pid_file"
    fi
done

# Fallback: periksa port 61208, 8000, 8501, 8089
for port in 61208 8000 8501 8089; do
    pids=$(ss -tulpn "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | cut -d= -f2)
    for p in $pids; do
        if [ -n "$p" ]; then
            echo "[-] Menghentikan proses sisa di port $port (PID: $p)..."
            kill -9 "$p" 2>/dev/null || true
        fi
    done
done

echo "[v] Seluruh layanan uji-venv telah dihentikan."
