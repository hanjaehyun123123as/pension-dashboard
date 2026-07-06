# 감시 PC 부팅 시 대시보드 서버 자동 시작 등록 + 지금 바로 시작
$repo = $PSScriptRoot
$cmdPath = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup\pension-dashboard.cmd'
# 계정명에 한글이 있어도 깨지지 않도록 %USERPROFILE% 변수를 그대로 쓴다 (ASCII만 저장)
$cmdBody = "@echo off`r`nstart `"`" /min powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"%USERPROFILE%\Documents\pension-dashboard\serve_dashboard.ps1`""
$cmdBody | Out-File $cmdPath -Encoding ascii
Write-Host "자동 시작 등록 완료: $cmdPath"

# 지금 바로 서버 시작
Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-WindowStyle','Hidden','-File',"$repo\serve_dashboard.ps1" -WindowStyle Hidden
Start-Sleep -Seconds 3

# 접속 주소 안내
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } | Select-Object -First 1).IPAddress
Write-Host ""
Write-Host "=== 대시보드 서버 시작됨 ==="
Write-Host "이 PC에서 보기:     http://localhost:8899"
Write-Host "다른 PC/폰에서 보기: http://${ip}:8899  (같은 공유기/네트워크 안에서)"
