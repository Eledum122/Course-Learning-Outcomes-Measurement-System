# PowerShell script to run CLOs Measurement System
# سكريبت PowerShell لتشغيل نظام قياس مخرجات التعلم

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CLOs Measurement System" -ForegroundColor Green
Write-Host "نظام قياس مخرجات التعلم للمقررات الدراسية" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set location to script directory
Set-Location -Path $PSScriptRoot

Write-Host "Starting application..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor White
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""

# Run the application
python main.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Application closed." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
