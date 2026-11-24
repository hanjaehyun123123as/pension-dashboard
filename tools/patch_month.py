# 이미 만들어진 대시보드 HTML 3종에서 국민연금 데이터 부분만 새 달로 교체 (탭·동기화 등 다른 코드는 그대로)
import sys, io, os, re, json, gzip, base64, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

tpl = open('template.html', encoding='utf-8').read()          # monthly_update.py가 갱신한 MONTHS
MONTHS = re.search(r"const MONTHS=\[[^\]]*\];", tpl).group(0)
LAST = re.findall(r"'([^']+)'", MONTHS)[-1]
GZ, GZA = open('data.gz','rb').read(), open('data_art.gz','rb').read()
n_all = len(gzip.decompress(GZ).split(b'\n')); n_art = len(gzip.decompress(GZA).split(b'\n'))

def enc(gz, pw=b'4618'):
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=300000).derive(pw)
    return salt + iv + AESGCM(key).encrypt(iv, gz, None)

def patch(h, blob, man, tg=None):
    def one(pat, rep, s):
        s2, k = re.subn(pat, rep, s, count=1)
        assert k == 1, pat
        return s2
    h = one(r'(<script id="D" type="text/plain">)[A-Za-z0-9+/=]*(</script>)', lambda m: m.group(1) + base64.b64encode(blob).decode() + m.group(2), h)
    h = one(r"const MONTHS=\[[^\]]*\];", lambda m: MONTHS, h)
    h = one(r"· 자료: 22\.12 ~ \d{2}\.\d{1,2}", lambda m: '· 자료: 22.12 ~ ' + LAST, h)
    h = one(r"데이터 로딩 중… \(\d+만 사업장", lambda m: f'데이터 로딩 중… ({man}만 사업장', h)
    if tg is not None:
        spec = importlib.util.spec_from_loader('tt', loader=None); tt = importlib.util.module_from_spec(spec)
        exec(open(r"C:\Users\123\Documents\pension-dashboard\tools\tonghap_tab.py", encoding='utf-8').read(), tt.__dict__)
        h = tt.replace_data(h, tg)
    return h

# 1) 클로드 아티팩트 (게시본 본문)
LIVE = sys.argv[1]
full = open(LIVE, encoding='utf-8').read()
body = full[full.index('<body>') + 6: full.rindex('</body></html>')]
tg = open(r"C:\Users\123\Documents\pension-dashboard\tools\tonghap.json", encoding='utf-8').read()
art = patch(body, GZA, round(n_art/1e4), tg)
open('art_month.html', 'w', encoding='utf-8').write(art)
# 2) 공개(폰용, 암호) 3) 작업 PC 평문
P1 = r"C:\Users\123\Documents\pension-dashboard\index.html"
P2 = r"C:\Users\123\내 드라이브\claude\국민연금 클로드 26.4\국민연금_인원검색_대시보드.html"
pub = patch(open(P1, encoding='utf-8').read(), enc(GZ), round(n_all/1e4))
loc = patch(open(P2, encoding='utf-8').read(), GZ, round(n_all/1e4))
open(P1, 'w', encoding='utf-8').write(pub); open(P2, 'w', encoding='utf-8').write(loc)
open(r"C:\Users\123\내 드라이브\claude\국민연금 클로드 26.4\_art_test.html", 'w', encoding='utf-8').write(
    '<!DOCTYPE html><html><head><meta charset="utf-8"><title>t</title></head><body style="margin:0">' + art + '</body></html>')
for nm, s in (('아티팩트', art), ('공개', pub), ('작업PC', loc)):
    print(nm, round(len(s.encode('utf-8'))/1e6, 2), 'MB')
print('마지막 월', LAST, '| 사업장 전체', n_all, '/ 아티팩트', n_art)
