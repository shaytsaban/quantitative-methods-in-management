# Headless test of the deck: layout overflow per slide (first view, all revealed, all solved), reveals, every activity
# (right answer accepted, wrong answer rejected), direction of every math run, forbidden characters.
import json, os, re, subprocess, sys, tempfile, html as hh
H = os.path.dirname(os.path.abspath(__file__))
ARG = sys.argv[1] if len(sys.argv) > 1 else '1'
SRC = os.path.join(H, '..', 'lectures', f'lecture-{ARG}', 'presentation.html') if ARG.isdigit() else ARG
LESSON = int(ARG) if ARG.isdigit() else int((re.search(r'lecture-(\d+)', ARG) or re.search(r'(\d+)', os.path.basename(ARG)) or [0, 1])[1])
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TEST = r'''
window.onerror=(m,u,l,c,e)=>{document.documentElement.setAttribute('data-err',m+' @'+l+':'+c);};
(async function(){
const D=window.__deck,R={errors:[],overflow:[],small:[],mc:[],act:[],chars:[],bidi:[],wide:[],reveal:[]};
const st=document.createElement('style');st.textContent='*{transition:none!important;animation:none!important}';document.head.appendChild(st);
const stage=document.getElementById('stage');
const rel=e=>{const s=stage.getBoundingClientRect(),r=e.getBoundingClientRect(),k=s.width/1280;return{t:(r.top-s.top)/k,b:(r.bottom-s.top)/k,l:(r.left-s.left)/k,r:(r.right-s.left)/k,w:r.width/k,h:r.height/k};};
function measure(s,i,tag){const limit=s.querySelector('.ft')?720-37:716;let worst=0,who='',wl=0,wr=1280;
 s.querySelectorAll('*').forEach(e=>{if(e.closest('.ft')||e.closest('.pd-num')||e.closest('.orb')||e.closest('.hints')||e.closest('[hidden]')||e.closest('.toon')||e.closest('svg')&&e.tagName!=='svg')return;const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')return;const r=rel(e);if(!r.w&&!r.h)return;
  if(r.b>worst){worst=r.b;who=(e.className||e.tagName)+'';}if(r.l<wl)wl=r.l;if(r.r>wr)wr=r.r;});
 if(worst>limit+.5||wl<-.5||wr>1280.5)R.overflow.push({n:i+1,id:s.id,tag,bottom:Math.round(worst),limit,who:String(who).slice(0,40),l:Math.round(wl),r:Math.round(wr)});}
// content wider than its box (clipped or spilling equations and tables)
function wide(s){s.querySelectorAll('.eq,.opx,.tq,.ctab,.gq,.tbl2,.anat,.mach,.twoway').forEach(e=>{if(e.closest('[hidden]'))return;const box=e.closest('.card,.wkr,.tstep,.rule,.try,.qr,.solw,.col,.slide');const g=document.createRange();g.selectNodeContents(e);const a=g.getBoundingClientRect(),b=box.getBoundingClientRect();if(a.width&&(a.left<b.left-1.5||a.right>b.right+1.5))R.wide.push({id:s.id,t:e.textContent.slice(0,40),over:Math.round(Math.max(b.left-a.left,a.right-b.right))});});}
// direction by measurement: inside every math run the first character sits left of the last one, and the run is one line
function bidi(s){s.querySelectorAll('.eq,.m,.n,.opx,.tw-e,.frac>span').forEach(e=>{if(e.closest('[hidden]')||e.closest('.hints'))return;const cs=getComputedStyle(e);if(cs.direction!=='ltr'||!/isolate|plaintext/.test(cs.unicodeBidi)&&cs.display==='inline')R.bidi.push({id:s.id,why:'not an isolated ltr run',t:e.textContent.slice(0,30)});
 const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);const ts=[];let t;while(t=w.nextNode())if(t.nodeValue.trim()&&!t.parentElement.closest('.mh'))ts.push(t);if(ts.length<1)return;
 const pos=[];const fr=new Set();ts.forEach(t=>{const f=t.parentElement.closest('.frac');if(f&&e.contains(f)&&f!==e&&!e.matches('.frac>span')){if(fr.has(f))return;fr.add(f);const r=f.getBoundingClientRect();pos.push({x:r.left,y:r.top,c:'[frac]',sup:false});return;}const v=t.nodeValue;for(let j=0;j<v.length;j++){if(!v[j].trim())continue;const g=document.createRange();g.setStart(t,j);g.setEnd(t,j+1);const r=g.getBoundingClientRect();if(r.width)pos.push({x:r.left,y:r.top,c:v[j],sup:!!t.parentElement.closest('sup')});}});
 for(let j=1;j<pos.length;j++){if(pos[j].x<pos[j-1].x-0.5&&!(e.classList.contains('eq')&&Math.abs(pos[j].y-pos[j-1].y)>16&&!pos[j].sup&&!pos[j-1].sup)){R.bidi.push({id:s.id,why:'order',t:e.textContent.slice(0,40),at:pos[j-1].c+pos[j].c});break;}}
 if(e.classList.contains('m')||e.classList.contains('n')){const rs=e.getClientRects();if(rs.length>1&&Math.abs(rs[0].top-rs[rs.length-1].top)>14)R.bidi.push({id:s.id,why:'wrapped',t:e.textContent.slice(0,40)});}});
 // a minus or an equals sign loose in Hebrew text (outside an ltr run) would be mirrored
 const w=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let t;while(t=w.nextNode()){const p=t.parentElement;if(!p||p.closest('svg,script,style,.eq,.m,.n,.opx,.op,.gq,.kp,[dir=ltr],input,.hints'))continue;if(/[−=+^<>≠]/.test(t.nodeValue)||/\d\s*-\s*\d/.test(t.nodeValue))R.bidi.push({id:s.id,why:'loose sign in Hebrew text',t:t.nodeValue.trim().slice(0,40)});}}
function small(s){const w=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let n;const seen={};while(n=w.nextNode()){if(!n.nodeValue.trim())continue;const p=n.parentElement;if(p.closest('.ft,sup,sub,tspan,svg,.hints,[hidden],.kp,.rn,.fn,.tn,.wn>b'))continue;const f=parseFloat(getComputedStyle(p).fontSize);if(f<16.4)seen[Math.round(f*10)/10]=(n.nodeValue.trim().slice(0,18));}if(Object.keys(seen).length)R.small.push({id:s.id,seen});}
const A=(id,kind,ok,more)=>R.act.push(Object.assign({id,kind,ok:!!ok},more||{}));
const MAN=__MAN__;const byId={};MAN.forEach(m=>byId[m.id]=m);const plain=e=>e.textContent.replace(/\s+/g,' ').trim();
function stateOf(b,fb){if(fb.classList.contains('good'))return b.classList.contains('solved')?'ok':'good-but-not-solved';if(fb.classList.contains('half'))return 'half';if(fb.classList.contains('wrong'))return fb.textContent.includes('לא הצלחנו לקרוא')?'bad':'no';return 'empty';}
async function runTry2(b,m){const ins=[...b.querySelectorAll('input.ex')],fb=b.querySelector('.fbbar'),chk=b.querySelector('.chk');const bad=[];
 const keys=ins.map(i=>i.dataset.v);if(keys.join()!==Object.keys(m.a).join())bad.push({why:'boxes',keys});
 ins.forEach(i=>{if(i.dataset.a!==m.a[i.dataset.v])bad.push({why:'data-a differs',v:i.dataset.v});});
 m.cases.forEach(([vals,exp,what],k)=>{ins.forEach(i=>{i.value=vals[i.dataset.v];i.dispatchEvent(new Event('input',{bubbles:true}));});
  if(k%2)ins[ins.length-1].dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));else chk.click();const got=stateOf(b,fb);
  if(exp.startsWith('trap:')){if(got!=='no'||!plain(fb).includes(exp.slice(5)))bad.push({vals,exp,got,fb:plain(fb).slice(0,70)});}else if(got!==exp)bad.push({vals,exp,got,what,fb:plain(fb).slice(0,70)});});
 const nh=b.querySelectorAll('.hints>div').length;if(nh!==m.nhints)bad.push({why:'hints'});if(nh){b.querySelector('.hintb').click();if(!plain(fb).includes('רמז 1'))bad.push({why:'hint not shown'});}
 const ns=b.querySelectorAll('.tsol .tstep').length;if(ns!==m.nsteps||!ns)bad.push({why:'steps',ns});
 b.querySelector('.solb').click();const pop=document.getElementById('moreov');const nx=pop.querySelector('.nxs');for(let k=1;k<ns;k++)nx.click();if(pop.querySelectorAll('.tstep.show').length!==ns)bad.push({why:'popup stages'});pop.classList.remove('open');
 ins.forEach(i=>{i.value=m.a[i.dataset.v];});chk.click();if(stateOf(b,fb)!=='ok')bad.push({why:'final answer'});
 A(b.id,'try2',!bad.length,{cases:m.cases.length,bad});}
async function runTry(b){const m=byId[b.id];if(m&&m.kind==='try2')return runTry2(b,m);if(!m){A(b.id,'try',false,{why:'no manifest entry'});return;}const i=b.querySelector('input.ex'),fb=b.querySelector('.fbbar'),chk=b.querySelector('.chk');const bad=[];
 if(b.dataset.a!==m.a)bad.push({why:'data-a differs',dom:b.dataset.a,man:m.a});
 m.cases.forEach(([v,exp,what],k)=>{i.value=v;i.dispatchEvent(new Event('input',{bubbles:true}));if(k%2)i.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));else chk.click();let got=stateOf(b,fb);
  if(exp.startsWith('trap:')){if(got!=='no'||!plain(fb).includes(exp.slice(5).replace(/\s+/g,' ').trim()))bad.push({v,exp,got,fb:plain(fb).slice(0,60),what});}
  else if(got!==exp)bad.push({v,exp,got,what});});
 const hb=b.querySelector('.hintb'),nh=b.querySelectorAll('.hints>div').length;if(nh!==m.nhints)bad.push({why:'hints',nh});if(nh){hb.click();if(!fb.classList.contains('half')||!plain(fb).includes('רמז 1'))bad.push({why:'hint not shown'});}
 const ns=b.querySelectorAll('.tsol .tstep').length;if(ns!==m.nsteps||!ns)bad.push({why:'steps',ns,man:m.nsteps});
 if(b.classList.contains('big')){const sb=b.querySelector('.solb');sb.click();if(b.querySelectorAll('.tsol .tstep.show').length!==1)bad.push({why:'first stage'});for(let k=1;k<ns;k++)sb.click();if(b.querySelectorAll('.tsol .tstep.show').length!==ns||!sb.disabled)bad.push({why:'stages'});}
 else{b.querySelector('.solb').click();const pop=document.getElementById('moreov');const nx=pop.querySelector('.nxs');if(!pop.classList.contains('open')||pop.querySelectorAll('.tstep.show').length!==1)bad.push({why:'popup first stage'});for(let k=1;k<ns;k++)nx.click();if(pop.querySelectorAll('.tstep.show').length!==ns)bad.push({why:'popup stages'});const r=pop.querySelector('.more-box').getBoundingClientRect();if(r.bottom>innerHeight||r.top<0)bad.push({why:'popup outside the screen'});pop.classList.remove('open');}
 // keypad: appears on focus and writes into the box
 i.value='';i.focus();if(!document.hasFocus())i.dispatchEvent(new FocusEvent('focusin',{bubbles:true}));const kp=document.querySelector('.kp');const kb=kp&&kp.querySelector('button');if(!kp||getComputedStyle(kp).display==='none'||!kb)bad.push({why:'keypad missing'});else{kb.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true}));if(i.value!==kb.dataset.k)bad.push({why:'keypad did not type',v:i.value});}
 i.focus();if(!document.hasFocus())i.dispatchEvent(new FocusEvent('focusin',{bubbles:true}));i.value='7x+123';chk.click();await new Promise(r=>setTimeout(r,0));{const kr=document.querySelector('.kp').getBoundingClientRect(),fr=fb.getBoundingClientRect(),ir=i.getBoundingClientRect();const hit=(p,q)=>!(p.right<=q.left||q.right<=p.left||p.bottom<=q.top||q.bottom<=p.top);if(hit(kr,fr)||hit(kr,ir))bad.push({why:'keypad covers the feedback or the answer box'});if(kr.bottom>innerHeight||kr.top<0)bad.push({why:'keypad outside the screen'});}
 i.value=m.a;i.dispatchEvent(new Event('input',{bubbles:true}));chk.click();if(stateOf(b,fb)!=='ok')bad.push({why:'final answer'});
 A(b.id,'try',!bad.length,{cases:m.cases.length,bad});}
async function solve(s){
 for(const b of s.querySelectorAll('.try'))await runTry(b);
 s.querySelectorAll('.cells').forEach(b=>{const m=byId[b.id];const ins=[...b.querySelectorAll('input.ex')],fb=b.querySelector('.fbbar');const bad=[];if(!m||m.ans.length!==ins.length){A(b.id,'cells',false,{why:'manifest'});return;}
  ins.forEach((i,k)=>{if(i.dataset.a!==m.ans[k])bad.push({why:'data-a',k});i.value='('+m.ans[k]+')+1';});b.querySelector('.chk').click();if(!fb.classList.contains('wrong')||!ins.every(i=>i.classList.contains('badc')||i.classList.contains('halfc')))bad.push({why:'wrong values accepted'});
  b.querySelector('.rst').click();if(!ins.every(i=>!i.value))bad.push({why:'reset'});
  ins.forEach((i,k)=>{i.value=k?m.ans[k]:'';});b.querySelector('.chk').click();if(b.classList.contains('solved'))bad.push({why:'solved with an empty cell'});
  ins.forEach((i,k)=>{i.value=m.ans[k];});b.querySelector('.chk').click();if(!b.classList.contains('solved')||!ins.every(i=>i.classList.contains('good')))bad.push({why:'right values rejected',fb:plain(fb).slice(0,50)});
  b.querySelector('.rst').click();b.querySelector('.shw').click();if(!b.classList.contains('solved'))bad.push({why:'show answers'});A(b.id,'cells',!bad.length,{n:ins.length,bad});});
 s.querySelectorAll('.ops').forEach(b=>{const m=byId[b.id];const C=JSON.parse(b.dataset.cfg),fb=b.querySelector('.fbbar');let ok=!!m&&m.kinds.join()===C.states.map(x=>x.kind).join(),wrongSeen=0;
  for(let k=0;k<C.states.length;k++){const ops=[...b.querySelectorAll('.opx .op')];ops.filter(o=>+o.dataset.i!==C.states[k].ok).forEach(w=>{w.click();if(!fb.classList.contains('wrong')||b.__k()!==k)ok=false;wrongSeen++;});
   const r=ops.find(o=>+o.dataset.i===C.states[k].ok);if(!r||r.dataset.k!==C.states[k].kind){ok=false;break;}r.click();if(b.__k()!==k+1)ok=false;}
  const fin=plain(b.querySelector('.opx')).replace('−','-');ok=ok&&b.classList.contains('solved')&&b.querySelectorAll('.oplog li').length===C.states.length&&m&&fin===m.final;
  b.querySelector('.rst').click();if(b.__k()!==0)ok=false;for(let k=0;k<C.states.length;k++)b.querySelector('.shw').click();if(!b.classList.contains('solved'))ok=false;A(b.id,'ops',ok,{wrongSeen,fin});});
 s.querySelectorAll('.sorter').forEach(b=>{const m=byId[b.id];let ok=!!m;const rows=[...b.querySelectorAll('.srow')];if(m&&m.rows.length!==rows.length)ok=false;rows.forEach((r,k)=>{const os=[...r.querySelectorAll('.so')],a=+r.dataset.a;if(m&&plain(os[a])!==m.rows[k].replace(/\s+/g,' ').trim())ok=false;os.forEach((o,j)=>{if(j!==a){o.click();if(r.classList.contains('solved'))ok=false;}});os[a].click();if(!r.classList.contains('solved'))ok=false;});A(b.id,'sorter',ok&&b.classList.contains('solved'));});
 s.querySelectorAll('.mc').forEach(q=>{const m=byId[q.id];const a=+q.dataset.a,os=[...q.querySelectorAll('.o')];let ok=!!m&&os.length===m.n&&plain(os[a]).slice(3)===m.right.replace(/\s+/g,' ').trim();const w=(a+1)%os.length;os[w].click();ok=ok&&os[w].classList.contains('bad')&&os[a].classList.contains('ok')&&getComputedStyle(q.querySelector('.w')).display!=='none';
  q.classList.remove('done');os.forEach(o=>o.classList.remove('ok','bad'));os[a].click();ok=ok&&os[a].classList.contains('ok')&&!os.some(o=>o.classList.contains('bad'));R.mc.push({id:q.id,ok,a,n:os.length});});}
for(let i=0;i<D.slides.length;i++){const s=D.slides[i];D.show(i);measure(s,i,'first');D.setAll(s,true);measure(s,i,'open');wide(s);bidi(s);small(s);
 const txt=s.textContent;[['em','—'],['maqaf','־'],['en','–'],['ell','…'],['arrow','→'],['q1','“'],['q2','”'],['hyphenminus-in-math',null]].forEach(([k,c])=>{if(c&&txt.includes(c))R.chars.push({id:s.id,k});});
 s.querySelectorAll('.eq,.m').forEach(e=>{if(/-/.test(e.textContent))R.chars.push({id:s.id,k:'ascii minus in math: '+e.textContent.slice(0,20)});});
 await solve(s);measure(s,i,'solved');wide(s);
 }
// reveals: walking with next() shows every group, one per click, and reaches the last slide
D.show(0);let k=0,per={};while(D.cur()<D.slides.length-1&&k<3000){const c=D.cur();D.next();k++;per[c]=(per[c]||0)+1;}
R.walk={clicks:k,end:D.cur(),slides:D.slides.length};
D.slides.forEach((s,i)=>{const g=D.groups(s).length;if((per[i]||0)!==g+1&&i<D.slides.length-1)R.reveal.push({id:s.id,groups:g,clicks:per[i]});});
R.counts={slides:D.slides.length,tries:document.querySelectorAll('.try').length,cells:document.querySelectorAll('.cells').length,ops:document.querySelectorAll('.ops').length,sorters:document.querySelectorAll('.sorter').length,mc:document.querySelectorAll('.mc').length,math:document.querySelectorAll('.eq,.m').length,steps:document.querySelectorAll('.st').length};
document.documentElement.setAttribute('data-test',JSON.stringify(R));
})();
'''

sys.path.insert(0, H)
from qlib import same, ev, strip
MANI = json.load(open(os.path.join(H, 'tests', f'manifest-{LESSON}.json'), encoding='utf8'))
FLIP = {'<': '>', '>': '<', '≤': '≥', '≥': '≤'}
def _terms(a):
    out, d, cur = [], 0, ''
    for i, c in enumerate(a):
        if c == '(': d += 1
        elif c == ')': d -= 1
        if c in '+-' and d == 0 and i and a[i - 1] not in '^*/(':
            out.append(cur); cur = c
        else: cur += c
    out.append(cur); return out
def cases_ineq(m):
    a = m['a']
    mm = re.fullmatch(r'([a-z])(<|>|≤|≥)(.+)', a); v, op, b = mm.groups()
    other = {'<': '≤', '≤': '<', '>': '≥', '≥': '>'}[op]
    cs = [(a, 'ok', 'the answer'), (f' {v} {op} {b} ', 'ok', 'with spaces'), (f'{b}{FLIP[op]}{v}', 'ok', 'written from the other side'),
          (f'{v}{FLIP[op]}{b}', 'trap:המספר נכון, אבל הכיוון', 'direction flipped'), (f'{v}{other}{b}', 'trap:המספר והכיוון נכו', 'strict and non strict'),
          (f'{v}{op}({b})+1', 'no', 'wrong bound'), (b, 'half', 'only the number'), ('', 'empty', 'empty'), (f'{v}{op}', 'bad', 'unreadable'),
          ('w' + op + b, 'half', 'another letter'), (f'{v}{op}({b})+0', 'half', 'bound still an exercise')]
    if op in '≤≥': cs.append((f'{v}{op.replace("≤", "<=").replace("≥", ">=")}{b}', 'ok', 'typed as <= or >='))
    tv = {x for x, _ in m['traps']}
    cs = [c for c in cs if c[0] not in tv]
    for x, msg in m['traps']: cs.append((x, 'trap:' + re.sub('<[^>]+>', '', msg)[:14], 'trap'))
    return cs


def cases(m):
    a, f = m['a'], m['form']
    if f == 'ineq': return cases_ineq(m)
    cs = [(a, 'ok', 'the answer'), (a.replace('-', '−').replace('*', '·'), 'ok', 'typographic minus and dot'), (' ' + a.replace('+', ' + ') + ' ', 'ok', 'with spaces'), (a.upper() if f != 'fac' or 'e' not in a else a, 'ok', 'capital letters')]
    t = _terms(a)
    if len(t) > 1 and f == 'exp':
        r = ''.join(x if x[0] in '+-' else '+' + x for x in reversed(t)).lstrip('+')
        assert same(r, a), (r, a); cs.append((r, 'ok', 'terms in another order'))
    if re.search(r'\^[23](?!\d)', a) and '^(' not in a: cs.append((a.replace('^2', '²').replace('^3', '³'), 'ok', 'superscript digits'))
    cs += [(f'({a})+1', 'no', 'answer plus 1'), ('7x+123', 'no', 'unrelated'), ('', 'empty', 'empty'), ('x^', 'bad', 'unreadable'), ('(2x+3', 'bad', 'open bracket')]
    if abs(ev(a)) > 1e-9: cs.append((f'-({a})', 'no', 'opposite sign'))
    if f == 'exp' and len(t) >= 1: cs.append((f'({a})', 'half', 'answer inside brackets'))
    if f == 'exp' and re.search('[a-z]', a): cs.append((a + '+x-x', 'half', 'not collected'))
    if f == 'num':
        cs.append((f'{a}+0', 'half', 'still an exercise'))
        vs = sorted(set(re.findall('[a-z]', m['expr'])) - {'e'})
        if len(vs) == 1 and re.search('[=<>]', m['expr']): cs.append((f'{vs[0]} = {a}', 'ok', 'written as x = answer'))
        if '/' in a: cs += [(repr(round(ev(a), 9)), 'ok', 'decimal with nine digits'), (repr(round(ev(a), 2)), 'no', 'decimal rounded to two digits')]
        if abs(ev(a)) >= 1000 and float(ev(a)).is_integer(): cs.append((f'{int(ev(a)):,}', 'ok', 'thousands comma'))
    e = m['expr']
    if e and e != a:
        try: eq = same(e, a)
        except Exception: eq = False
        if eq: cs.append((e, 'half', 'the question itself typed back'))
    for x, msg in m['traps']: cs.append((x, 'trap:' + re.sub('<[^>]+>', '', msg)[:14], 'trap'))
    return cs
def cases_xy(m):
    a = m['a']; ks = list(a)
    cs = [(dict(a), 'ok', 'the answer'), ({k: f'{k}={v}' for k, v in a.items()}, 'ok', 'written as x = value'), ({k: '' for k in ks}, 'empty', 'both empty'),
          ({ks[0]: a[ks[0]], ks[1]: ''}, 'half', 'second empty'), ({ks[0]: a[ks[0]], ks[1]: f'({a[ks[1]]})+1'}, 'trap:הערך של', 'second wrong'),
          ({ks[0]: f'({a[ks[0]]})+1', ks[1]: a[ks[1]]}, 'trap:הערך של', 'first wrong'), ({ks[0]: '(', ks[1]: a[ks[1]]}, 'bad', 'unreadable'),
          ({ks[0]: f'{ks[1]}={a[ks[1]]}', ks[1]: a[ks[1]]}, 'trap:כתבתם ערך של', 'value of the other unknown')]
    if abs(ev(a[ks[0]]) - ev(a[ks[1]])) > 1e-9: cs.append(({ks[0]: a[ks[1]], ks[1]: a[ks[0]]}, 'trap:החלפתם', 'swapped'))
    return cs


for m in MANI:
    if m['kind'] == 'try': m['cases'] = cases(m)
    if m['kind'] == 'try2': m['cases'] = cases_xy(m)
src = open(SRC, encoding='utf8').read()
i = src.rindex('})();\n</script>')
out = src[:i] + 'window.__deck=window.__deck;\n' + '})();\n</script>\n<script>' + TEST.replace('__MAN__', json.dumps(MANI, ensure_ascii=False).replace('</', '<\\/')) + '</script>' + src[i + len('})();\n</script>'):]
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
p = os.path.join(d, 't.html'); open(p, 'w', encoding='utf8').write(out)
r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/p', '--window-size=1400,900', '--virtual-time-budget=60000', '--dump-dom', 'file://' + p], capture_output=True, text=True, timeout=300)
dom = r.stdout
m = re.search(r'data-test="([^"]*)"', dom)
e = re.search(r'data-err="([^"]*)"', dom)
if e: print('JS ERROR:', hh.unescape(e.group(1)))
if not m: print('no test result'); sys.exit(1)
R = json.loads(hh.unescape(m.group(1)))
bad_act = [a for a in R['act'] if not a['ok']]
bad_mc = [a for a in R['mc'] if not a['ok']]
print('counts', R['counts']); print('walk', R['walk'])
for k in ('overflow', 'wide', 'bidi', 'chars', 'reveal', 'small'):
    print(f'{k}: {len(R[k])}')
    for x in R[k][:40]: print('   ', json.dumps(x, ensure_ascii=False))
print('lesson', LESSON, 'activities', len(R['act']), 'of', len(MANI) - sum(m['kind'] == 'mc' for m in MANI), 'in the manifest; typed cases', sum(a.get('cases', 0) for a in R['act']), '; failed', len(bad_act)); [print('   ', json.dumps(a, ensure_ascii=False)[:900]) for a in bad_act[:40]]
print('mc', len(R['mc']), 'failed', len(bad_mc))
