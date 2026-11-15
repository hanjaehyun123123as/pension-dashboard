# 통합 탭: 제목 옆 '통합' 작은 탭 + 종목당 한 줄 스크리닝 표
#   재고자산·수주잔고(DART 추이선 + 최근 4개 분기 값 + QoQ·YoY) + 국민연금(추이선 + 분기말 4개월 + MoM·YTD) + 시총
# 데이터 자리는 __TONGHAP__ (tools/tonghap.json 또는 null). 수주+재고 탭(suju_tab.py)이 먼저 들어가 있어야 한다.
# tonghap.json 만드는 곳: 내 드라이브\DART_리서치 codex\수주잔고_재고자산_추출\make_tonghap.py
CSS = r"""
#tgView{display:none}
html.tg-on #tgView{display:block}
html.tg-on #main,html.tg-on #loading,html.tg-on #gate,html.tg-on #sujuView{display:none!important}
#tgT{border-collapse:collapse;width:100%}
#tgT th{position:sticky;top:0;z-index:1;background:var(--panel2);user-select:none;white-space:nowrap;padding:5px 7px}
#tgT th[onclick]{cursor:pointer}
#tgT tr.h1 th{height:26px;text-align:center;color:var(--tx);border-bottom:1px solid var(--line)}
#tgT tr.h2 th{top:26px}
#tgT td{white-space:nowrap;padding:5px 7px}
#tgT td.nm{text-align:left;color:var(--tx);font-weight:600}
#tgT .mk{font-size:10px;color:var(--tx2);font-weight:400;margin-left:4px}
#tgT td.g0,#tgT th.g0{border-left:2px solid var(--line)}
#tgT td.sp{padding-right:2px}
#tgT td.sp svg{vertical-align:middle}
#tgT td.lv{color:var(--tx);font-weight:600}
#tgT td.up{color:var(--grn)}#tgT td.dn{color:var(--red)}
#tgT tr.r:hover td{background:var(--panel2)}
#tgT tr.r.op td{background:var(--panel2)}
.tgx{cursor:pointer;border:1px solid var(--line);border-radius:5px;padding:0 6px;color:var(--tx2);font-size:11px}
.tgx:hover{color:var(--tx);border-color:var(--acc)}
#tgT tr.det td{background:var(--panel);text-align:left;padding:10px 12px;white-space:normal}
.tgcharts{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:8px}
.tgch{font-size:11.5px;color:var(--tx2)}
.tgch b{color:var(--tx);font-weight:600;margin-right:6px}
.tgmini{border-collapse:collapse;font-size:11.5px;margin-top:6px;width:auto!important}
.tgmini td,.tgmini th{padding:2px 9px;text-align:right;border:none!important;position:static!important;background:none!important}
.tgmini th{color:var(--tx2);font-weight:400}
.tgmini td:first-child,.tgmini th:first-child{text-align:left;color:var(--tx2);padding-left:0}
.tgmini td.up{color:var(--grn)}.tgmini td.dn{color:var(--red)}
.tgc{display:inline-flex;gap:4px;align-items:center}
"""

PILL = '<span class="vtab" data-v="t" onclick="sjView(\'t\')">통합</span>'
PILL_AFTER = '<span class="vtab" data-v="s" onclick="sjView(\'s\')">수주+재고</span>'

OPTS = ('<option value="iq">재고 증가율 QoQ</option><option value="iy">재고 증가율 YoY</option>'
        '<option value="bq">수주 증가율 QoQ</option><option value="by">수주 증가율 YoY</option>'
        '<option value="pm">연금 MoM</option><option value="py">연금 YTD</option><option value="pv">연금 인원(명)</option>')


def cond(n, sel):
    o = OPTS.replace('value="%s"' % sel, 'value="%s" selected' % sel)
    return ('<span class="tgc">조건%d <select id="tgK%d" class="fin fsel" onchange="tgRender()">%s</select>'
            '<input id="tgV%d" class="fin" type="number" step="any" oninput="tgRender()"><span id="tgU%d">%%</span>'
            '<select id="tgO%d" class="fin fsel" onchange="tgRender()"><option value="ge">이상</option><option value="le">이하</option></select></span>'
            % (n, n, o, n, n, n))


VIEW = r"""<div id="tgView"><div class="card">
<div class="sjhead">
  <h2 style="margin:0 8px 0 0">통합 스크리닝 <span id="tgBase" style="font-weight:400"></span></h2>
</div>
<div class="sjbar">
  <input id="tgQ" placeholder="종목 검색" oninput="tgRender()" style="background:var(--panel2);border:1px solid var(--line);border-radius:6px;color:var(--tx);padding:5px 10px;font-size:13px;outline:none;width:150px">
  <span>시총 ≥ <input id="tgCap" class="fin" type="number" step="100" oninput="tgRender()">억</span>
  """ + cond(1, 'iq') + "\n  " + cond(2, 'py') + r"""
  <label><input type="checkbox" id="tgBl" onchange="tgRender()"> 수주잔고 있는 종목만</label>
  <label><input type="checkbox" id="tgW" onchange="tgRender()"> ⭐ 관심종목만 (<span id="tgWN">0</span>)</label>
  <span style="flex:1"></span><span id="tgStat"></span>
</div>
<div style="max-height:75vh;overflow:auto;border:1px solid var(--line);border-radius:8px"><table id="tgT"></table></div>
<div id="tgMore" style="margin-top:6px"></div>
<div style="margin-top:8px;font-size:11.5px;color:var(--tx2);line-height:1.6">열 제목 클릭 = 정렬 · ▸ = 그 종목 전 기간 차트·숫자 + 인원검색 연결 · ☆ = 관심종목(수주+재고 탭과 같은 목록)<br>
재고자산·수주잔고(억원): DART 사업·반기·분기보고서에서 직접 뽑은 값(연결 우선) · 추이선은 21~24년 연말 → 25.1Q부터 분기 · 숫자 4칸 = 최근 4개 분기 · QoQ = 그 회사 최근 분기의 직전 분기 대비 · YoY = 전년 같은 분기 대비 · 외화로만 적힌 수주잔고는 비어 있음(▸에 원문 금액)<br>
국민연금(명): 매칭 사업장 합계 · 추이선은 22.12·23.12·24.12 연말 → 25.12부터 월별 · 숫자 4칸 = 분기말 달 · MoM = 전월 대비 · YTD = 전년 12월 대비 · 시가총액은 수주+재고 탭(26.3) 기준</div>
</div></div>
"""

JS = r"""
const TG=__TONGHAP__;
let tgSort={k:'cap',d:-1},tgOpen=new Set(),tgAll=false,TGX=[];
function tgMoney(e){if(e==null)return '';const a=Math.abs(e);if(a>=10000)return (e/10000).toLocaleString('ko-KR',{maximumFractionDigits:2})+'조';if(a>=10)return Math.round(e).toLocaleString('ko-KR')+'억';return e.toLocaleString('ko-KR',{maximumFractionDigits:1})+'억';}
function tgPL(k){return TG.P0.has(k)?k.slice(0,2)+'년':k;}
function tgPrep(){
  const P=TG.P,ix={};P.forEach((k,i)=>ix[k]=i);
  const fq=P.find(k=>!k.endsWith('4Q'));TG.P0=new Set(P.filter(k=>fq&&k<fq&&k.endsWith('4Q')));
  const LP=P.length-1;TG.Q4=[LP-3,LP-2,LP-1,LP];
  const prevQ=k=>{let y=+k.slice(0,2),q=+k[3]-1;if(!q){y--;q=4;}return String(y).padStart(2,'0')+'.'+q+'Q';};
  const yoyQ=k=>String(+k.slice(0,2)-1).padStart(2,'0')+k.slice(2);
  const M=TG.M,ML=M.length-1,ly=+M[ML].split('.')[0],lm=+M[ML].split('.')[1],yb=M.indexOf((ly-1)+'.12');
  TG.PM4=[3,2,1,0].map(s=>{let y=ly,m=lm-3*s;while(m<=0){m+=12;y--;}return M.indexOf(y+'.'+m);});
  const gr=(a,i,k)=>{if(!a||i<0)return null;const j=ix[k];if(j==null)return null;const x=a[i],y=a[j];return (x!=null&&y)?(x-y)/Math.abs(y):null;};
  const last=a=>{if(!a)return -1;for(let i=a.length-1;i>=0;i--)if(a[i]!=null)return i;return -1;};
  TGX=TG.rows.map((r,i)=>{const I=r[3]||null,B=r[4]||null,Pn=r[5]||null,li=last(I),bi=last(B);
    const pv=Pn?Pn[ML]:null,pp=Pn?Pn[ML-1]:null,p0=(Pn&&yb>=0)?Pn[yb]:null;
    const o={i,r,nn:normalize(r[0]),cap:r[2],iv:li>=0?I[li]:null,iq:gr(I,li,li>=0?prevQ(P[li]):''),iy:gr(I,li,li>=0?yoyQ(P[li]):''),
      bv:bi>=0?B[bi]:null,bq:gr(B,bi,bi>=0?prevQ(P[bi]):''),by:gr(B,bi,bi>=0?yoyQ(P[bi]):''),
      pv,pm:(pv!=null&&pp)?(pv-pp)/pp:null,py:(pv!=null&&p0)?(pv-p0)/p0:null};
    for(let j=0;j<4;j++){const q=TG.Q4[j],m=TG.PM4[j];o['i'+j]=(I&&q>=0)?I[q]:null;o['b'+j]=(B&&q>=0)?B[q]:null;o['p'+j]=(Pn&&m>=0)?Pn[m]:null;}
    return o;});
}
function tgSpk(a){if(!a)return '';const v=[];a.forEach((x,j)=>{if(x!=null)v.push([j,x]);});
  if(v.length<2)return '';
  let lo=Infinity,hi=-Infinity;v.forEach(t=>{if(t[1]<lo)lo=t[1];if(t[1]>hi)hi=t[1];});
  const s=(a.length-1)||1,p=v.map(([j,x])=>((j/s*56+2).toFixed(1))+','+((17-(hi>lo?(x-lo)/(hi-lo):.5)*14).toFixed(1)));
  const L=p[p.length-1].split(',');
  return '<svg width="60" height="20"><polyline points="'+p.join(' ')+'" fill="none" stroke="var(--acc)" stroke-width="1.3" stroke-linejoin="round"/><circle cx="'+L[0]+'" cy="'+L[1]+'" r="2" fill="var(--acc)"/></svg>';}
function tgChart(a,labs,fmt,line){
  const W=340,H=120,pl=4,pb=16,pt=16;if(!a||!a.some(x=>x!=null))return '<div style="width:'+W+'px;color:var(--tx2)">자료 없음</div>';
  const n=a.length,bw=(W-pl*2)/n;let hi=0,lo=0;a.forEach(x=>{if(x!=null){if(x>hi)hi=x;if(x<lo)lo=x;}});
  if(line){lo=Infinity;a.forEach(x=>{if(x!=null&&x<lo)lo=x;});lo=lo-(hi-lo)*0.15;}
  const y=x=>pt+(H-pt-pb)*(1-(hi>lo?(x-lo)/(hi-lo):.5)),y0=y(Math.max(lo,0));
  let s='<svg width="'+W+'" height="'+H+'" style="display:block">',pts=[];
  a.forEach((x,j)=>{const cx=pl+bw*j+bw/2;if(x==null)return;
    if(line){pts.push(cx.toFixed(1)+','+y(x).toFixed(1));s+='<circle cx="'+cx.toFixed(1)+'" cy="'+y(x).toFixed(1)+'" r="2.4" fill="var(--acc)"><title>'+labs[j]+' '+fmt(x)+'</title></circle>';}
    else{const t=Math.min(y(x),y0),h=Math.max(1,Math.abs(y0-y(x)));s+='<rect x="'+(cx-bw*0.34).toFixed(1)+'" y="'+t.toFixed(1)+'" width="'+(bw*0.68).toFixed(1)+'" height="'+h.toFixed(1)+'" rx="2" fill="var(--acc)" opacity="'+(j===n-1?1:0.55)+'"><title>'+labs[j]+' '+fmt(x)+'</title></rect>';}});
  if(line)s='<svg width="'+W+'" height="'+H+'" style="display:block"><polyline points="'+pts.join(' ')+'" fill="none" stroke="var(--acc)" stroke-width="1.5"/>'+s.slice(s.indexOf('>')+1);
  const li=a.length-1-[...a].reverse().findIndex(x=>x!=null),fi=a.findIndex(x=>x!=null);
  s+='<text x="'+(pl+bw*li+bw/2)+'" y="11" font-size="10.5" fill="var(--tx)" text-anchor="end">'+fmt(a[li])+'</text>';
  s+='<text x="'+(pl+bw*fi+bw/2)+'" y="'+(H-3)+'" font-size="10" fill="var(--tx2)">'+labs[fi]+'</text><text x="'+(pl+bw*li+bw/2)+'" y="'+(H-3)+'" font-size="10" fill="var(--tx2)" text-anchor="end">'+labs[li]+'</text>';
  return s+'</svg>';}
function tgDet(o){
  const r=o.r,P=TG.P.map(tgPL),M=TG.M,I=r[3]||null,B=r[4]||null,Pn=r[5]||null;
  const n0=x=>x==null?'':Math.round(x).toLocaleString('ko-KR');
  const chg=a=>a?a.map((x,j)=>{if(!j)return null;const y=a[j-1];return (x!=null&&y)?(x-y)/Math.abs(y):null;}):[];
  const row=(t,a,f)=>'<tr><td>'+t+'</td>'+a.map(x=>'<td'+(f===sjPct?' class="'+sjCls(x)+'"':'')+'>'+(x==null?'':f(x))+'</td>').join('')+'</tr>';
  let h='<div class="tgcharts"><div class="tgch"><b>재고자산</b>억원'+tgChart(I,P,tgMoney)+'</div><div class="tgch"><b>수주잔고</b>억원'+tgChart(B,P,tgMoney)+'</div><div class="tgch"><b>국민연금</b>명'+tgChart(Pn,M,x=>Math.round(x).toLocaleString('ko-KR')+'명',1)+'</div></div>';
  h+='<table class="tgmini"><tr><th>억원</th>'+P.map(x=>'<th>'+x+'</th>').join('')+'</tr>';
  if(I)h+=row('재고자산',I,tgMoney)+row('　전기 대비',chg(I),sjPct);
  if(B)h+=row('수주잔고',B,tgMoney)+row('　전기 대비',chg(B),sjPct);
  h+='</table>';
  if(Pn)h+='<table class="tgmini"><tr><th>명</th>'+M.map(x=>'<th>'+x+'</th>').join('')+'</tr>'+row('국민연금',Pn,n0)+row('　전기 대비',chg(Pn),sjPct)+'</table>';
  if(r[8])h+='<div style="margin-top:6px;color:var(--tx2)">수주 메모(외화 등): '+esc(r[8])+'</div>';
  if(r[6])h+='<div style="margin-top:8px;color:var(--tx2)">국민연금 매칭 사업장: '+esc(r[6])+(r[7]?' <span class="chip" onclick="tgGo('+o.i+')">인원검색에서 보기</span>':'')+'</div>';
  return h;}
function tgStar(i){const n=TG.rows[i][0],k=sjW.indexOf(n);if(k>=0)sjW.splice(k,1);else sjW.push(n);sjWSave();tgRender();}
function tgTog(i){if(tgOpen.has(i))tgOpen.delete(i);else tgOpen.add(i);tgRender();}
function tgGo(i){const r=TG.rows[i];if(!r[7])return;sjView('m');if(!N){alert('인원 데이터를 불러오는 중입니다. 잠시 후 다시 눌러주세요.');return;}preset(r[7]);window.scrollTo(0,0);}
function tgSortBy(k){if(tgSort.k===k)tgSort.d*=-1;else tgSort={k,d:(k==='n'||k==='#')?1:-1};tgRender();}
function tgRender(){
  if(!TGX.length)tgPrep();
  const q=normalize(document.getElementById('tgQ').value||''),cap=document.getElementById('tgCap').value,ws=new Set(sjW);
  const wOnly=document.getElementById('tgW').checked,blOnly=document.getElementById('tgBl').checked;
  const cs=[1,2].map(n=>{const k=document.getElementById('tgK'+n).value;document.getElementById('tgU'+n).textContent=k==='pv'?'명':'%';
    return {k,v:document.getElementById('tgV'+n).value,o:document.getElementById('tgO'+n).value};}).filter(c=>c.v!=='');
  let R=TGX.filter(o=>{
    if(q&&!o.nn.includes(q))return false;
    if(cap!==''&&!(o.cap!=null&&o.cap>=+cap))return false;
    if(blOnly&&o.bv==null)return false;
    if(wOnly&&!ws.has(o.r[0]))return false;
    for(const c of cs){let x=o[c.k];if(x==null)return false;if(c.k!=='pv')x*=100;if(c.o==='ge'?x<+c.v:x>+c.v)return false;}
    return true;});
  const k=tgSort.k;
  if(k!=='#'){const g=k==='n'?(o=>o.r[0]):(o=>o[k]);R.sort((a,b)=>{const x=g(a),y=g(b);if(x==null&&y==null)return a.i-b.i;if(x==null)return 1;if(y==null)return -1;return typeof x==='string'?tgSort.d*x.localeCompare(y,'ko'):tgSort.d*(x-y);});}
  const QL=TG.Q4.map(j=>j>=0?tgPL(TG.P[j]):''),ML=TG.PM4.map(j=>j>=0?TG.M[j]:'');
  const th=(t,c,cls,extra)=>'<th'+(cls?' class="'+cls+'"':'')+(c?' onclick="tgSortBy(\''+c+'\')"':'')+(extra||'')+'>'+t+(c&&tgSort.k===c&&c!=='#'?(tgSort.d>0?' ▲':' ▼'):'')+'</th>';
  const grp=(p,labs,g1,g2)=>th('추이','','g0')+labs.map((l,j)=>th(l,p+j)).join('')+th(g1[0],g1[1])+th(g2[0],g2[1]);
  let h='<tr class="h1">'+th('#','#','',' rowspan="2"')+th('종목','n','',' rowspan="2" style="text-align:left"')+th('시가총액','cap','',' rowspan="2"')
    +'<th class="g0" colspan="7">재고자산 (억원)</th><th class="g0" colspan="7">수주잔고 (억원)</th><th class="g0" colspan="7">국민연금 (명)</th><th rowspan="2"></th></tr>'
    +'<tr class="h2">'+grp('i',QL,['QoQ','iq'],['YoY','iy'])+grp('b',QL,['QoQ','bq'],['YoY','by'])+grp('p',ML,['MoM','pm'],['YTD','py'])+'</tr>';
  const NC=25,lim=tgAll?R.length:Math.min(R.length,400);
  const pc=x=>'<td class="'+sjCls(x)+'">'+sjPct(x)+'</td>';
  const vals=(o,p,f)=>[0,1,2,3].map(j=>'<td'+(j===3?' class="lv"':'')+'>'+f(o[p+j])+'</td>').join('');
  const pn=x=>x==null?'':x.toLocaleString('ko-KR');
  for(let n=0;n<lim;n++){const o=R[n],r=o.r,on=ws.has(r[0]),op=tgOpen.has(o.i);
    h+='<tr class="r'+(op?' op':'')+'"><td style="color:var(--tx2)">'+(n+1)+'</td>'
      +'<td class="nm"><span class="sjst'+(on?' on':'')+'" onclick="tgStar('+o.i+')" title="'+(on?'관심종목에서 빼기':'관심종목에 추가')+'">'+(on?'★':'☆')+'</span>'+esc(r[0])+'<span class="mk">'+(r[1]==='P'?'코스피':r[1]==='Q'?'코스닥':'')+'</span></td>'
      +'<td>'+tgMoney(o.cap)+'</td>'
      +'<td class="sp g0">'+tgSpk(r[3])+'</td>'+vals(o,'i',tgMoney)+pc(o.iq)+pc(o.iy)
      +'<td class="sp g0">'+(r[4]?tgSpk(r[4]):(r[8]?'<span style="color:var(--tx2)" title="'+esc(r[8])+'">외화</span>':''))+'</td>'+vals(o,'b',tgMoney)+pc(o.bq)+pc(o.by)
      +'<td class="sp g0">'+tgSpk(r[5])+'</td>'+vals(o,'p',pn)+pc(o.pm)+pc(o.py)
      +'<td><span class="tgx" onclick="tgTog('+o.i+')" title="전 기간 차트·숫자">'+(op?'▾':'▸')+'</span></td></tr>';
    if(op)h+='<tr class="det"><td colspan="'+NC+'">'+tgDet(o)+'</td></tr>';}
  if(!R.length)h+='<tr><td colspan="'+NC+'" style="text-align:left;color:var(--tx2);padding:14px">'+(wOnly&&!sjW.length?'관심종목이 비어 있습니다. 종목 이름 앞의 ☆를 누르거나 수주+재고 탭의 ⭐ 관심종목에서 붙여넣어 추가하세요.':'조건에 맞는 종목이 없습니다')+'</td></tr>';
  document.getElementById('tgT').innerHTML=h;
  document.getElementById('tgMore').innerHTML=R.length>lim?'<span class="chip" onclick="tgAll=true;tgRender()">나머지 '+(R.length-lim).toLocaleString('ko-KR')+'종목 더 보기</span>':'';
  document.getElementById('tgStat').textContent=R.length.toLocaleString('ko-KR')+' / '+TGX.length.toLocaleString('ko-KR')+'종목';
  document.getElementById('tgWN').textContent=sjW.length;
}
if(TG){
  const _sjView0=sjView;
  sjView=function(v){
    document.documentElement.classList.toggle('tg-on',v==='t');
    _sjView0(v==='t'?'_':v);
    document.querySelectorAll('.vtab').forEach(t=>t.classList.toggle('on',t.dataset.v===v));
    if(v==='t')tgRender();
  };
  document.getElementById('vtabs').style.display='';
  document.getElementById('tgBase').textContent='· 재고·수주 '+tgPLraw(TG.P[0])+' ~ '+TG.P[TG.P.length-1]+' (DART 보고서) · 국민연금 '+TG.M[0]+' ~ '+TG.M[TG.M.length-1]+' · '+TG.rows.length.toLocaleString('ko-KR')+'종목';
}else{const p=document.querySelector('.vtab[data-v="t"]');if(p)p.remove();}
function tgPLraw(k){return k.endsWith('4Q')?k.slice(0,2)+'년':k;}
"""


def replace_data(html, data):
    """이미 통합 탭이 들어간 HTML(아티팩트를 read로 받은 파일 등)에서 TG 데이터만 새 tonghap.json 내용으로 바꾼다.
    분기 갱신 때: make_tonghap.py → 아티팩트 read → replace_data → 같은 url로 publish"""
    i = html.index('const TG=') + len('const TG=')
    j = html.index(';\nlet tgSort=', i)
    return html[:i] + data + html[j:]


def strip(html):
    """이미 들어간 통합 탭(버전 무관)을 걷어낸다 → 새 버전을 다시 inject할 때 사용"""
    if 'id="tgView"' not in html:
        return html
    html = html.replace(PILL, '', 1)
    a = html.index('#tgView{display:none}')
    b = html.index('</style>', a)
    html = html[:a] + html[b:]
    a = html.index('<div id="tgView">')
    b = html.index('</div></div>\n', a) + len('</div></div>\n')
    html = html[:a] + html[b:]
    a = html.index('const TG=')
    b = html.index("function tgPLraw(k){return k.endsWith('4Q')?k.slice(0,2)+'년':k;}", a)
    b = html.index('\n', b) + 1
    return html[:a].rstrip('\n') + '\n' + html[b:]


def inject(html, fragment=False):
    """수주+재고 탭이 들어간 템플릿(fragment=False) 또는 아티팩트 조각(fragment=True)에 통합 탭을 끼운다. 이미 있으면 걷어내고 새로."""
    html = strip(html)
    assert html.count(PILL_AFTER) == 1, 'suju 탭이 먼저 있어야 함'
    html = html.replace(PILL_AFTER, PILL_AFTER + PILL, 1)
    i = html.index('</style>')
    html = html[:i] + CSS.strip() + '\n' + html[i:]
    anchor = '</div>\n<script id="D"' if fragment else '<script id="D"'
    assert html.count(anchor) == 1, anchor
    html = html.replace(anchor, VIEW + anchor, 1)
    end = '\nboot();\n</script>'
    assert html.count(end) == 1
    html = html.replace(end, '\n' + JS.strip() + end, 1)
    return html
