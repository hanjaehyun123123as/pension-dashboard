# 대시보드 3종 빌드: 공개(암호), 로컬(평문), 아티팩트(상장사 그룹)
import os, re, json, base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

TPL  = open('template.html', encoding='utf-8').read()
GROUPS = open('groups.json', encoding='utf-8').read()
GZ   = open('data.gz','rb').read()

def enc(gz, pw=b'4618'):
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=300000).derive(pw)
    return salt + iv + AESGCM(key).encrypt(iv, gz, None)

# 1) 공개 사이트 (암호 4618)
t = TPL.replace('__GROUPS__', GROUPS)
p1 = r"C:\Users\123\Documents\pension-dashboard\index.html"
open(p1,'w',encoding='utf-8').write(t.replace('__ENC__','true').replace('__B64__', base64.b64encode(enc(GZ)).decode()))
# 2) 작업 PC용 (평문)
p2 = r"C:\Users\123\내 드라이브(wogus4618@gmail.com)\국민연금 클로드 26.4\국민연금_인원검색_대시보드.html"
open(p2,'w',encoding='utf-8').write(t.replace('__ENC__','false').replace('__B64__', base64.b64encode(GZ).decode()))

# 3) 아티팩트 (다중 기본그룹 + 조각 HTML)
a = TPL
a = a.replace("const WKEY='pd_watch3';", "const WKEY='pd_art_watch1';")
for x,y in [("localStorage.getItem('pd_watch_open')","localStorage.getItem('pd_art_watch_open')"),
            ("localStorage.setItem('pd_watch_open',","localStorage.setItem('pd_art_watch_open',"),
            ("localStorage.setItem('pd_pins'","localStorage.setItem('pd_art_pins'"),
            ("localStorage.getItem('pd_pins')","localStorage.getItem('pd_art_pins')"),
            ("localStorage.removeItem('pd_pins')","localStorage.removeItem('pd_art_pins')"),
            ("기본 목록(830개 법인)","기본 목록"),
            ("현재 그룹을 기본목록(830개)으로 복원","현재 그룹을 기본목록으로 복원"),
            ("· 자료: 22.12 ~ 26.7","· 자료: 22.12 ~ 26.7 · 상장사 전체 포함"),
            ("데이터 로딩 중… (89만 사업장, 몇 초 걸립니다)","데이터 로딩 중… (33만 사업장, 몇 초 걸립니다)")]:
    a = a.replace(x,y)
style = re.search(r'<style>.*?</style>', a, re.S).group(0)
body  = re.search(r'<body>(.*)</body>', a, re.S).group(1)
frag  = style + "\n" + body.strip()
frag = frag.replace("body{background:var(--bg);color:var(--tx);font-family:'Malgun Gothic','Segoe UI',sans-serif;font-size:14px;padding:18px}",
  ".pdwrap{background:var(--bg);color:var(--tx);font-family:'Malgun Gothic','Segoe UI',sans-serif;font-size:14px;padding:18px;border-radius:12px}\n.pdwrap *{box-sizing:border-box}")
frag = frag.replace("<style>", "<style>\n.pdwrap h1,.pdwrap h2{color:var(--tx)}")
i = frag.index("</style>")+len("</style>")
frag = frag[:i] + '\n<div class="pdwrap">\n' + frag[i:]
frag = frag.replace('<script id="D"', '</div>\n<script id="D"', 1)
frag = frag.replace('__GROUPS__', GROUPS).replace('__ENC__','false')
frag = frag.replace('__B64__', base64.b64encode(open('data_art.gz','rb').read()).decode())
p3 = os.path.abspath('pension_dashboard_artifact.html')
open(p3,'w',encoding='utf-8').write(frag)
open(r"C:\Users\123\내 드라이브(wogus4618@gmail.com)\국민연금 클로드 26.4\_art_test.html",'w',encoding='utf-8').write(
  '<!DOCTYPE html><html><head><meta charset="utf-8"><title>t</title></head><body style="margin:0">'+frag+'</body></html>')
for p in (p1,p2,p3): print(os.path.basename(p), round(os.path.getsize(p)/1e6,2),'MB')
