/* ===== lesson activities for an algebra deck: typed answers checked as expressions, hints, staged solutions ===== */
(function(){
const say=(el,ok,html)=>{el.className='fbbar '+(ok===true?'good':ok===false?'wrong':ok==='half'?'half':'');el.innerHTML=html;};
const M=h=>'<span class="m" dir="ltr">'+h+'</span>';

/* ---------- expression parser: numbers, letters, + - * / ^, brackets, implicit multiplication (same grammar as qlib.py) ---------- */
const SUP={'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9'};
function norm(s){s=String(s).replace(/[⁰¹²³⁴-⁹]+/g,m=>'^'+[...m].map(c=>SUP[c]).join(''));
 return s.replace(/[\u2212\u2013\u2014]/g,'-').replace(/[·×∙]/g,'*').replace(/[÷:]/g,'/').replace(/\*\*/g,'^').replace(/\s+/g,'').replace(/(\d),(?=\d{3}(?:\D|$))/g,'$1').replace(/[\[{]/g,'(').replace(/[\]}]/g,')').toLowerCase();}
function parse(src){const s=norm(src);let i=0;if(!s)throw new Error('empty');
 const pk=()=>s[i]||'';
 function expr(){let t=[{s:1,n:term()}];while(pk()==='+'||pk()==='-'){const sg=pk()==='+'?1:-1;i++;t.push({s:sg,n:term()});}return t.length===1?t[0].n:{t:'add',a:t};}
 function term(){let f=[unary()];for(;;){const c=pk();if(c==='*'){i++;f.push(unary());}else if(c==='/'){i++;f.push({t:'inv',a:unary()});}else if(c&&/[0-9a-z(.]/.test(c)){f.push(power());}else break;}return f.length===1?f[0]:{t:'mul',a:f};}
 function unary(){if(pk()==='-'){i++;return {t:'neg',a:unary()};}if(pk()==='+'){i++;return unary();}return power();}
 function power(){const b=atom();if(pk()==='^'){i++;return {t:'pow',a:b,b:unary()};}return b;}
 function atom(){const c=pk();if(c==='('){i++;const v=expr();if(pk()!==')')throw new Error('bracket');i++;return {t:'par',a:v};}
  const m=/^\d+(\.\d+)?|^\.\d+/.exec(s.slice(i));if(m){i+=m[0].length;return {t:'num',v:parseFloat(m[0])};}
  if(/[a-z]/.test(c)){i++;return {t:'var',v:c};}throw new Error('char');}
 const r=expr();if(i<s.length)throw new Error('trailing');return r;}
function ev(n,env){switch(n.t){case 'num':return n.v;case 'var':return n.v==='e'?Math.E:env[n.v];case 'par':return ev(n.a,env);case 'neg':return -ev(n.a,env);case 'inv':return 1/ev(n.a,env);
 case 'pow':return Math.pow(ev(n.a,env),ev(n.b,env));case 'mul':return n.a.reduce((p,x)=>p*ev(x,env),1);case 'add':return n.a.reduce((p,x)=>p+x.s*ev(x.n,env),0);}}
const point=(k,pos)=>{const e={};for(let c=97;c<123;c++){const v=((c*7+k*13)%19)/9+0.6;e[String.fromCharCode(c)]=pos||((c+k)%3)?v:-v;}return e;};
function equiv(a,b){let ok=true,seen=0;for(const pos of [false,true]){ok=true;seen=0;for(let k=0;k<5;k++){const x=ev(a,point(k,pos)),y=ev(b,point(k,pos));if(!Number.isFinite(x)||!Number.isFinite(y)){seen=-1;break;}seen++;if(Math.abs(x-y)>1e-6*Math.max(1,Math.abs(x)))ok=false;}if(seen>0)return ok;}return false;}
const bare=n=>{while(n.t==='par')n=n.a;return n;};
function terms(n){n=bare(n);return n.t==='add'?n.a.length:1;}
function hasPar(n){if(n.t==='par')return true;if(n.t==='add')return n.a.some(x=>hasPar(x.n));if(n.t==='mul')return n.a.some(hasPar);if(n.t==='pow')return hasPar(n.a)||hasPar(n.b);if(n.t==='neg'||n.t==='inv')return hasPar(n.a);return false;}
/* the factors of a product: brackets that hold a sum (with their multiplicity) and everything else */
function factors(n,out){out=out||{sums:0,mono:[]};const b=bare(n);
 if(n.t==='mul'||b.t==='mul'){b.a.forEach(x=>factors(x,out));}
 else if(b.t==='neg'){out.mono.push({t:'num',v:-1});factors(b.a,out);}
 else if(b.t==='add'){out.sums+=1;}
 else if(b.t==='pow'&&bare(b.a).t==='add'){const e=bare(b.b);out.sums+=(e.t==='num'&&e.v>=1&&e.v<=9)?e.v:1;}
 else out.mono.push(b);
 return out;}
function pretty(n){switch(n.t){case 'num':return String(n.v);case 'var':return '<i>'+n.v+'</i>';case 'par':return '('+pretty(n.a)+')';case 'neg':return '−'+pretty(n.a);case 'inv':return pretty(n.a);
 case 'pow':return pretty(n.a)+'<sup>'+pretty(bare(n.b))+'</sup>';
 case 'mul':return n.a.map((x,j)=>{if(x.t==='inv')return '/'+pretty(x.a);const prev=j?n.a[j-1]:null;const dot=j&&(x.t==='num'||x.t==='neg'||(prev&&(bare(prev).t==='num'||prev.t==='inv')&&x.t==='num'));return (dot?'·':'')+pretty(x);}).join('');
 case 'add':return n.a.map((x,j)=>(j?(x.s>0?' + ':' − '):(x.s>0?'':'−'))+pretty(x.n)).join('');}}
window.__alg={parse,equiv,pretty,ev,norm,judge:i=>judge(i)};

/* ---------- one checked answer: used by every typed input ---------- */
/* the answer data sits on the input itself (tables, grids) or on its exercise (.try) */
function mono(n){if(n.t==='num'||n.t==='var')return true;if(n.t==='neg')return mono(n.a);
 if(n.t==='pow'){const e=n.b.t==='neg'?n.b.a:n.b;return n.a.t==='var'&&e.t==='num';}
 if(n.t==='mul'){const seen={};let nums=0;for(let j=0;j<n.a.length;j++){let f=n.a[j];if(j===0&&f.t==='neg')f=f.a;if(f.t==='num'){nums++;if(j>0)return false;}else if(f.t==='var'||(f.t==='pow'&&mono(f))){const v=f.t==='var'?f.v:f.a.v;if(seen[v])return false;seen[v]=1;}else return false;}return nums<=1;}
 return false;}
function tidy(u){return u.t==='add'?u.a.every(x=>mono(x.n)):mono(u);}
/* a number written as a number: 7, -3, 2.5, 15/7, -15/7 */
function numLit(n){n=bare(n);if(n.t==='neg')n=bare(n.a);if(n.t==='num')return true;if(n.t!=='mul'||n.a.length!==2||n.a[1].t!=='inv'||bare(n.a[1].a).t!=='num')return false;let f=bare(n.a[0]);if(f.t==='neg')f=bare(f.a);return f.t==='num';}
const RELS=s=>String(s).replace(/<=|=</g,'≤').replace(/>=|=>/g,'≥');
const FLIP={'<':'>','>':'<','≤':'≥','≥':'≤'};
function splitRel(s){const m=/^([^<>≤≥]*)([<>≤≥])([^<>≤≥]*)$/.exec(RELS(s).replace(/\s+/g,''));return m?{l:m[1],op:m[2],r:m[3]}:null;}
function sameIneq(p,q){const a=splitRel(p),b=splitRel(q);if(!a||!b)return false;const o=r=>/^[a-z]$/i.test(r.l)?[r.l.toLowerCase(),r.op,r.r]:[r.r.toLowerCase(),FLIP[r.op],r.l];const x=o(a),y=o(b);if(x[0]!==y[0]||x[1]!==y[1])return false;try{return equiv(parse(x[2]),parse(y[2]));}catch(e){return false;}}
function judgeIneq(raw,ans){const a=splitRel(ans),u=splitRel(raw);const v=a.l;
 if(!u){try{if(equiv(parse(raw),parse(a.r)))return {st:'half',msg:'המספר נכון. כתבו את התשובה כאי שוויון שלם, למשל <span class="m" dir="ltr"><i>'+v+'</i> &lt; '+pretty(parse(a.r))+'</span>.'};}catch(e){return {st:'bad'};}return {st:'no'};}
 let op,b;const L=u.l.toLowerCase(),Rr=u.r.toLowerCase();
 if(L===v){op=u.op;b=Rr;}else if(Rr===v){op=FLIP[u.op];b=L;}else return {st:'half',msg:'כתבו את התשובה כך שבצד אחד יופיע <span class="m" dir="ltr"><i>'+v+'</i></span> לבדו, ובצד השני מספר.'};
 let bn;try{bn=parse(b);}catch(e){return {st:'bad'};}
 if(!equiv(bn,parse(a.r)))return {st:'no',trap:null};
 if(!numLit(bn))return {st:'half',msg:'הגבול נכון, אבל עדיין כתוב כתרגיל. השלימו את החישוב עד למספר אחד.'};
 if(op===a.op)return {st:'ok'};
 if(op===FLIP[a.op]||op===FLIP[{'<':'≤','≤':'<','>':'≥','≥':'>'}[a.op]])return {st:'no',trap:'המספר נכון, אבל הכיוון הפוך. אם כפלתם או חילקתם במספר שלילי, סימן אי השוויון מתהפך.'};
 return {st:'no',trap:'המספר והכיוון נכונים, אבל שימו לב להבדל בין <span class="n">&lt;</span> (קטן מ) לבין <span class="n">≤</span> (קטן או שווה).'};}
function judge(inp){const host=inp.closest('.try');const ds=(inp.dataset.a!==undefined?inp:host).dataset;if(ds.a===undefined||ds.a==='')return {st:'bad'};
 let raw=inp.value.trim();if(!raw)return {st:'empty'};
 if(ds.form==='ineq'){const r=judgeIneq(raw,ds.a);if(r.st==='no'){try{JSON.parse(ds.traps||'[]').some(([x,msg])=>{if(sameIneq(raw,x)){r.trap=msg;return true;}});}catch(e){}}return r;}
 /* "x=4" is a fine way to answer: the unknown and its value */
 const pre=/^([a-zA-Z])\s*=(.+)$/.exec(raw);if(pre){const want=inp.dataset.v;if(want&&pre[1].toLowerCase()!==want)return {st:'no',trap:'כתבתם ערך של <span class="m" dir="ltr"><i>'+pre[1].toLowerCase()+'</i></span>, אבל התיבה הזאת היא של <span class="m" dir="ltr"><i>'+want+'</i></span>.'};raw=pre[2].trim();}
 if(ds.form==='num'&&/%$/.test(raw))raw=raw.slice(0,-1);
 let u,a;try{u=parse(raw);}catch(e){return {st:'bad'};}
 a=parse(ds.a);if(!equiv(u,a)){let trap=null;try{JSON.parse(ds.traps||'[]').some(([x,msg])=>{if(equiv(u,parse(x))){trap=msg;return true;}});}catch(e){}return {st:'no',trap};}
 const form=ds.form||'';
 if(form==='num'){if(!numLit(u))return {st:'half',msg:'הערך נכון, אבל עדיין כתוב כתרגיל. השלימו את החישוב עד למספר אחד.'};}
 if(form==='exp'){if(hasPar(u))return {st:'half',msg:'הביטוי שווה לביטוי המקורי, אבל נשארו בו סוגריים. פתחו אותם.'};if(terms(u)>+(ds.terms||99))return {st:'half',msg:'הביטוי נכון, אבל אפשר עוד לכנס איברים דומים.'};
  if(!tidy(u))return {st:'half',msg:'הביטוי שווה, אבל אפשר עוד לפשט: בכל איבר צריך להישאר מספר אחד, וכל אות פעם אחת עם המעריך שלה.'};}
 if(form==='fac'){const f=factors(u);if(!f.sums||bare(u).t==='add')return {st:'half',msg:'הביטוי שווה, אבל הוא עדיין סכום. התשובה צריכה להיות מכפלה: גורם כפול סוגריים.'};
  if(ds.out){const mono_=f.mono.length?{t:'mul',a:f.mono}:{t:'num',v:1},o=parse(ds.out);if(!equiv(mono_,o)&&!equiv({t:'neg',a:mono_},o))return {st:'half',msg:'הפירוק נכון, אבל אפשר להוציא גורם משותף גדול יותר.'};}
  if(+(ds.nb||0)>f.sums)return {st:'half',msg:'נכון עד כאן, אבל אפשר להמשיך ולפרק גם את מה שבתוך הסוגריים.'};}
 return {st:'ok'};}
function readBack(v){try{const r=splitRel(v);let h;if(r)h=pretty(parse(r.l))+' '+r.op.replace('<','&lt;')+' '+pretty(parse(r.r));else{const p=/^([a-zA-Z])\s*=(.+)$/.exec(v.trim());h=p?'<i>'+p[1].toLowerCase()+'</i> = '+pretty(parse(p[2])):pretty(parse(v.trim().replace(/%$/,'')));}return 'כך קראנו את מה שהקלדתם: '+M(h);}catch(e){return 'ממשיכים להקליד';}}
const BADREAD='לא הצלחנו לקרוא את הביטוי. בדקו שכל סוגריים נסגרים, ושחזקה כתובה עם הסימן ^ (למשל x^2).';

/* ---------- keypad: appears under the input in focus ---------- */
function ins(inp,t){const a=inp.selectionStart??inp.value.length,b=inp.selectionEnd??a;if(t==='⌫'){if(a===b&&a>0)inp.setRangeText('',a-1,a,'end');else inp.setRangeText('',a,b,'end');}else inp.setRangeText(t,a,b,'end');inp.dispatchEvent(new Event('input',{bubbles:true}));}
document.addEventListener('pointerdown',e=>{const k=e.target.closest('.kp button');if(!k)return;e.preventDefault();const inp=k.closest('.kp').__inp;if(inp){inp.focus();ins(inp,k.dataset.k);}});
const kp=document.createElement('div');kp.className='kp';document.body.appendChild(kp);let kpT=null;
function placeKp(){const inp=kp.__inp;if(!inp||kp.style.display==='none')return;const r=inp.getBoundingClientRect();const host=inp.closest('.try,.cells');const fb=host&&host.querySelector('.fbbar');const rb=fb?fb.getBoundingClientRect():r;
 const w=kp.offsetWidth,h=kp.offsetHeight;let top=Math.max(r.bottom,rb.bottom)+6;if(top+h>innerHeight-48)top=r.top-h-6;kp.style.left=Math.max(6,Math.min(innerWidth-w-6,r.left+r.width/2-w/2))+'px';kp.style.top=top+'px';}
function showKp(inp){clearTimeout(kpT);const vars=(inp.closest('[data-vars]')?.dataset.vars||'x').split('');
 const host=inp.closest('[data-kp]');const extra=[...(host?host.dataset.kp:'')];kp.innerHTML=[...vars,...extra,'^','(',')','+','-','*','⌫'].map(k=>`<button type="button" data-k="${k}">${k==='^'?'חזקה ^':k==='-'?'−':k==='*'?'·':k==='/'?'שבר /':k==='<'?'&lt;':k}</button>`).join('');kp.__inp=inp;kp.style.display='flex';placeKp();}
new MutationObserver(()=>placeKp()).observe(document.getElementById('stage'),{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class']});
addEventListener('resize',placeKp);
document.addEventListener('focusin',e=>{if(e.target.matches&&e.target.matches('input.ex'))showKp(e.target);});
/* a click opens it too, also when the window itself has no focus */
document.addEventListener('click',e=>{if(e.target.matches&&e.target.matches('input.ex'))showKp(e.target);});
document.addEventListener('focusout',e=>{if(e.target.matches&&e.target.matches('input.ex'))kpT=setTimeout(()=>{kp.style.display='none';},120);});

/* ---------- staged solution: one stage per click, inline or in a popup ---------- */
const pop=mo;   /* the popup of deck.js */
function stager(box,btn){const st=$$('.tstep',box);let k=0;const lab=()=>{btn.textContent=k>=st.length?'כל השלבים מוצגים':k?`השלב הבא (${k+1} מתוך ${st.length})`:'פתרון בשלבים';btn.disabled=k>=st.length;};
 const step=()=>{if(k<st.length){st[k].classList.add('show');k++;}lab();box.scrollTop=box.scrollHeight;};const reset=()=>{k=0;st.forEach(x=>x.classList.remove('show'));lab();};lab();return {step,reset,all:()=>{while(k<st.length)step();}};}

/* ---------- TRY: a question with a typed answer, hints and a staged solution ---------- */
$$('.try').forEach(b=>{const ins=$$('input.ex',b),inp=ins[0],multi=ins.length>1,fb=$('.fbbar',b),hints=$$('.hints>div',b),solb=$('.solb',b),tsol=$('.tsol',b);let h=0,tries=0;const idle=fb.innerHTML;
 const big=b.classList.contains('big');let sg=null;
 if(tsol&&big){sg=stager(tsol,solb);solb.addEventListener('click',()=>{tsol.hidden=false;sg.step();});}
 else if(tsol){solb.addEventListener('click',()=>{const box=pop.querySelector('.more-in');box.innerHTML='<div class="more-h tq">'+$('.tq',b).innerHTML+'</div><div class="tsol">'+tsol.innerHTML+'</div><div class="actbar"><button class="abtn nxs"></button></div>';const g=stager(box,$('.nxs',box));$('.nxs',box).onclick=g.step;g.step();pop.classList.add('open');});}
 const check=()=>{tries++;b.classList.remove('solved');ins.forEach(i=>i.classList.remove('good','badc'));
  if(multi){const rs=ins.map(i=>judge(i));const vn=i=>'<span class="m" dir="ltr"><i>'+i.dataset.v+'</i></span>';
   if(rs.every(r=>r.st==='empty')){say(fb,null,'הקלידו את שני הערכים, ואז לחצו ״בדיקה״.');return;}
   if(rs.some(r=>r.st==='bad')){say(fb,false,BADREAD);return;}
   rs.forEach((r,k)=>{if(r.st==='ok')ins[k].classList.add('good');else if(r.st!=='empty')ins[k].classList.add('badc');});
   if(rs.every(r=>r.st==='ok')){b.classList.add('solved');say(fb,true,'<b>נכון.</b> '+(b.dataset.w||''));return;}
   if(rs.some(r=>r.st==='empty')){const k=rs.findIndex(r=>r.st==='empty');say(fb,'half','חסר הערך של '+vn(ins[k])+'. מציבים את הערך שמצאתם באחת המשוואות.');return;}
   {const k=rs.findIndex(r=>r.trap&&/כתבתם ערך של/.test(r.trap));if(k>=0){say(fb,false,'<b>עדיין לא.</b> '+rs[k].trap);return;}}
   try{const sw=ins.length===2&&ins[0].dataset.a!==ins[1].dataset.a&&equiv(parse(ins[0].value.replace(/^[a-z]\s*=/i,'')),parse(ins[1].dataset.a))&&equiv(parse(ins[1].value.replace(/^[a-z]\s*=/i,'')),parse(ins[0].dataset.a));if(sw){say(fb,false,'<b>עדיין לא.</b> החלפתם בין הערכים: בדקו איזה ערך שייך ל-'+vn(ins[0])+' ואיזה ל-'+vn(ins[1])+'.');return;}}catch(e){}
   const k=rs.findIndex(r=>r.st!=='ok'),okk=rs.findIndex(r=>r.st==='ok');const trap=rs[k].trap;
   say(fb,false,'<b>עדיין לא.</b> '+(trap||(okk>=0?'הערך של '+vn(ins[okk])+' נכון. הערך של '+vn(ins[k])+' עדיין לא: הציבו את '+vn(ins[okk])+' באחת המשוואות.':'בדקו את שני הערכים: הציבו אותם בשתי המשוואות.')));return;}
  const r=judge(inp);
  if(r.st==='empty'){say(fb,null,'הקלידו תשובה, ואז לחצו ״בדיקה״.');return;}
  if(r.st==='bad'){say(fb,false,BADREAD);return;}
  if(r.st==='ok'){b.classList.add('solved');inp.classList.add('good');say(fb,true,'<b>נכון.</b> '+(b.dataset.w||''));return;}
  if(r.st==='half'){say(fb,'half','<b>כמעט.</b> '+r.msg);return;}
  inp.classList.add('badc');say(fb,false,'<b>עדיין לא.</b> '+(r.trap||(tries>1&&hints.length?'לחצו ״רמז״ כדי לקבל כיוון, או ״פתרון בשלבים״ כדי לראות את הדרך.':'בדקו שוב את הסימנים ואת סדר הפעולות, ונסו שנית.')));};
 $('.chk',b).addEventListener('click',check);ins.forEach((i,k)=>i.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();if(multi&&k<ins.length-1&&!ins[k+1].value.trim())ins[k+1].focus();else check();}}));
 ins.forEach(i=>i.addEventListener('input',()=>{i.classList.remove('good','badc');if(!i.value.trim()){fb.className='fbbar';fb.innerHTML=idle;return;}say(fb,null,(multi?'<span class="m" dir="ltr"><i>'+i.dataset.v+'</i></span>: ':'')+readBack(i.value));}));
 const hb=$('.hintb',b);if(hb)hb.addEventListener('click',()=>{if(!hints.length)return;say(fb,'half',`<b>רמז ${h%hints.length+1} מתוך ${hints.length}:</b> `+hints[h%hints.length].innerHTML);h++;});
 b.__reset=()=>{ins.forEach(i=>{i.value='';i.classList.remove('good','badc');});b.classList.remove('solved');fb.className='fbbar';fb.innerHTML=idle;h=0;tries=0;if(sg){sg.reset();tsol.hidden=true;}};});

/* ---------- CELLS: a table (or a grid of products) with several typed answers ---------- */
$$('.cells').forEach(b=>{const ins_=$$('input.ex',b),fb=$('.fbbar',b);const idle=fb.innerHTML;
 const check=()=>{let good=0,first=null,read=false;ins_.forEach(i=>{const r=judge(i);i.classList.remove('good','badc','halfc');if(r.st==='ok'){i.classList.add('good');good++;}else if(r.st==='empty'){}else{i.classList.add(r.st==='half'?'halfc':'badc');if(r.st==='bad')read=true;if(!first)first={i,r};}});
  const empty=ins_.filter(i=>!i.value.trim()).length;
  if(good===ins_.length){b.classList.add('solved');say(fb,true,'<b>הכול נכון.</b> '+(b.dataset.w||''));return;}
  b.classList.remove('solved');
  if(first){const r=first.r;say(fb,r.st==='half'?'half':false,`<b>${good} מתוך ${ins_.length} נכונים.</b> `+(r.st==='bad'?BADREAD:r.st==='half'?r.msg:(r.trap||first.i.dataset.h||'בדקו את התאים המסומנים באדום.')));}
  else say(fb,null,`<b>${good} מתוך ${ins_.length} נכונים.</b> `+(empty?'השלימו את התאים הריקים.':''));};
 $('.chk',b).addEventListener('click',check);ins_.forEach(i=>{i.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();const j=ins_.indexOf(i);if(j<ins_.length-1)ins_[j+1].focus();else check();}});i.addEventListener('input',()=>i.classList.remove('good','badc','halfc'));});
 const sh=$('.shw',b);if(sh)sh.addEventListener('click',()=>{ins_.forEach(i=>{i.value=i.dataset.show||i.dataset.a;});check();});
 const rs=$('.rst',b);if(rs)rs.addEventListener('click',()=>{ins_.forEach(i=>{i.value='';i.classList.remove('good','badc','halfc');});b.classList.remove('solved');fb.className='fbbar';fb.innerHTML=idle;});});

/* ---------- OPS: which operation comes first? click it, and the expression shrinks by one step ---------- */
const WHY={par:'יש סוגריים, ומה שבתוכם מחושב ראשון.',pow:'חזקה קודמת לכפל, לחילוק, לחיבור ולחיסור.',mul:'כפל וחילוק קודמים לחיבור ולחיסור.',add:'נשארו רק חיבור וחיסור.'};
const SAME={mul:'כפל וחילוק הם באותה רמה: מתקדמים משמאל לימין.',add:'חיבור וחיסור הם באותה רמה: מתקדמים משמאל לימין.',par:'בתוך הסוגריים חל אותו סדר פעולות.',pow:'מתחילים מהחזקה השמאלית.'};
const KN={par:'סוגריים',pow:'חזקה',mul:'כפל וחילוק',add:'חיבור וחיסור'};
$$('.ops').forEach(b=>{const C=JSON.parse(b.dataset.cfg),ex=$('.opx',b),log=$('.oplog',b),fb=$('.fbbar',b);let k=0;
 const draw=()=>{if(k<C.states.length){ex.innerHTML=C.states[k].h;}else{ex.innerHTML=C.final;}};
 const done=()=>{b.classList.add('solved');say(fb,true,'<b>סיימנו.</b> '+C.w);};
 const adv=()=>{const s=C.states[k];const li=document.createElement('li');li.innerHTML=`<b>${KN[s.kind]}:</b> `+s.res;log.appendChild(li);k++;draw();ex.classList.remove('flash');void ex.offsetWidth;ex.classList.add('flash');if(k>=C.states.length)done();else say(fb,true,'<b>נכון.</b> '+s.res+' מה הפעולה הבאה?');};
 ex.addEventListener('click',e=>{const o=e.target.closest('.op');if(!o||k>=C.states.length)return;const s=C.states[k];if(+o.dataset.i===s.ok){adv();}else{o.classList.add('bad');setTimeout(()=>o.classList.remove('bad'),700);say(fb,false,'<b>עוד לא.</b> '+(o.dataset.k===s.kind?SAME[s.kind]:WHY[s.kind]));}});
 $('.rst',b).addEventListener('click',()=>{k=0;log.innerHTML='';b.classList.remove('solved');draw();say(fb,null,'לחצו על סימן הפעולה שמבצעים ראשונה.');});
 $('.shw',b).addEventListener('click',()=>{if(k<C.states.length)adv();});
 b.__solve=()=>{while(k<C.states.length)adv();};b.__k=()=>k;draw();});

/* ---------- find the mistake: click the first wrong line of a student's solution ---------- */
$$('.err').forEach(b=>{const bad=+b.dataset.bad,box=$('.elines',b),ls=$$('.el',box),fb=$('.fbbar',b),fx=$('.efix',b),idle=fb.innerHTML;
 const clear=()=>ls.forEach(x=>{['okl','bad','after','later','pick'].forEach(c=>x.classList.toggle(c,false));});
 ls.forEach(l=>l.addEventListener('click',()=>{if(b.classList.contains('solved'))return;const i=+l.dataset.i;ls.forEach(x=>x.classList.toggle('pick',false));
  if(i===bad){l.classList.add('bad');b.classList.add('solved');box.classList.add('solved');ls.forEach((x,k)=>{if(k<bad)x.classList.add('okl');if(k>bad)x.classList.add('after');});fx.hidden=false;say(fb,true,'<b>נכון, כאן הטעות.</b> '+b.dataset.w);}
  else if(i<bad){l.classList.add('okl','pick');say(fb,false,'<b>השורה הזו נכונה.</b> '+l.dataset.w+' המשיכו לחפש בשורות שאחריה.');}
  else{l.classList.add('later','pick');say(fb,'half','<b>השורה הזו ממשיכה טעות שקרתה קודם.</b> היא נובעת מהשורה שלפניה, אבל הטעות עצמה נמצאת בשורה מוקדמת יותר. חפשו למעלה.');}}));
 $('.rst',b).addEventListener('click',()=>{clear();b.classList.toggle('solved',false);box.classList.toggle('solved',false);fx.hidden=true;fb.className='fbbar';fb.innerHTML=idle;});});
/* ---------- sorter: each row has one right answer ---------- */
$$('.sorter').forEach(b=>{const rows=$$('.srow',b),fb=$('.fbbar',b),sc=$('.score',b);
 const upd=()=>{const d=rows.filter(r=>r.classList.contains('solved')).length;sc.textContent=d+' / '+rows.length;if(d===rows.length){b.classList.add('solved');say(fb,true,'כל השורות נכונות. '+fb.innerHTML);}};
 rows.forEach(r=>{const a=+r.dataset.a;$$('.so',r).forEach(o=>o.addEventListener('click',()=>{if(r.classList.contains('solved'))return;const i=+o.dataset.i;
  if(i===a){o.classList.add('ok');r.classList.add('solved');$$('.so',r).forEach(x=>x.classList.remove('bad'));say(fb,true,'<b>נכון.</b> '+r.dataset.w);upd();}
  else{o.classList.add('bad');say(fb,false,'<b>לא.</b> '+(r.dataset.h||'קראו שוב את השורה, ונסו אפשרות אחרת.'));}}));});
 $('.rst',b).addEventListener('click',()=>{rows.forEach(r=>{r.classList.remove('solved');$$('.so',r).forEach(x=>x.classList.remove('ok','bad'));});b.classList.remove('solved');say(fb,null,'בחרו תשובה בכל שורה.');sc.textContent='0 / '+rows.length;});});
})();
