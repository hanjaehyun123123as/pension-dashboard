# 최신 게시본(read 저장 파일)에 저장소 tonghap_tab.py의 통합 탭을 다시 끼운다. 사용: python reinject.py <read파일> <이전탭백업.py> <출력.html>
import sys, io, importlib.util, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
def load(path):
    spec = importlib.util.spec_from_loader('m', loader=None); m = importlib.util.module_from_spec(spec)
    exec(open(path, encoding='utf-8').read(), m.__dict__); return m
live, oldtab, out_path = sys.argv[1:4]
full = open(live, encoding='utf-8').read()
base = full[full.index('<body>') + 6: full.rindex('</body></html>')]
old = load(oldtab); new = load(r"C:\Users\123\Documents\pension-dashboard\tools\tonghap_tab.py")
assert old.CSS.strip() in base and old.VIEW in base, '게시본 탭 코드가 이전 백업과 다름 — 다른 곳에서 고쳤는지 확인'
i = base.index('const TG='); j = base.index(';\nlet tgSort=', i); data = base[i + len('const TG='):j]   # 게시본 데이터 그대로
out = new.inject(base, fragment=True).replace('__TONGHAP__', data)
open(out_path, 'w', encoding='utf-8').write(out)
open(r"C:\Users\123\내 드라이브\claude\국민연금 클로드 26.4\_art_test.html", 'w', encoding='utf-8').write(
    '<!DOCTYPE html><html><head><meta charset="utf-8"><title>t</title></head><body style="margin:0">' + out + '</body></html>')
ch = [l for l in difflib.unified_diff(base.split('\n'), out.split('\n'), lineterm='', n=0) if l[:1] in '+-' and not l.startswith(('+++', '---'))]
print('바뀐 줄', len(ch), '| TG 데이터 바뀜', any(l.startswith('-const TG=') for l in ch), '| MB', round(len(out.encode('utf-8'))/1e6, 2))
