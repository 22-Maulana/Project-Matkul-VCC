from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="FastAPI Server - Virtual Environment",
    description="Backend API untuk pengujian komputasi CPU di Python Virtual Environment (venv)",
    version="2.0.0"
)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FastAPI Activated - Virtual Environment</title>
  <style>
    :root {
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --success: #10b981;
      --success-bg: #ecfdf5;
      --success-border: #a7f3d0;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    body {
      background-color: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 24px 16px;
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
      max-width: 560px;
      width: 100%;
      padding: 36px 32px;
      text-align: center;
    }

    .badge-container {
      display: flex;
      justify-content: center;
      margin-bottom: 18px;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--success-bg);
      color: #065f46;
      border: 1px solid var(--success-border);
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.3px;
    }

    .pulse-dot {
      width: 8px;
      height: 8px;
      background-color: var(--success);
      border-radius: 50%;
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      }
      70% {
        box-shadow: 0 0 0 7px rgba(16, 185, 129, 0);
      }
      100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
      }
    }

    h1 {
      font-size: 26px;
      font-weight: 800;
      color: var(--text);
      letter-spacing: -0.5px;
      margin-bottom: 6px;
    }

    .env-tag {
      display: inline-block;
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 24px;
    }

    .env-tag strong {
      color: var(--primary);
    }

    .info-panel {
      background: #f1f5f9;
      border-radius: 12px;
      padding: 16px 20px;
      text-align: left;
      margin-bottom: 24px;
      font-size: 14px;
      line-height: 1.6;
      border-left: 4px solid var(--primary);
    }

    .info-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 0;
      border-bottom: 1px solid #e2e8f0;
    }

    .info-row:last-child {
      border-bottom: none;
    }

    .info-label {
      color: var(--text-muted);
      font-weight: 500;
    }

    .info-val {
      font-weight: 600;
      color: var(--text);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 13px;
    }

    .btn-group {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 12px;
    }

    @media (min-width: 480px) {
      .btn-group-row {
        display: flex;
        gap: 10px;
      }
      .btn-group-row .btn {
        flex: 1;
      }
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 12px 20px;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid transparent;
      width: 100%;
    }

    .btn-primary {
      background: var(--primary);
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }

    .btn-primary:hover:not(:disabled) {
      background: var(--primary-hover);
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
    }

    .btn-primary:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }

    .btn-outline {
      background: transparent;
      color: #334155;
      border-color: #cbd5e1;
    }

    .btn-outline:hover {
      background: #f8fafc;
      border-color: #94a3b8;
      color: #0f172a;
    }

    /* Result Box */
    .result-card {
      margin-top: 16px;
      padding: 16px;
      border-radius: 12px;
      background: #f8fafc;
      border: 1px solid var(--border);
      text-align: left;
      font-size: 13px;
      display: none;
    }

    .result-card.active {
      display: block;
      animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      margin-bottom: 8px;
      color: var(--text);
    }

    .result-badge {
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 6px;
      font-weight: 700;
    }

    .result-badge.success {
      background: #dcfce7;
      color: #15803d;
    }

    .result-badge.loading {
      background: #fef3c7;
      color: #b45309;
    }

    .result-badge.error {
      background: #fee2e2;
      color: #b91c1c;
    }

    .result-detail {
      color: var(--text-muted);
      font-size: 12px;
      line-height: 1.5;
    }

    .result-code {
      margin-top: 10px;
      background: #0f172a;
      color: #38bdf8;
      padding: 12px;
      border-radius: 8px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      overflow-x: auto;
      white-space: pre;
    }

    .footer {
      margin-top: 24px;
      font-size: 12px;
      color: var(--text-muted);
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge-container">
      <div class="status-badge">
        <span class="pulse-dot"></span>
        FastAPI Activated
      </div>
    </div>

    <h1>FastAPI Server</h1>
    <div class="env-tag">
      Environment: <strong>Python Virtual Environment (venv)</strong> &bull; Port <strong>8000</strong>
    </div>

    <div class="info-panel">
      <div class="info-row">
        <span class="info-label">Status Server</span>
        <span class="info-val" style="color: #10b981;">● Online / Active</span>
      </div>
      <div class="info-row">
        <span class="info-label">Target Endpoint</span>
        <span class="info-val">GET /berat</span>
      </div>
      <div class="info-row">
        <span class="info-label">Keterangan</span>
        <span class="info-val" style="font-family: inherit; font-size: 12px; color: var(--text-muted);">Uji Stres Komputasi CPU</span>
      </div>
    </div>

    <div class="btn-group">
      <button id="btn-test" class="btn btn-primary" onclick="testBenchmark()">
        <span id="btn-icon">⚡</span>
        <span id="btn-label">Uji Endpoint /berat</span>
      </button>

      <div class="btn-group-row">
        <a href="/docs" target="_blank" class="btn btn-outline">
          <span>📚</span> Swagger UI
        </a>
        <a href="/redoc" target="_blank" class="btn btn-outline">
          <span>📋</span> ReDoc
        </a>
      </div>
    </div>

    <div id="result-box" class="result-card">
      <div class="result-header">
        <span id="res-title">Hasil Uji Komputasi</span>
        <span id="res-badge" class="result-badge success">200 OK</span>
      </div>
      <div id="res-detail" class="result-detail"></div>
      <pre id="res-json" class="result-code"></pre>
    </div>

    <div class="footer">
      FastAPI Benchmark Suite &bull; AWS EC2 Ubuntu
    </div>
  </div>

  <script>
    async function testBenchmark() {
      const btn = document.getElementById("btn-test");
      const btnIcon = document.getElementById("btn-icon");
      const btnLabel = document.getElementById("btn-label");
      const resBox = document.getElementById("result-box");
      const resBadge = document.getElementById("res-badge");
      const resDetail = document.getElementById("res-detail");
      const resJson = document.getElementById("res-json");

      btn.disabled = true;
      btnIcon.innerText = "⏳";
      btnLabel.innerText = "Memproses Komputasi...";

      resBox.className = "result-card active";
      resBadge.className = "result-badge loading";
      resBadge.innerText = "Sedang Berjalan...";
      resDetail.innerText = "Mengirim permintaan ke endpoint /berat...";
      resJson.style.display = "none";

      const startTime = performance.now();

      try {
        const response = await fetch("/berat");
        if (!response.ok) throw new Error("HTTP " + response.status);
        const data = await response.json();
        const duration = Math.round(performance.now() - startTime);

        resBadge.className = "result-badge success";
        resBadge.innerText = `200 OK (${duration} ms)`;
        const primeCount = data.total_prima !== undefined ? data.total_prima : data.total_prima_ditemukan;
        resDetail.innerHTML = `Durasi: <strong>${duration} ms</strong> | Total Prima: <strong>${(primeCount || 0).toLocaleString("id-ID")}</strong> | Status: <strong>${data.status || "OK"}</strong>`;
        resJson.style.display = "block";
        resJson.innerText = JSON.stringify(data, null, 2);
      } catch (err) {
        resBadge.className = "result-badge error";
        resBadge.innerText = "Gagal";
        resDetail.innerText = "Terjadi kesalahan saat memanggil /berat: " + err.message;
        resJson.style.display = "none";
      } finally {
        btn.disabled = false;
        btnIcon.innerText = "⚡";
        btnLabel.innerText = "Uji Ulang Endpoint /berat";
      }
    }
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse, tags=["Beranda"])
def halaman_utama():
    return HTML_CONTENT

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
