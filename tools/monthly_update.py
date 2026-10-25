# 국민연금 대시보드 월간 업데이트 (CSV 1개 → 엑셀 피벗 갱신 + 빌드 재료 생성)
# 사용: python monthly_update.py "CSV1" ["CSV2" ...]  (오래된 달부터 순서대로, 엑셀은 마지막에 한 번 저장)
import sys, io, os, re, json, gzip, shutil, warnings
import pandas as pd
warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CSV   = sys.argv[1]
PIVOT = r"C:\Users\123\내 드라이브\claude\국민연금_사업장_가입자수_피벗.xlsx 클로드.xlsx"
REPO  = r"C:\Users\123\Documents\pension-dashboard"

def read_month(path):
    csv = pd.read_csv(path, encoding='cp949', dtype={'사업자등록번호': str},
                      usecols=['자료생성년월','사업장명','사업자등록번호','사업장지번상세주소','가입자수'])
    ym = csv['자료생성년월'].astype(str).unique()
    assert len(ym) == 1, f'월이 섞여 있음: {ym}'
    y, m = ym[0].split('-')
    label = f'{int(y)%100}.{int(m)}'
    csv = csv.drop(columns='자료생성년월'); csv.columns = ['n','biz','addr','v']
    csv['n'] = csv['n'].astype(str).str.strip(); csv['biz'] = csv['biz'].astype(str).str.strip()
    g = csv.groupby(['n','biz'], as_index=False).agg(v=('v','sum'), addr=('addr','first'))
    print(f'CSV {ym[0]} → 컬럼 {label} | 사업장 {len(g):,}')
    return label, g

# 2) 기존 피벗 읽기
sheets = pd.read_excel(PIVOT, sheet_name=None, dtype={'사업자등록번호(앞6)': str})
old = pd.concat(sheets.values(), ignore_index=True)
months = [c for c in old.columns if re.fullmatch(r'\d{2}\.\d{1,2}', str(c))]
PREV = months[-1]
print(f'기존 피벗: {len(old):,}행, 마지막 월 {PREV}')
bak = PIVOT.replace('_피벗.xlsx 클로드.xlsx', f'_피벗_백업_{PREV}까지.xlsx')
shutil.copyfile(PIVOT, bak); print('백업:', os.path.basename(bak))

# 3) 새 월 병합 (CSV 순서대로)
allp = old.drop(columns=[x for x in old.columns if x not in ['사업장명','사업자등록번호(앞6)','주소(최근)']+months])
for path in sys.argv[1:]:
    NEW, cur_m = read_month(path)
    assert NEW not in months, f'{NEW} 컬럼이 이미 있음 — 중복 업데이트'
    allp['n'] = allp['사업장명'].astype(str).str.strip(); allp['biz'] = allp['사업자등록번호(앞6)'].astype(str).str.strip()
    vmap = dict(zip(zip(cur_m['n'],cur_m['biz']), cur_m['v'])); amap = dict(zip(zip(cur_m['n'],cur_m['biz']), cur_m['addr']))
    keys = list(zip(allp['n'], allp['biz']))
    allp[NEW] = [vmap.get(k) for k in keys]
    na = [amap.get(k) for k in keys]
    allp['주소(최근)'] = [a if isinstance(a,str) and a.strip() else o for a,o in zip(na, allp['주소(최근)'])]
    ks = set(keys); new = cur_m[[k not in ks for k in zip(cur_m['n'],cur_m['biz'])]]
    add = pd.DataFrame({'사업장명':new['n'].values,'사업자등록번호(앞6)':new['biz'].values,'주소(최근)':new['addr'].values, NEW:new['v'].values})
    for c in months: add[c] = pd.NA
    print(f'  기존 매칭 {int(allp[NEW].notna().sum()):,} / 신규 사업장 {len(new):,}')
    cols = ['사업장명','사업자등록번호(앞6)','주소(최근)'] + months + [NEW]
    allp = pd.concat([allp[cols], add[cols]], ignore_index=True)
    months = months + [NEW]
cur = allp[allp[NEW].notna()].sort_values(NEW, ascending=False)
past = allp[allp[NEW].isna()].sort_values('사업장명')
with pd.ExcelWriter(PIVOT, engine='xlsxwriter') as w:
    cur.to_excel(w, sheet_name=f'가입자수({NEW}존재)', index=False)
    past.to_excel(w, sheet_name=f'과거사업장({NEW}없음)', index=False)
print(f'엑셀 저장: {NEW}존재 {len(cur):,} / {NEW}없음 {len(past):,}')

# 4) 대시보드 데이터
M = months; NM = len(M)
for c in M: allp[c] = pd.to_numeric(allp[c], errors='coerce')
d = allp[allp[M].max(axis=1) >= 1]
lines = []
for r in d.itertuples(index=False):
    name = str(r[0]).replace('\t',' ').replace('\n',' ')
    biz = '' if pd.isna(r[1]) else str(r[1])
    addr = '' if pd.isna(r[2]) else ' '.join(str(r[2]).split()[:3])
    vals = ['' if (pd.isna(r[i]) or int(r[i])==0) else str(int(r[i])) for i in range(3, 3+NM)]
    lines.append('\t'.join([name,biz,addr] + vals))
open('data.gz','wb').write(gzip.compress('\n'.join(lines).encode('utf-8'), 9))
print(f'대시보드 데이터 {len(lines):,}행')

# 5) 기본그룹 복구 + 아티팩트용 데이터(10명 이상 + 그룹 소속)
h = open(os.path.join(REPO,'index.html'), encoding='utf-8').read()
groups = json.loads(re.search(r'const DEFAULT_GROUPS=(\[.*?\]);\n', h, re.S).group(1))
json.dump(groups, open('groups.json','w',encoding='utf-8'), ensure_ascii=False)
keep = {(e['l'], e.get('b','')) for g in groups for e in g['items']}
sel = []
for ln in lines:
    p = ln.split('\t'); vs = [int(v) for v in p[3:3+NM] if v]
    if (vs and max(vs) >= 10) or (p[0],p[1]) in keep: sel.append(ln)
gz = gzip.compress('\n'.join(sel).encode('utf-8'), 9)
open('data_art.gz','wb').write(gz)
print(f'아티팩트 데이터 {len(sel):,}행, b64 {len(gz)*4/3/1e6:.2f}MB (한도 16MB)')

# 6) 템플릿·빌드스크립트 월 문구 갱신
man_all = round(len(lines)/10000); man_art = round(len(sel)/10000)
tp = os.path.join(REPO,'tools','template.html'); t = open(tp, encoding='utf-8').read()
t = re.sub(r"const MONTHS=\[[^\]]*\];", "const MONTHS=[" + ",".join(f"'{c}'" for c in M) + "];", t)
t = re.sub(r"· 자료: 22\.12 ~ \d{2}\.\d{1,2}</div>", f"· 자료: 22.12 ~ {NEW}</div>", t)
t = re.sub(r"데이터 로딩 중… \(\d+만 사업장", f"데이터 로딩 중… ({man_all}만 사업장", t)
open(tp,'w',encoding='utf-8').write(t); shutil.copyfile(tp, 'template.html')
bp = os.path.join(REPO,'tools','build_all.py'); b = open(bp, encoding='utf-8').read()
b = re.sub(r'\("· 자료: 22\.12 ~ [\d.]+","· 자료: 22\.12 ~ [\d.]+ · 상장사 전체 포함"\)',
           f'("· 자료: 22.12 ~ {NEW}","· 자료: 22.12 ~ {NEW} · 상장사 전체 포함")', b)
b = re.sub(r'\("데이터 로딩 중… \(\d+만 사업장, 몇 초 걸립니다\)","데이터 로딩 중… \(\d+만 사업장, 몇 초 걸립니다\)"\)',
           f'("데이터 로딩 중… ({man_all}만 사업장, 몇 초 걸립니다)","데이터 로딩 중… ({man_art}만 사업장, 몇 초 걸립니다)")', b)
open(bp,'w',encoding='utf-8').write(b); shutil.copyfile(bp, 'build_all.py')
print(f'템플릿 MONTHS → {M[-3:]} ... / 다음 단계: python build_all.py')
