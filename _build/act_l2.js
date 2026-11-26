(()=>{const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];const say=(el,ok,html)=>{el.className='fbbar '+(ok===true?'good':ok===false?'wrong':ok==='half'?'half':'');el.innerHTML=html;};
/* ---------- find the mistake: click the first wrong line of a student's solution ---------- */
$$('.err').forEach(b=>{const bad=+b.dataset.bad,box=$('.elines',b),ls=$$('.el',box),fb=$('.fbbar',b),fx=$('.efix',b),idle=fb.innerHTML;
 const clear=()=>ls.forEach(x=>{['okl','bad','after','later','pick'].forEach(c=>x.classList.toggle(c,false));});
 ls.forEach(l=>l.addEventListener('click',()=>{if(b.classList.contains('solved'))return;const i=+l.dataset.i;ls.forEach(x=>x.classList.toggle('pick',false));
  if(i===bad){l.classList.add('bad');b.classList.add('solved');box.classList.add('solved');ls.forEach((x,k)=>{if(k<bad)x.classList.add('okl');if(k>bad)x.classList.add('after');});fx.hidden=false;say(fb,true,'<b>נכון, כאן הטעות.</b> '+b.dataset.w);}
  else if(i<bad){l.classList.add('okl','pick');say(fb,false,'<b>השורה הזו נכונה.</b> '+l.dataset.w+' המשיכו לחפש בשורות שאחריה.');}
  else{l.classList.add('later','pick');say(fb,'half','<b>השורה הזו ממשיכה טעות שקרתה קודם.</b> היא נובעת מהשורה שלפניה, אבל הטעות עצמה נמצאת בשורה מוקדמת יותר. חפשו למעלה.');}}));
 $('.rst',b).addEventListener('click',()=>{clear();b.classList.toggle('solved',false);box.classList.toggle('solved',false);fx.hidden=true;fb.className='fbbar';fb.innerHTML=idle;});});
})();
