# Helper script to launch FastAPI Backend Server
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting AI Knowledge Assistant Backend (FastAPI + RAG) " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$env:Path = "C:\Python312;C:\Python312\Scripts;C:\Program Files\nodejs;" + $env:Path
Set-Location "$PSScriptRoot\backend"

# Detect if PostgreSQL is listening on port 5432
$pgAvailable = $false
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $ar = $tcp.BeginConnect("127.0.0.1", 5432, $null, $null)
    $success = $ar.AsyncWaitHandle.WaitOne(600)
    if ($success -and $tcp.Connected) {
        $tcp.EndConnect($ar)
        $pgAvailable = $true
    }
    $tcp.Close()
} catch {
    $pgAvailable = $false
}

if ($pgAvailable) {
    Write-Host "[DB] Connected to PostgreSQL on port 5432 with pgvector." -ForegroundColor Green
    $env:DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/knowledge_assistant"
} else {
    Write-Host "[DB] PostgreSQL port 5432 not active." -ForegroundColor Yellow
    Write-Host "[DB] Standalone mode: using SQLite (knowledge_assistant.db)." -ForegroundColor Yellow
    Write-Host "     (To use PostgreSQL with pgvector, run 'docker compose up -d')" -ForegroundColor Gray
    $env:DATABASE_URL = "sqlite:///./knowledge_assistant.db"
}

Write-Host "`nServer running at http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Interactive Swagger Docs: http://127.0.0.1:8000/docs`n" -ForegroundColor Green

python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
