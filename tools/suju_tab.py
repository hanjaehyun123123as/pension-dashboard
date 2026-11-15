# 수주+재고 탭: 제목 옆 작은 탭 + 표 화면을 대시보드 HTML(템플릿/아티팩트 조각)에 끼워 넣는다.
# 데이터 자리는 __SUJU__ (build_all.py가 suju.json 내용 또는 null로 바꿈)
CSS = r"""
#vtabs{display:inline-flex;gap:4px;margin-left:10px;vertical-align:3px}
.vtab{font-size:11px;font-weight:600;padding:2px 9px;border:1px solid var(--line);border-radius:10px;color:var(--tx2);cursor:pointer;background:var(--panel)}
.vtab:hover{color:var(--tx);border-color:var(--acc)}
.vtab.on{background:var(--acc);border-color:var(--acc);color:#08131f}
#sujuView{display:none}
html.sj-on #sujuView{display:block}
html.sj-on #main,html.sj-on #loading,html.sj-on #gate{display:none!important}
.sjbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:10px;font-size:12px;color:var(--tx2)}
#sjQ{background:var(--panel2);border:1px solid var(--line);border-radius:6px;color:var(--tx);padding:5px 10px;font-size:13px;outline:none;width:170px}
#sjQ:focus{border-color:var(--acc)}
#sjT th{cursor:pointer;user-select:none}
#sjT td.nm{text-align:left;color:var(--tx);font-weight:600}
#sjT td.st{text-align:left;color:var(--tx2);font-size:11.5px;max-width:300px;overflow:hidden;text-overflow:ellipsis}
#sjT td.lk{cursor:pointer}
#sjT td.lk:hover{color:var(--acc);text-decoration:underline}
#sjT td.up{color:var(--grn)}#sjT td.dn{color:var(--red)}#sjT td.pn{color:var(--acc)}
#sjT tr:hover td{background:var(--panel2)}
"""

TABS = ('<span id="vtabs" style="display:none">'
        '<span class="vtab on" data-v="m" onclick="sjView(\'m\')">인원검색</span>'
        '<span class="vtab" data-v="s" onclick="sjView(\'s\')">수주+재고</span></span>')

VIEW = r"""<div id="sujuView"><div class="card">
<div class="sjbar">
  <h2 style="margin:0">수주잔고 · 재고자산 + 국민연금 <span id="sjBase" style="font-weight:400"></span></h2>
  <input id="sjQ" placeholder="종목 검색" oninput="sjRender()">
  <label><input type="checkbox" id="sjOrd" onchange="sjRender()"> 수주잔고 있는 종목만</label>
  <span>재고 증가율 ≥ <input id="sjInvMin" class="fin" type="number" step="1" oninput="sjRender()">%</span>
  <span>수주 증가율 ≥ <input id="sjOrdMin" class="fin" type="number" step="1" oninput="sjRender()">%</span>
  <span>연금 증감 ≥ <input id="sjPenMin" class="fin" type="number" step="1" oninput="sjRender()">%</span>
  <span style="flex:1"></span><span id="sjStat"></span>
</div>
<div style="max-height:75vh;overflow:auto;border:1px solid var(--line);border-radius:8px"><table id="sjT"></table></div>
<div style="margin-top:8px;font-size:11.5px;color:var(--tx2)">열 제목 클릭 = 정렬(# = 원래 순서) · 매칭 사업장 클릭 = 인원검색 탭에서 그 회사 사업장 보기 · 연금 증감 = 첫 달 대비 최근 달 · 증가율은 직전 분기 대비(QoQ)</div>
</div></div>
"""

JS = r"""
const SUJU=__SUJU__;
let sjSort={k:-1,d:1};
function sjView(v){
  document.documentElement.classList.toggle('sj-on',v==='s');
  document.querySelectorAll('.vtab').forEach(t=>t.classList.toggle('on',t.dataset.v===v));
  if(v==='s'&&!document.getElementById('sjT').innerHTML)sjRender();
}
function sjMoney(e){if(e==null)return '';if(e>=10000)return (e/10000).toLocaleString('ko-KR',{maximumFractionDigits:1})+'조';return Math.round(e).toLocaleString('ko-KR')+'억';}
function sjPct(x){return x==null?'':(x>0?'+':'')+(x*100).toFixed(1)+'%';}
function sjCls(x){return x==null?'':x>0?'up':x<0?'dn':'';}
function sjNum(x){return x==null?'':x.toLocaleString('ko-KR');}
function sjSortBy(c){if(c<0){sjSort={k:-1,d:1};}else if(sjSort.k===c){sjSort.d*=-1;}else{sjSort={k:c,d:(c===0||c===12)?1:-1};}sjRender();}
function sjGo(i){
  const r=SUJU.rows[i];if(!r[13])return;
  sjView('m');
  if(!N){alert('인원 데이터를 불러오는 중입니다. 잠시 후 다시 눌러주세요.');return;}
  preset(r[13]);window.scrollTo(0,0);
}
function sjRender(){
  const R=SUJU.rows,P=SUJU.months.length,q=normalize(document.getElementById('sjQ').value||''),only=document.getElementById('sjOrd').checked;
  const nv=id=>{const s=document.getElementById(id).value;return s===''?null:+s/100;};
  const iv=nv('sjInvMin'),ov=nv('sjOrdMin'),pm=nv('sjPenMin');
  let rows=R.map((r,i)=>{const a=r[7],b=r[6+P];return {r,i,pg:(a&&b!=null)?(b-a)/a:null};});
  rows=rows.filter(o=>{const r=o.r;
    if(q&&!normalize(r[0]).includes(q))return false;
    if(only&&r[5]==null)return false;
    if(iv!=null&&!(r[4]!=null&&r[4]>=iv))return false;
    if(ov!=null&&!(r[6]!=null&&r[6]>=ov))return false;
    if(pm!=null&&!(o.pg!=null&&o.pg>=pm))return false;
    return true;});
  const k=sjSort.k;
  if(k>=0){const get=o=>k===99?o.pg:o.r[k];rows.sort((a,b)=>{const x=get(a),y=get(b);if(x==null&&y==null)return a.i-b.i;if(x==null)return 1;if(y==null)return -1;return typeof x==='string'?sjSort.d*x.localeCompare(y,'ko'):sjSort.d*(x-y);});}
  const H=[['#',-1],['종목',0],['현재가',1],['변동율',2],['시가총액',3],['재고자산 증가율',4],['수주잔고',5],['수주잔고 증가율',6]]
    .concat(SUJU.months.map((m,j)=>['연금 '+m,7+j])).concat([['연금 증감',99],['매칭 사업장',7+P]]);
  let h='<tr>'+H.map(([t,c])=>'<th onclick="sjSortBy('+c+')"'+(c===0||c===7+P?' style="text-align:left"':'')+'>'+t+(sjSort.k===c&&c>=0?(sjSort.d>0?' ▲':' ▼'):'')+'</th>').join('')+'</tr>';
  rows.forEach((o,n)=>{const r=o.r;
    h+='<tr><td style="color:var(--tx2)">'+(n+1)+'</td><td class="nm">'+esc(r[0])+'</td><td>'+sjNum(r[1])+'</td>'
      +'<td class="'+sjCls(r[2])+'">'+sjPct(r[2])+'</td><td>'+sjMoney(r[3])+'</td>'
      +'<td class="'+sjCls(r[4])+'">'+sjPct(r[4])+'</td><td>'+sjMoney(r[5])+'</td>'
      +'<td class="'+sjCls(r[6])+'">'+sjPct(r[6])+'</td>';
    for(let j=7;j<7+P;j++)h+='<td class="pn">'+sjNum(r[j])+'</td>';
    h+='<td class="'+sjCls(o.pg)+'">'+sjPct(o.pg)+'</td>';
    h+='<td class="st'+(r[8+P]?' lk" onclick="sjGo('+o.i+')" title="인원검색에서 보기"':'"')+'>'+esc(r[7+P]||'')+'</td></tr>';});
  document.getElementById('sjT').innerHTML=h;
  document.getElementById('sjStat').textContent=rows.length.toLocaleString('ko-KR')+' / '+R.length.toLocaleString('ko-KR')+'종목';
}
if(SUJU){
  document.getElementById('vtabs').style.display='';
  document.getElementById('sjBase').textContent='· '+SUJU.base+' 분기 · '+SUJU.rows.length.toLocaleString('ko-KR')+'종목 · 국민연금 '+SUJU.months[0]+' ~ '+SUJU.months[SUJU.months.length-1];
}
"""

TITLE = '<h1>국민연금 사업장 인원 검색 대시보드</h1>'


def inject(html, fragment=False):
    """템플릿(fragment=False) 또는 아티팩트 조각(fragment=True)에 탭을 끼운다. 이미 있으면 그대로 둔다."""
    if 'id="sujuView"' in html:
        return html
    assert html.count(TITLE) == 1
    html = html.replace(TITLE, TITLE[:-5] + TABS + '</h1>', 1)
    i = html.index('</style>')
    html = html[:i] + CSS.strip() + '\n' + html[i:]
    anchor = '</div>\n<script id="D"' if fragment else '<script id="D"'
    assert html.count(anchor) == 1, anchor
    html = html.replace(anchor, VIEW + anchor, 1)
    end = '\nboot();\n</script>'
    assert html.count(end) == 1
    html = html.replace(end, '\n' + JS.strip() + end, 1)
    return html
