#!/usr/bin/env bash
# ==============================================================================
# Script Menjalankan Semua Layanan di uji-venv Menggunakan Virtual Environment
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=== Menjalankan Layanan Python (Virtual Environment) ==="

# 1. Glances Monitoring (env-glances)
setsid -f "$DIR/env-glances/bin/glances" -w -p 61208 > "$DIR/glances.log" 2>&1
sleep 1
pid_glances=$(ss -tulpn "sport = :61208" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
echo "$pid_glances" > "$DIR/glances.pid"
echo "[+] [env-glances]   Glances Web UI berjalan di http://0.0.0.0:61208 (PID: $pid_glances)"

# 2. FastAPI Backend & CPU Stress (env-fastapi)
setsid -f "$DIR/env-fastapi/bin/uvicorn" api:app --host 0.0.0.0 --port 8000 --app-dir "$DIR" > "$DIR/fastapi.log" 2>&1
sleep 1
pid_fastapi=$(ss -tulpn "sport = :8000" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
echo "$pid_fastapi" > "$DIR/fastapi.pid"
echo "[+] [env-fastapi]   FastAPI berjalan di http://0.0.0.0:8000 (PID: $pid_fastapi)"

# 3. Streamlit RAM Stress (env-streamlit)
setsid -f "$DIR/env-streamlit/bin/streamlit" run "$DIR/dashboard.py" --server.port 8501 --server.address 0.0.0.0 --server.headless true > "$DIR/streamlit.log" 2>&1
sleep 2
pid_streamlit=$(ss -tulpn "sport = :8501" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
echo "$pid_streamlit" > "$DIR/streamlit.pid"
echo "[+] [env-streamlit] Streamlit berjalan di http://0.0.0.0:8501 (PID: $pid_streamlit)"

# 4. Locust Load Testing (env-locust)
setsid -f "$DIR/env-locust/bin/locust" -f "$DIR/locustfile.py" --web-host 0.0.0.0 --web-port 8089 --host http://localhost:8000 < /dev/null > "$DIR/locust.log" 2>&1
sleep 1
pid_locust=$(ss -tulpn "sport = :8089" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
echo "$pid_locust" > "$DIR/locust.pid"
echo "[+] [env-locust]    Locust Web UI berjalan di http://0.0.0.0:8089 (Target: http://localhost:8000) (PID: $pid_locust)"

echo "=========================================================="
echo "Semua layanan venv berhasil dijalankan di background."
echo "Gunakan ./status.sh untuk memeriksa status proses."
echo "Gunakan ./stop_all.sh untuk menghentikan seluruh layanan."
