# Helper script to launch React Frontend
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host " Starting AI Knowledge Assistant Frontend (React + Vite)  " -ForegroundColor Magenta
Write-Host "==========================================================" -ForegroundColor Magenta

$env:Path = "C:\Program Files\nodejs;" + $env:Path
Set-Location "$PSScriptRoot\frontend"

Write-Host "Web app running at http://localhost:5173" -ForegroundColor Green

npm run dev
