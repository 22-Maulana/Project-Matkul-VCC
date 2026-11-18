from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="API Simulasi Beban Komputasi",
    description="Server backend untuk pengujian load testing dan monitoring kinerja CPU.",
    version="2.0.0"
)

@app.get("/", response_class=HTMLResponse, tags=["Beranda"])
def beranda():
    return """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Server API - Cloud Computing</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; color: #334155; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .container { background: white; max-width: 700px; width: 100%; padding: 40px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border-top: 5px solid #2563eb; }
            .header-flex { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 25px; }
            h1 { color: #0f172a; margin: 0; font-size: 1.8rem; }
            .status-badge { background-color: #10b981; color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; letter-spacing: 0.5px; }
            .info-box { background-color: #f1f5f9; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #3b82f6; }
            .info-box p { margin: 8px 0; font-size: 1.05rem; }
            .endpoint { font-family: monospace; background: #e2e8f0; padding: 4px 8px; border-radius: 4px; color: #b91c1c; font-weight: bold; }
            .btn-container { display: flex; gap: 15px; }
            .btn { flex: 1; text-align: center; text-decoration: none; padding: 14px; border-radius: 8px; font-weight: 600; transition: all 0.2s; }
            .btn-primary { background-color: #2563eb; color: white; border: 1px solid #2563eb; }
            .btn-primary:hover { background-color: #1d4ed8; }
            .btn-outline { background-color: transparent; color: #475569; border: 1px solid #cbd5e1; }
            .btn-outline:hover { background-color: #f8fafc; border-color: #94a3b8; }
            .footer { margin-top: 30px; text-align: center; font-size: 0.85rem; color: #94a3b8; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-flex">
                <h1>🚀 Server Backend API</h1>
                <span class="status-badge">ONLINE / PORT 8000</span>
            </div>
            
            <div class="info-box">
                <p><strong>Proyek:</strong> Analisis Perbandingan Kinerja Eksekusi Program (Virtual vs Global Env)</p>
                <p><strong>Fungsi Server:</strong> Menangani <i>request</i> komputasi berat (pencarian bilangan prima) untuk mensimulasikan lonjakan CPU saat menerima serangan <i>traffic</i> dari Locust.</p>
                <p><strong>Target Endpoint:</strong> <span class="endpoint">GET /berat</span></p>
            </div>

            <div class="btn-container">
                <a href="/docs" class="btn btn-primary">Buka Interaktif UI (Swagger)</a>
                <a href="/redoc" class="btn btn-outline">Buka Dokumentasi (ReDoc)</a>
            </div>

            <div class="footer">
                Di-deploy pada instance AWS EC2 Ubuntu &bull; Infrastruktur Eksperimen Kinerja
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/berat", tags=["Uji Beban Ekstrem"])
def kerja_berat():
    # Menguras CPU dengan algoritma bilangan prima
    primes = [x for x in range(2, 20000) if all(x % y != 0 for y in range(2, int(x**0.5) + 1))]
    return {
        "status": "Berhasil",
        "kode_respon": 200,
        "total_prima": len(primes),
        "total_prima_ditemukan": len(primes),
        "pesan": "CPU EC2 Anda baru saja disiksa!"
    }
