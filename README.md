# 국민연금 사업장 인원 검색 대시보드

국민연금 사업장 가입자수 데이터(월별)를 회사명 키워드로 검색해
계열 사업장(본사·현장·일용)을 묶어 인원 추이를 보는 대시보드입니다.

- `index.html` — 대시보드 본체 (데이터 내장, 이 파일 하나로 동작)
- `serve_dashboard.ps1` — 24시간 서버 (매시간 git pull로 자동 업데이트)
- `install_dashboard_startup.ps1` — 감시 PC 부팅 시 자동 시작 등록

## 감시 PC 설치

**자동입니다.** 감시 PC의 telebot-youtube 자동 업데이트 스크립트(telebot_update.ps1)가
이 저장소가 없으면 클론하고 자동시작 등록 + 서버 시작까지 해줍니다.
설치가 끝나면 텔레그램으로 알림이 옵니다.

수동으로 설치하려면 (필요할 때만):

```powershell
cd $env:USERPROFILE\Documents
git clone https://github.com/hanjaehyun123123as/pension-dashboard.git
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Documents\pension-dashboard\install_dashboard_startup.ps1"
```

## 접속

- 감시 PC에서: http://localhost:8899
- 같은 네트워크의 다른 PC/폰에서: http://감시PC아이피:8899

## 데이터 업데이트 (새 달 자료가 나왔을 때)

작업 PC에서 클로드에게 "국민연금 대시보드 새 엑셀로 업데이트해줘"라고 하면
index.html을 다시 만들어 push → 감시 PC가 1시간 안에 자동 반영.

데이터 출처: 국민연금공단 사업장 가입 내역 (22.12 ~ 26.5),
원본: 국민연금_사업장_가입자수_피벗.xlsx
