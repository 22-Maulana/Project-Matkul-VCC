#!/usr/bin/env bash
# ==============================================================================
# Script Menghentikan Layanan Python Global Environment
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

echo "=== Menghentikan Layanan Python (Global Environment) ==="

for app in fastapi streamlit locust glances; do
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

# Fallback: pastikan port 8001, 8502, 8090, 61209 bersih jika masih ada sisa proses
for port in 8001 8502 8090 61209; do
    pids=$(ss -tulpn "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | cut -d= -f2)
    for p in $pids; do
        if [ -n "$p" ]; then
            echo "[-] Menghentikan proses sisa di port $port (PID: $p)..."
            kill -9 "$p" 2>/dev/null || true
        fi
    done
done

echo "[v] Seluruh layanan global env telah dihentikan."
