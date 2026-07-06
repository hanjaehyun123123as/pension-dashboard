# 국민연금 대시보드 24시간 서버
# 매시간 GitHub에서 최신 버전을 받아와 다시 서빙합니다.
Set-Location $PSScriptRoot
$port = 8899

# python이 PATH에 없으면 telebot-youtube 가상환경의 python을 사용
$py = "python"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    $py = Join-Path $env:USERPROFILE "Documents\telebot-youtube\.venv\Scripts\python.exe"
}

while ($true) {
    try { git pull --quiet } catch {}
    $srv = Start-Process $py -ArgumentList '-m','http.server',"$port" -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 3600
    try { Stop-Process -Id $srv.Id -Force -ErrorAction Stop } catch {}
}
