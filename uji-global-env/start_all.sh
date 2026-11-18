#!/usr/bin/env bash
# ==============================================================================
# Script Menjalankan Program Python Menggunakan Global Environment
# Port yang digunakan berbeda dengan port uji-venv agar dapat berjalan paralel
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Pastikan PATH mencakup bin lokal pengguna
export PATH="$HOME/.local/bin:$PATH"

echo "=== Menjalankan Layanan Python (Global Environment) ==="

# 1. FastAPI (Backend & API CPU Stress)
setsid -f python3 -m uvicorn api:app --host 0.0.0.0 --port 8001 --app-dir "$DIR" > "$DIR/fastapi.log" 2>&1
sleep 1
pid_fastapi=$(ss -tulpn "sport = :8001" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
echo "$pid_fastapi" > "$DIR/fastapi.pid"
echo "[+] FastAPI berjalan di http://0.0.0.0:8001 (PID: $pid_fastapi)"

# 2. Streamlit (AI Vector Simulator & RAM Stress)
setsid -f python3 -m streamlit run "$DIR/dashboard.py" --server.port 8502 --server.address 0.0.0.0 --server.headless true > "$DIR/streamlit.log" 2>&1
sleep 2
pid_streamlit=$(ss -tulpn "sport = :8502" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
echo "$pid_streamlit" > "$DIR/streamlit.pid"
echo "[+] Streamlit berjalan di http://0.0.0.0:8502 (PID: $pid_streamlit)"

# 3. Locust (Load Testing Tool)
setsid -f python3 -m locust -f "$DIR/locustfile.py" --web-host 0.0.0.0 --web-port 8090 --host http://localhost:8001 < /dev/null > "$DIR/locust.log" 2>&1
sleep 1
pid_locust=$(ss -tulpn "sport = :8090" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
echo "$pid_locust" > "$DIR/locust.pid"
echo "[+] Locust Web UI berjalan di http://0.0.0.0:8090 (Target: http://localhost:8001) (PID: $pid_locust)"

# 4. Glances (System Resource Monitoring)
setsid -f python3 -m glances -w -p 61209 > "$DIR/glances.log" 2>&1
sleep 1
pid_glances=$(ss -tulpn "sport = :61209" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
echo "$pid_glances" > "$DIR/glances.pid"
echo "[+] Glances Web UI berjalan di http://0.0.0.0:61209 (PID: $pid_glances)"

echo "=========================================================="
echo "Semua layanan global env berhasil dijalankan di background."
echo "Gunakan ./status.sh untuk memeriksa status proses."
echo "Gunakan ./stop_all.sh untuk menghentikan seluruh layanan."
