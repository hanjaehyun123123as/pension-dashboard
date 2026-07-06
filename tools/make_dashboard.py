# 국민연금 대시보드 재생성 스크립트
# 사용법: python make_dashboard.py "원본피벗.xlsx" [비밀번호]
#   - 비밀번호를 주면 암호화 버전(index.html), 안 주면 평문 버전을 만든다
#   - 원본 엑셀: 시트별로 [사업장명, 사업자등록번호(앞6), 주소(최근), 월컬럼들...] 구조
import sys, os, gzip, base64
import pandas as pd

def build_blob(xlsx_path):
    sheets = pd.read_excel(xlsx_path, sheet_name=None, dtype={'사업자등록번호(앞6)': str})
    dfs = [df.iloc[:, :12] for df in sheets.values()]
    d = pd.concat(dfs, ignore_index=True)
    months = list(d.columns[3:12])
    keep = d[months].max(axis=1) >= 1
    d = d[keep]
    lines = []
    for r in d.itertuples(index=False):
        name = str(r[0]).replace('\t', ' ').replace('\n', ' ')
        biz = '' if pd.isna(r[1]) else str(r[1])
        addr = '' if pd.isna(r[2]) else ' '.join(str(r[2]).split()[:3])
        vals = ['' if (pd.isna(r[i]) or int(r[i]) == 0) else str(int(r[i])) for i in range(3, 12)]
        lines.append('\t'.join([name, biz, addr] + vals))
    raw = '\n'.join(lines).encode('utf-8')
    return gzip.compress(raw, 9), months, len(lines)

def encrypt(gz, password):
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                     iterations=300000).derive(password.encode())
    return salt + iv + AESGCM(key).encrypt(iv, gz, None)

if __name__ == '__main__':
    xlsx = sys.argv[1]
    pw = sys.argv[2] if len(sys.argv) > 2 else None
    here = os.path.dirname(os.path.abspath(__file__))
    tpl = open(os.path.join(here, 'template.html'), encoding='utf-8').read()
    # 주의: 월 컬럼이 바뀌면 template.html의 MONTHS 배열도 함께 수정해야 함
    gz, months, n = build_blob(xlsx)
    print('rows:', n, 'months:', months)
    if pw:
        data = encrypt(gz, pw)
        out = tpl.replace('__ENC__', 'true')
    else:
        data = gz
        out = tpl.replace('__ENC__', 'false')
    out = out.replace('__B64__', base64.b64encode(data).decode())
    dst = os.path.join(os.path.dirname(here), 'index.html')
    open(dst, 'w', encoding='utf-8').write(out)
    print('written:', dst, round(os.path.getsize(dst) / 1e6, 1), 'MB')
