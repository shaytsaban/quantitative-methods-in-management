# Course hub. Run: python3 build_hub.py  ->  ../index.html
# A meeting without a recording yet gets the placeholder box; put a YouTube id in REC to embed it.
import os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from pdfkit import CR1, CR2
exec(open(os.path.join(H, 'plan.py'), encoding='utf8').read())
_ns = {}; exec(open(os.path.join(H, 'booklet.py'), encoding='utf8').read(), _ns)
NB = len(_ns['EX'])
n = lambda s: f'<span class="n">{s}</span>'
LEC = {
 1: dict(title='ריענון באלגברה: מיומנויות אלגבריות', learn=['חזקה, סימנים בכפל, וסדר פעולות החשבון', 'משתנה, ביטוי אלגברי, איבר ומקדם; הצבה של מספר בביטוי', 'כינוס איברים דומים', 'שלושת חוקי החזקות',
         'פתיחת סוגריים, מינוס לפני סוגריים, ופישוט ביטויים', 'שלוש נוסחאות הכפל המקוצר', 'הוצאת גורם משותף ופירוק לגורמים', 'תרגילים מסכמים, ותרגול עצמי לבית לפי נושאים']),
 2: dict(title='משוואות, מערכות משוואות, אחוזים ואי שוויונים', learn=['חזרה קצרה על הכלים של מפגש 1', 'משוואה ממעלה ראשונה עם נעלם אחד: המאזניים, העברת אגף ובדיקה בהצבה', 'משוואות עם שברים: כפל במכנה המשותף, ונעלם במכנה עם תחום הגדרה',
         'מערכת של שתי משוואות: שיטת ההצבה ושיטת השוואת המקדמים', 'אחוזים: אחוז מסכום, מקדם שינוי, שינויים ברצף ושיעור שינוי', 'אי שוויונים: פתרון, ציר המספרים, והיפוך הסימן בכפל במספר שלילי',
         'תרגילים מסכמים מסיפורים ניהוליים, ותרגול עצמי לבית'],
         home='השקפים האחרונים של המצגת, לפי נושאים. בכל נושא: ״מצאו את הטעות״, ותרגילים מהקל אל הקשה עם פתרון מפורט. בסוף: ממילים למתמטיקה, ושלוש בעיות מילוליות.')}
BUILT = set(LEC)
for _k, _v in LEC.items():
    _d = open(os.path.join(H, '..', 'lectures', f'lecture-{_k}', 'presentation.html'), encoding='utf8').read()
    _v['ns'], _v['nt'] = _d.count('<section class="slide'), _d.count('class="act try')
    _v['nb'] = sum(1 for e in _ns['EX'] if _ns['TOPICS'][e[1]][0] == _k)
NS, NT = LEC[1]['ns'], LEC[1]['nt']
REC = {}     # meeting -> YouTube id
css = open(os.path.join(H, 'shell', 'hub.css'), encoding='utf8').read() + '''
.hero h1{font-size:clamp(38px,7vw,64px)}.hero .h1s{font-size:clamp(20px,3vw,28px);font-weight:700;color:#7fe3d6;margin-top:6px;line-height:1.25}
.cred{margin-top:18px;display:inline-block;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.28);border-radius:14px;padding:10px 18px;font-size:16px;line-height:1.55;color:#e4ebfb}.cred b{color:#ffd37a}
.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:-34px;position:relative;z-index:2}
.fact{background:#fff;border-radius:18px;padding:16px 20px;box-shadow:0 2px 0 var(--line),0 14px 34px rgba(22,33,58,.1);border-top:6px solid var(--coral)}
.fact:nth-child(2){border-top-color:#0f9d90}.fact:nth-child(3){border-top-color:#e8960c}.fact:nth-child(4){border-top-color:#27447f}
.fact .fi{font-size:28px;line-height:1}.fact b{display:block;font-size:19px;font-weight:800;color:var(--navy2);margin-top:6px}.fact>span{display:block;font-size:15.5px;color:var(--ink2);line-height:1.4;margin-top:2px}
.fact a{direction:ltr;unicode-bidi:isolate;display:inline-block;text-decoration:underline;overflow-wrap:anywhere}
.halves{display:flex;gap:10px;margin-top:16px;font-weight:800;font-size:15.5px;flex-wrap:wrap}
.halves>span{border-radius:99px;padding:5px 16px}.halves .a{background:#dff5f2;color:#087469}.halves .b{background:#ece8ff;color:#4f33c9}.halves .c{background:#fff0d2;color:#a86703}.halves .d{background:#ffe3dc;color:#b8391f}
.plan{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:14px}
.pc{position:relative;background:#fff;border-radius:16px;padding:14px 16px 36px;box-shadow:0 2px 0 var(--line);border-right:7px solid #0f9d90;display:block;color:inherit;text-decoration:none;min-height:124px;transition:transform .15s}
.pc:hover{transform:translateY(-3px)}.pc.b{border-right-color:#6d4df2}.pc.c{border-right-color:#e8960c}.pc.d{border-right-color:#c4421f}
.pc.on{box-shadow:0 0 0 3px var(--coral),0 14px 30px rgba(255,106,77,.22)}
.pc .pn{display:inline-grid;place-items:center;min-width:32px;height:32px;border-radius:10px;background:var(--navy2);color:#fff;font-weight:800;font-size:17px;margin-bottom:6px}
.pc b{display:block;font-size:17px;line-height:1.3;font-weight:800;color:var(--navy2)}
.pc em{position:absolute;bottom:10px;right:16px;font-style:normal;font-size:13px;font-weight:800;color:var(--mut);background:#eef0f6;border-radius:99px;padding:1px 12px}
.pc.on em{background:var(--coral);color:#fff}
.cgrid{grid-template-columns:1fr 1fr 1fr}
.lec.up .lec-head{padding-bottom:6px}.lec.up .lec-n{background:#8a93aa;width:52px;height:52px;font-size:24px;border-radius:14px}.lec.up .lec-head h3{font-size:21px}
.upb{display:grid;grid-template-columns:1.5fr 1fr;gap:24px;padding:4px 30px 22px;align-items:center}
.upb p{font-size:16px;color:var(--ink2);line-height:1.5}.upb .soon{margin-top:6px;font-weight:700;color:var(--mut)}
.recsm{position:relative;aspect-ratio:16/6;border-radius:14px;background:linear-gradient(150deg,#0f1b33,#27447f);display:flex;gap:12px;align-items:center;justify-content:center;color:#d6e0f7;font-size:15px}
.recsm .play{width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,.14);display:grid;place-items:center;font-size:16px;color:#fff;direction:ltr}.recsm b{color:#fff;display:block;font-size:15.5px}
@media (max-width:900px){.plan{grid-template-columns:repeat(2,1fr)}.facts{grid-template-columns:repeat(2,1fr)}.cgrid{grid-template-columns:1fr}.upb{grid-template-columns:1fr;padding:4px 18px 18px}}
@media (max-width:560px){.plan{grid-template-columns:1fr}.pc{min-height:0}.facts{grid-template-columns:1fr;margin-top:-22px}}
'''
lk = lambda k, href, e, b, d: f'<a class="lk {k}" href="{href}" target="_blank" rel="noopener"><span class="e">{e}</span><span><b>{b}</b><span class="d">{d}</span></span></a>'
plan = ''.join(f'<a class="pc {k}{" on" if i in BUILT else ""}" href="#lesson-{i}"><span class="pn">{n(i)}</span><b>{t}</b><em>{"באתר" if i in BUILT else "בקרוב"}</em></a>' for i, t, d, k in PLAN)


def rec(i, big=False):
    if i in REC:
        return f'<div class="recbox"><iframe src="https://www.youtube-nocookie.com/embed/{REC[i]}" title="הקלטת מפגש {i}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
    if big:
        return f'<div class="recbig"><div class="rb-in"><span class="rb-play">&#9654;</span><b>הקלטת מפגש {n(i)}</b><span>תועלה לאחר המפגש</span></div></div>'
    return f'<div class="recsm" id="rec-{i}"><span class="play">&#9654;</span><span><b>הקלטת מפגש {n(i)}</b>תועלה לאחר המפגש</span></div>'


def lec_card(i):
    L = LEC[i]
    li = ''.join(f'<li>{x}</li>' for x in L['learn'])
    nb = L['nb']
    nxt = f' מה שלא הספקנו בכיתה ממשיך במפגש {n(i + 1)}.' if i < 13 else ''
    return f'''<article class="lec" id="lesson-{i}">
<div class="lec-head"><div class="lec-n">{i}</div><div><h3>{L['title']}</h3><div class="sub">מפגש {n(i)}</div></div></div>
<div class="lec-body">
<div><h4>מה לומדים במפגש</h4><ul class="learn">{li}</ul>
<div class="rec1" id="rec-{i}"><h4>הקלטת המפגש</h4>{rec(i, True)}</div>
</div>
<div><h4>חומרי המפגש</h4>
<div class="grp"><h5>1. במפגש</h5><div class="links">
<a class="lk p" href="lectures/lecture-{i}/presentation.html"><span class="e">🖥️</span><span><b>מצגת המפגש</b><span class="d">{n(L['ns'])} שקפים. כל פתרון נחשף שלב אחר שלב, ו-{n(L['nt'])} תרגילים עם בדיקה מיידית, רמזים ופתרון בשלבים.</span></span></a>
</div></div>
<div class="grp"><h5>2. אחרי המפגש, לחזרה</h5><div class="links">
<a class="lk s" href="lectures/lecture-{i}/summary.pdf" target="_blank" rel="noopener"><span class="e">📄</span><span><b>סיכום המפגש (PDF)</b><span class="d">כל תוכן המצגת במסמך אחד: הגדרות, דוגמאות, כללים, תרגילים עם פתרונות, ומילון מושגים.</span></span></a>
</div></div>
<div class="grp"><h5>3. תרגול</h5><div class="links">
<a class="lk p" href="lectures/lecture-{i}/presentation.html#s-home"><span class="e">✍️</span><span><b>תרגול עצמי לבית, בתוך המצגת</b><span class="d">{L.get('home', 'השקפים האחרונים של המצגת, לפי נושאים, עם בדיקה, רמזים ופתרון בשלבים.')}</span></span></a>
<a class="lk s" href="materials/booklet-m{i}.pdf" target="_blank" rel="noopener"><span class="e">📘</span><span><b>חוברת התרגילים: מפגש {i}</b><span class="d">תרגילים {n(f'{i}-1')} עד {n(f'{i}-{nb}')}, מהקל אל הקשה, עם תשובות סופיות בסוף.</span></span></a>
<a class="lk r" href="materials/booklet-m{i}-solutions.pdf" target="_blank" rel="noopener"><span class="e">✅</span><span><b>פתרונות החוברת: מפגש {i} (PDF)</b><span class="d">פתרון מלא בשלבים לכל תרגיל.</span></span></a>
</div></div>
</div>
</div>
<div class="todo"><h4>📝 מה עושים במפגש {n(i)}</h4><ol>
<li><b>במפגש:</b> עובדים יחד במצגת, ופותרים את הפעילויות שבתוך השקפים.</li>
<li><b>אחרי המפגש:</b> קוראים את הסיכום, ופותרים את שקפי ״תרגול עצמי לבית״ שבסוף המצגת.{nxt}</li>
<li><b>מהחוברת:</b> תרגילים {n(f'{i}-1')} עד {n(f'{i}-{nb}')}, על דף. בודקים מול התשובות הסופיות, ורק אחר כך פותחים את הפתרונות המלאים.</li>
</ol></div>
</article>'''


built = '\n'.join(lec_card(i) for i in sorted(BUILT, reverse=True))

ups = ''.join(f'''<article class="lec up" id="lesson-{i}"><div class="lec-head"><div class="lec-n">{i}</div><div><h3>{t}</h3><div class="sub">מפגש {n(i)}</div></div></div>
<div class="upb"><div><p>{d}</p><p class="soon">המצגת, הסיכום והתרגילים יעלו לאתר לקראת המפגש.</p></div>{rec(i)}</div></article>''' for i, t, d, k in PLAN if i not in BUILT)
html = f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>שיטות כמותיות בניהול | אתר הקורס</title>
<meta name="description" content="אתר הקורס שיטות כמותיות בניהול, המרכז האקדמי למשפט ולעסקים ברמת גן: מצגות אינטראקטיביות עם בדיקה מיידית, רמזים ופתרון בשלבים, סיכומים, חוברת תרגילים ופתרונות.">
<link rel="stylesheet" href="assets/fonts.css">
<style>{css}</style>
</head>
<body>
<header class="hero"><div class="wrap">
<div class="kick"><span>המרכז האקדמי למשפט ולעסקים, רמת גן</span></div>
<h1>שיטות כמותיות בניהול</h1>
<div class="h1s">כלים מתמטיים לקבלת החלטות ניהוליות</div>
<p class="lead">הקורס מלמד לנסח בעיות החלטה ולפתור אותן: עצי החלטה, תכנון לינארי ותכנון פרויקטים. ארבעת המפגשים הראשונים בונים את הבסיס המתמטי, לאט ובהדרגה, גם למי שלא נגע במתמטיקה שנים. לכל מפגש באתר: מצגת אינטראקטיבית שבודקת את התשובות שלכם ונותנת רמזים, סיכום כתוב להדפסה, וחוברת תרגילים עם פתרונות מלאים.</p>
<p class="meta">ד״ר שי צבאן · {n(13)} מפגשים · קורס חובה · {n(3)} נקודות זכות</p>
<div class="cred">קרדיט לתכנים עצמם וליצירת תוכן הקורס: <b>ד״ר אסף שריג</b><br>קרדיט לעיצוב הפדגוגי, ההמחשות, הדוגמאות, בניית המצגת ותהליך הלמידה: <b>ד״ר שי צבאן</b></div>
</div></header>
<main class="wrap">
<section class="facts">
<div class="fact"><div class="fi">🎓</div><b>הציון</b><span>בחינה מסכמת: {n('100%')} מהציון. מותרים מחשבון ודפי הנוסחאות שיצורפו לשאלון.</span></div>
<div class="fact"><div class="fi">📝</div><b>תרגילים</b><span>{n(3)} תרגילים לתרגול אישי במהלך הסמסטר, עם פתרון מלא. אין חובת הגשה.</span></div>
<div class="fact"><div class="fi">🧭</div><b>איך לומדים</b><span>במפגש עובדים במצגת. אחריו: סיכום, תרגול עצמי במצגת, וחוברת התרגילים.</span></div>
<div class="fact"><div class="fi">✉️</div><b>פניות למרצה</b><span><a href="mailto:shay.tsaban@gmail.com">shay.tsaban@gmail.com</a><br>יש לציין את שם המוסד ואת שם הקורס.</span></div>
</section>
<section class="block" id="course-files">
<h2 class="sec">קובצי הקורס</h2>
<div class="cgrid">
{lk('s', 'materials/syllabus.pdf', '📋', 'סילבוס הקורס (PDF)', f'תיאור הקורס, תוצרי הלמידה, תוכנית {n(13)} המפגשים, הרכב הציון ורשימת הקריאה.')}
{lk('s', 'materials/booklet.pdf', '📘', 'חוברת תרגילים (PDF)', f'כל המפגשים בקובץ אחד, פרק לכל מפגש. כרגע: {n(NB)} תרגילים למפגשים {n(1)} ו-{n(2)}, עם תשובות סופיות. פרק חדש נוסף אחרי כל מפגש.')}
{lk('r', 'materials/booklet-solutions.pdf', '✅', 'פתרונות החוברת המלאה (PDF)', 'פתרון מלא לכל תרגיל, שלב אחר שלב, עם הסבר לכל שלב. פותחים רק אחרי שמנסים לבד.')}
</div>
</section>
<section class="block" id="plan">
<h2 class="sec">תוכנית הקורס: {n(13)} מפגשים</h2>
<div class="halves"><span class="a">מפגשים {n(1)} עד {n(4)}: יסודות מתמטיים</span><span class="b">מפגשים {n(5)} ו-{n(6)}: תורת ההחלטות</span><span class="c">מפגשים {n(7)} עד {n(11)}: תכנון לינארי</span><span class="d">מפגשים {n(12)} ו-{n(13)}: תכנון פרויקטים וחזרה</span></div>
<div class="plan">{plan}</div>
<p class="cnote">ייתכנו שינויים בסדר הנושאים ובקצב ההתקדמות. החומרים של כל מפגש עולים לאתר לקראת המפגש.</p>
</section>
<section class="block">
<h2 class="sec">המפגשים</h2>
{built}
{ups}
</section>
<footer>ד״ר שי צבאן · פניות במייל: <a href="mailto:shay.tsaban@gmail.com">shay.tsaban@gmail.com</a>, עם שם המוסד ושם הקורס<br>{CR1} · {CR2}</footer>
</main>
</body>
</html>
'''
for bad in ('—', '־', '–'):
    assert bad not in html, bad
open(os.path.join(H, '..', 'index.html'), 'w', encoding='utf8').write(html)
print('hub', len(html), {k: (v['ns'], v['nt'], v['nb']) for k, v in LEC.items()}, 'booklet', NB)
