# Helper script to run all backend and frontend automated tests
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host " Running Automated Test Suites for AI Knowledge Assistant " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Yellow

$env:Path = "C:\Python312;C:\Python312\Scripts;C:\Program Files\nodejs;" + $env:Path

Write-Host "`n[1/2] Running Backend Pytest Suite..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot\backend"
python -m pytest -v

Write-Host "`n[2/2] Running Frontend Vitest Suite..." -ForegroundColor Magenta
Set-Location "$PSScriptRoot\frontend"
npm test

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " All test suites completed! " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
