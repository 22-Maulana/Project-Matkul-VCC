#!/usr/bin/env bash
# ==============================================================================
# Script Memeriksa Status Layanan VENV vs GLOBAL ENV
# ==============================================================================

echo "=========================================================="
echo "          STATUS PORT & SERVICE PYTHON EXPERIMENT         "
echo "=========================================================="

echo ""
echo "--- [1] Port Uji-VENV (Default / Asli) ---"
printf "%-15s %-10s %-15s %-10s\n" "Layanan" "Port" "Status" "PID"
for svc_info in "FastAPI:8000" "Streamlit:8501" "Locust:8089" "Glances:61208"; do
    svc=$(echo "$svc_info" | cut -d: -f1)
    port=$(echo "$svc_info" | cut -d: -f2)
    pid=$(ss -tulpn "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
    if [ -n "$pid" ]; then
        status="RUNNING"
    else
        status="STOPPED"
        pid="-"
    fi
    printf "%-15s %-10s %-15s %-10s\n" "$svc" "$port" "$status" "$pid"
done

echo ""
echo "--- [2] Port Uji-GLOBAL-ENV (Port Berbeda) ---"
printf "%-15s %-10s %-15s %-10s\n" "Layanan" "Port" "Status" "PID"
for svc_info in "FastAPI:8001" "Streamlit:8502" "Locust:8090" "Glances:61209"; do
    svc=$(echo "$svc_info" | cut -d: -f1)
    port=$(echo "$svc_info" | cut -d: -f2)
    pid=$(ss -tulpn "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
    if [ -n "$pid" ]; then
        status="RUNNING"
    else
        status="STOPPED"
        pid="-"
    fi
    printf "%-15s %-10s %-15s %-10s\n" "$svc" "$port" "$status" "$pid"
done

echo "=========================================================="
