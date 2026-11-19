# Headless test of the deck: layout overflow per slide (first view, all revealed, all solved), reveals, every activity
# (right answer accepted, wrong answer rejected), direction of every math run, forbidden characters.
import json, os, re, subprocess, sys, tempfile, html as hh
H = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, '..', 'lectures', 'lecture-1', 'presentation.html')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TEST = r'''
window.onerror=(m,u,l,c,e)=>{document.documentElement.setAttribute('data-err',m+' @'+l+':'+c);};
(function(){
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
function bidi(s){s.querySelectorAll('.eq,.m,.n,.opx,.tw-e').forEach(e=>{if(e.closest('[hidden]')||e.closest('.hints'))return;const cs=getComputedStyle(e);if(cs.direction!=='ltr'||!/isolate|plaintext/.test(cs.unicodeBidi)&&cs.display==='inline')R.bidi.push({id:s.id,why:'not an isolated ltr run',t:e.textContent.slice(0,30)});
 const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);const ts=[];let t;while(t=w.nextNode())if(t.nodeValue.trim()&&!t.parentElement.closest('.mh'))ts.push(t);if(ts.length<1)return;
 const pos=[];ts.forEach(t=>{const v=t.nodeValue;for(let j=0;j<v.length;j++){if(!v[j].trim())continue;const g=document.createRange();g.setStart(t,j);g.setEnd(t,j+1);const r=g.getBoundingClientRect();if(r.width)pos.push({x:r.left,y:r.top,c:v[j],sup:!!t.parentElement.closest('sup')});}});
 for(let j=1;j<pos.length;j++){if(pos[j].x<pos[j-1].x-0.5&&!(e.classList.contains('eq')&&Math.abs(pos[j].y-pos[j-1].y)>16&&!pos[j].sup&&!pos[j-1].sup)){R.bidi.push({id:s.id,why:'order',t:e.textContent.slice(0,40),at:pos[j-1].c+pos[j].c});break;}}
 if(e.classList.contains('m')||e.classList.contains('n')){const rs=e.getClientRects();if(rs.length>1&&Math.abs(rs[0].top-rs[rs.length-1].top)>14)R.bidi.push({id:s.id,why:'wrapped',t:e.textContent.slice(0,40)});}});
 // a minus or an equals sign loose in Hebrew text (outside an ltr run) would be mirrored
 const w=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let t;while(t=w.nextNode()){const p=t.parentElement;if(!p||p.closest('svg,script,style,.eq,.m,.n,.opx,.op,.gq,.kp,[dir=ltr],input,.hints'))continue;if(/[−=+^<>≠]/.test(t.nodeValue)||/\d\s*-\s*\d/.test(t.nodeValue))R.bidi.push({id:s.id,why:'loose sign in Hebrew text',t:t.nodeValue.trim().slice(0,40)});}}
function small(s){const w=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let n;const seen={};while(n=w.nextNode()){if(!n.nodeValue.trim())continue;const p=n.parentElement;if(p.closest('.ft,sup,sub,tspan,svg,.hints,[hidden],.kp,.rn,.fn,.tn,.wn>b'))continue;const f=parseFloat(getComputedStyle(p).fontSize);if(f<16.4)seen[Math.round(f*10)/10]=(n.nodeValue.trim().slice(0,18));}if(Object.keys(seen).length)R.small.push({id:s.id,seen});}
const A=(id,kind,ok,more)=>R.act.push(Object.assign({id,kind,ok:!!ok},more||{}));
function solve(s){
 s.querySelectorAll('.try').forEach(b=>{const i=b.querySelector('input.ex'),fb=b.querySelector('.fbbar'),chk=b.querySelector('.chk');
  i.value='7x+123';i.dispatchEvent(new Event('input',{bubbles:true}));chk.click();const rej=fb.classList.contains('wrong');
  let trapsOk=true;try{JSON.parse(i.dataset.traps||'[]').forEach(([x,m])=>{i.value=x;chk.click();if(!fb.classList.contains('wrong')||!fb.innerHTML.includes(m.slice(0,12)))trapsOk=false;});}catch(e){trapsOk=false;}
  i.value=i.dataset.a;i.dispatchEvent(new Event('input',{bubbles:true}));const read=fb.textContent.includes('קראנו');chk.click();const acc=fb.classList.contains('good')&&b.classList.contains('solved');
  const hb=b.querySelector('.hintb'),nh=b.querySelectorAll('.hints>div').length;let hint=true;if(nh){hb.click();hint=fb.classList.contains('half');}
  const ns=b.querySelectorAll('.tsol .tstep').length;let stg=true;
  if(b.classList.contains('big')){const sb=b.querySelector('.solb');for(let k=0;k<ns;k++)sb.click();stg=b.querySelectorAll('.tsol .tstep.show').length===ns&&sb.disabled;}
  else{b.querySelector('.solb').click();const pop=document.getElementById('moreov');const nx=pop.querySelector('.nxs');for(let k=1;k<ns;k++)nx.click();stg=pop.classList.contains('open')&&pop.querySelectorAll('.tstep.show').length===ns;pop.classList.remove('open');}
  i.value=i.dataset.a;chk.click();
  A(b.id,'try',rej&&acc&&trapsOk&&hint&&stg&&read&&ns>0,{rej,acc,trapsOk,hint,stg,read,ns});});
 s.querySelectorAll('.cells').forEach(b=>{const ins=[...b.querySelectorAll('input.ex')],fb=b.querySelector('.fbbar');ins.forEach(i=>i.value='999');b.querySelector('.chk').click();const rej=fb.classList.contains('wrong')&&ins.every(i=>i.classList.contains('badc'));
  b.querySelector('.rst').click();const clr=ins.every(i=>!i.value);b.querySelector('.shw').click();const acc=b.classList.contains('solved')&&ins.every(i=>i.classList.contains('good'));A(b.id,'cells',rej&&clr&&acc,{rej,clr,acc,n:ins.length});});
 s.querySelectorAll('.ops').forEach(b=>{const C=JSON.parse(b.dataset.cfg),fb=b.querySelector('.fbbar');let ok=true,wrongSeen=false;
  for(let k=0;k<C.states.length;k++){const ops=[...b.querySelectorAll('.opx .op')];const w=ops.find(o=>+o.dataset.i!==C.states[k].ok);if(w){w.click();if(!fb.classList.contains('wrong')||b.__k()!==k)ok=false;wrongSeen=true;}
   const r=ops.find(o=>+o.dataset.i===C.states[k].ok);if(!r){ok=false;break;}r.click();if(b.__k()!==k+1)ok=false;}
  ok=ok&&b.classList.contains('solved')&&b.querySelectorAll('.oplog li').length===C.states.length;A(b.id,'ops',ok,{wrongSeen,final:b.querySelector('.opx').textContent});});
 s.querySelectorAll('.sorter').forEach(b=>{let ok=true;b.querySelectorAll('.srow').forEach(r=>{const os=r.querySelectorAll('.so'),a=+r.dataset.a;const w=(a+1)%os.length;os[w].click();if(r.classList.contains('solved'))ok=false;os[a].click();if(!r.classList.contains('solved'))ok=false;});A(b.id,'sorter',ok&&b.classList.contains('solved'));});
 s.querySelectorAll('.mc').forEach(m=>{const a=+m.dataset.a,os=[...m.querySelectorAll('.o')],w=(a+1)%os.length;os[w].click();const ok=os[w].classList.contains('bad')&&os[a].classList.contains('ok')&&getComputedStyle(m.querySelector('.w')).display!=='none';R.mc.push({id:m.id,ok,a,n:os.length});});}
D.slides.forEach((s,i)=>{D.show(i);measure(s,i,'first');D.setAll(s,true);measure(s,i,'open');wide(s);bidi(s);small(s);
 const txt=s.textContent;[['em','—'],['maqaf','־'],['en','–'],['ell','…'],['arrow','→'],['q1','“'],['q2','”'],['hyphenminus-in-math',null]].forEach(([k,c])=>{if(c&&txt.includes(c))R.chars.push({id:s.id,k});});
 s.querySelectorAll('.eq,.m').forEach(e=>{if(/-/.test(e.textContent))R.chars.push({id:s.id,k:'ascii minus in math: '+e.textContent.slice(0,20)});});
 solve(s);measure(s,i,'solved');wide(s);
 // popups of compact tries must fit the viewport
 });
// reveals: walking with next() shows every group, one per click, and reaches the last slide
D.show(0);let k=0,per={};while(D.cur()<D.slides.length-1&&k<3000){const c=D.cur();D.next();k++;per[c]=(per[c]||0)+1;}
R.walk={clicks:k,end:D.cur(),slides:D.slides.length};
D.slides.forEach((s,i)=>{const g=D.groups(s).length;if((per[i]||0)!==g+1&&i<D.slides.length-1)R.reveal.push({id:s.id,groups:g,clicks:per[i]});});
R.counts={slides:D.slides.length,tries:document.querySelectorAll('.try').length,cells:document.querySelectorAll('.cells').length,ops:document.querySelectorAll('.ops').length,sorters:document.querySelectorAll('.sorter').length,mc:document.querySelectorAll('.mc').length,math:document.querySelectorAll('.eq,.m').length,steps:document.querySelectorAll('.st').length};
document.documentElement.setAttribute('data-test',JSON.stringify(R));
})();
'''
src = open(SRC, encoding='utf8').read()
i = src.rindex('})();\n</script>')
out = src[:i] + 'window.__deck=window.__deck;\n' + '})();\n</script>\n<script>' + TEST + '</script>' + src[i + len('})();\n</script>'):]
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
p = os.path.join(d, 't.html'); open(p, 'w', encoding='utf8').write(out)
r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/p', '--window-size=1400,900', '--virtual-time-budget=20000', '--dump-dom', 'file://' + p], capture_output=True, text=True, timeout=300)
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
print('activities', len(R['act']), 'failed', len(bad_act)); [print('   ', json.dumps(a, ensure_ascii=False)) for a in bad_act[:30]]
print('mc', len(R['mc']), 'failed', len(bad_mc))
