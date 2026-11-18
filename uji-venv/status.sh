#!/usr/bin/env bash
# ==============================================================================
# Script Memeriksa Status Layanan di uji-venv
# ==============================================================================

echo "=========================================================="
echo "              STATUS LAYANAN UJI-VENV                     "
echo "=========================================================="
printf "%-18s %-10s %-15s %-10s\n" "Layanan (Venv)" "Port" "Status" "PID"
echo "----------------------------------------------------------"
for svc_info in "Glances (glances):61208" "FastAPI (fastapi):8000" "Streamlit (st):8501" "Locust (locust):8089"; do
    svc=$(echo "$svc_info" | cut -d: -f1)
    port=$(echo "$svc_info" | cut -d: -f2)
    pid=$(ss -tulpn "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | head -n1 | cut -d= -f2)
    if [ -n "$pid" ]; then
        status="RUNNING"
    else
        status="STOPPED"
        pid="-"
    fi
    printf "%-18s %-10s %-15s %-10s\n" "$svc" "$port" "$status" "$pid"
done
echo "=========================================================="
