# Exercise booklet of a meeting and its solutions. Run: python3 build_booklet.py  ->  ../materials/booklet.pdf, booklet-solutions.pdf
import os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from qlib import *
from pdfkit import *
exec(open(os.path.join(H, 'booklet.py'), encoding='utf8').read())
COURSE = 'שיטות כמותיות בניהול'
n = 0
for eid, t, q, expr, ans, steps in EX:
    sol = solution_of(expr.lstrip('~'), ans)
    if sol is None: assert t == 1 or not re.search('[a-z]', strip(expr)) or same(expr.lstrip('~'), ans), eid   # substitution questions change the value
    else: n += 1
    for m, _ in steps:
        if m.startswith('~'): continue
        step_check(m, ans if sol is None else None, sol); n += 1
print('exercises', len(EX), 'math lines checked', n)
CSS = BASE + '''
.ex{break-inside:avoid;border:.25mm solid var(--line);border-radius:1.6mm;padding:1.6mm 2.8mm;margin:0 0 2mm;background:#fff}
.ex .id{display:inline-block;background:var(--navy);color:#fff;border-radius:1mm;padding:0 2mm;font-weight:700;margin-left:2mm;direction:ltr;unicode-bidi:isolate}
.ex .eq{font-size:14pt;text-align:center;margin:1.2mm 0 .6mm}
.two{columns:2;column-gap:5mm}
.ans td,.ans th{padding:.9mm 2.4mm;border-bottom:.25mm solid var(--line);font-size:11.4pt}.ans th{background:var(--navy);color:#fff;text-align:right}.ans{width:100%}
.ans td:first-child{width:14mm;font-weight:700;direction:ltr;unicode-bidi:isolate;text-align:right}
ol.st{margin:1mm 0;padding-right:6mm}ol.st li{margin-bottom:.9mm}ol.st .eq{font-size:12.4pt}
h1.mt{font-size:19pt;background:var(--navy);color:#fff;border:0;border-radius:1.5mm;padding:2mm 3mm;margin-top:7mm}
h2{font-size:14pt;color:var(--navy);margin:4mm 0 1.5mm;border-bottom:.5mm solid var(--coral);padding-bottom:.6mm;break-after:avoid}
.sys{direction:ltr;unicode-bidi:isolate;border-left:.8mm solid var(--navy);padding:0 3mm;margin:1mm auto;width:max-content;font-size:13pt;font-weight:700}.sys span{display:block}
.frac{display:inline-flex;flex-direction:column;align-items:center;vertical-align:middle;line-height:1.1;margin:0 .6mm;font-size:.9em}.frac>span{padding:0 1.2mm}.frac>span:first-child{border-bottom:.3mm solid currentColor}
.fin{background:var(--incbg);border-right:1.2mm solid var(--inc);border-radius:1mm;padding:.8mm 2.6mm;font-weight:700}
'''
head = lambda t, s: (f'<div class="hd"><div class="k">{COURSE} · המרכז האקדמי למשפט ולעסקים, רמת גן</div><h1 class="t">{t}</h1><div class="s">{s}</div><div class="cr">{CR1}<br>{CR2}</div></div>')
def ANS(a):
    return MI('(' + ', '.join(a) + ') = (' + ', '.join(a.values()) + ')') if isinstance(a, dict) else MI(a)


def QEQ(expr):
    if expr.startswith('~'): return ''   # a story question: writing the model is part of the exercise
    if ';' in expr: return '<div class="sys">' + ''.join(f'<span>{PM(e)}</span>' for e in expr.split(';')) + '</div>'
    return EQ(expr)


def body(sol, meetings):
    out = ''
    for mt in meetings:
        if len(meetings) > 1: out += f'<h1 class="mt">מפגש {mt}: {MEETING_TITLE[mt]}</h1>'
        k = 0
        for ti, (tm, tn) in enumerate(TOPICS):
            if tm != mt: continue
            k += 1
            out += f'<h2>{k}. {tn}</h2><div class="two">'
            for eid, t, q, expr, ans, steps in EX:
                if t != ti: continue
                b = f'<div class="ex"><p><span class="id">{eid}</span>{TX(q)}</p>{QEQ(expr)}'
                if sol:
                    b += '<ol class="st">' + ''.join(f'<li>{TX(note)}' + (EQ(m.lstrip('=~') if not m.startswith('=') else '= ' + m[1:]) if m.strip('~') else '') + '</li>' for m, note in steps) + f'</ol><div class="fin">תשובה: {ANS(ans)}</div>'
                out += b + '</div>'
            out += '</div>'
    return out
intro = ('<div class="note"><b>איך עובדים עם החוברת.</b> פותרים על דף, שורה לכל פעולה. בסוף החוברת מופיעות התשובות הסופיות, לבדיקה מהירה. '
         'הפתרון המלא של כל תרגיל, שלב אחר שלב, נמצא בקובץ הפתרונות באתר הקורס. פותחים אותו רק אחרי שמנסים לבד. התרגילים אינם להגשה.</div>')
wrap = lambda t, b: f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>{COURSE} | {t}</title><style>{CSS}</style></head><body>{b}<p class="url" style="margin-top:4mm">{SITE}</p></body></html>'
MEETINGS = sorted({m for m, _ in TOPICS})
mine = lambda ms: [e for e in EX if TOPICS[e[1]][0] in ms]
anst = lambda es: '<h1>תשובות סופיות</h1><div class="two"><table class="ans"><tr><th>תרגיל</th><th>תשובה</th></tr>' + ''.join(f'<tr><td>{e[0]}</td><td>{ANS(e[4])}</td></tr>' for e in es) + '</table></div>'
OUT = os.path.join(H, '..', 'materials')
for ms, tag, name in [(MEETINGS, '', 'כל המפגשים')] + [([m], f'-m{m}', f'מפגש {m}') for m in MEETINGS]:
    es = mine(ms)
    sub = MEETING_TITLE[ms[0]] if len(ms) == 1 else 'כל המפגשים שנלמדו עד עכשיו, פרק לכל מפגש'
    to_pdf(wrap('חוברת תרגילים', head(f'חוברת תרגילים: {name}', f'{sub}. {len(es)} תרגילים, מהקל אל הקשה.') + intro + body(False, ms) + anst(es)), os.path.join(OUT, f'booklet{tag}.pdf'))
    to_pdf(wrap('פתרונות חוברת התרגילים', head(f'פתרונות חוברת התרגילים: {name}', 'פתרון מלא לכל תרגיל, שלב אחר שלב, עם הסבר לכל שלב.') + body(True, ms)), os.path.join(OUT, f'booklet{tag}-solutions.pdf'))
