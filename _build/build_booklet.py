# Exercise booklet of a meeting and its solutions. Run: python3 build_booklet.py  ->  ../materials/booklet.pdf, booklet-solutions.pdf
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from qlib import *
from pdfkit import *
exec(open(os.path.join(H, 'booklet.py'), encoding='utf8').read())
COURSE = 'שיטות כמותיות בניהול'
n = 0
for eid, t, q, expr, ans, steps in EX:
    assert same(expr, ans) or not __import__('re').search('[a-z]', strip(expr)) or t == 1, eid   # substitution questions change the value
    for m, _ in steps:
        if m.startswith('='): chain(m[1:], ans); n += 1
        elif not m.startswith('~'): chain(m); n += 1
print('exercises', len(EX), 'math lines checked', n)
CSS = BASE + '''
.ex{break-inside:avoid;border:.25mm solid var(--line);border-radius:1.6mm;padding:1.6mm 2.8mm;margin:0 0 2mm;background:#fff}
.ex .id{display:inline-block;background:var(--navy);color:#fff;border-radius:1mm;padding:0 2mm;font-weight:700;margin-left:2mm;direction:ltr;unicode-bidi:isolate}
.ex .eq{font-size:14pt;text-align:center;margin:1.2mm 0 .6mm}
.two{columns:2;column-gap:5mm}
.ans td,.ans th{padding:.9mm 2.4mm;border-bottom:.25mm solid var(--line);font-size:11.4pt}.ans th{background:var(--navy);color:#fff;text-align:right}.ans{width:100%}
.ans td:first-child{width:14mm;font-weight:700;direction:ltr;unicode-bidi:isolate;text-align:right}
ol.st{margin:1mm 0;padding-right:6mm}ol.st li{margin-bottom:.9mm}ol.st .eq{font-size:12.4pt}
.fin{background:var(--incbg);border-right:1.2mm solid var(--inc);border-radius:1mm;padding:.8mm 2.6mm;font-weight:700}
'''
head = lambda t, s: (f'<div class="hd"><div class="k">{COURSE} · המרכז האקדמי למשפט ולעסקים, רמת גן</div><h1 class="t">{t}</h1><div class="s">{s}</div><div class="cr">{CR1}<br>{CR2}</div></div>')
def body(sol):
    out = ''
    for ti, tn in enumerate(TOPICS):
        out += f'<h1>{ti + 1}. {tn}</h1><div class="two">'
        for eid, t, q, expr, ans, steps in EX:
            if t != ti: continue
            b = f'<div class="ex"><p><span class="id">{eid}</span>{TX(q)}</p>{EQ(expr)}'
            if sol:
                b += '<ol class="st">' + ''.join(f'<li>{TX(note)}' + (EQ(m.lstrip('=~') if not m.startswith('=') else '= ' + m[1:]) if m.strip('~') else '') + '</li>' for m, note in steps) + f'</ol><div class="fin">תשובה: {MI(ans)}</div>'
            out += b + '</div>'
        out += '</div>'
    return out
intro = ('<div class="note"><b>איך עובדים עם החוברת.</b> פותרים על דף, שורה לכל פעולה. בסוף החוברת מופיעות התשובות הסופיות, לבדיקה מהירה. '
         'הפתרון המלא של כל תרגיל, שלב אחר שלב, נמצא בקובץ הפתרונות באתר הקורס. פותחים אותו רק אחרי שמנסים לבד. התרגילים אינם להגשה.</div>')
ans = '<h1>תשובות סופיות</h1><div class="two"><table class="ans"><tr><th>תרגיל</th><th>תשובה</th></tr>' + ''.join(f'<tr><td>{e[0]}</td><td>{MI(e[4])}</td></tr>' for e in EX) + '</table></div>'
wrap = lambda t, b: f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>{COURSE} | {t}</title><style>{CSS}</style></head><body>{b}<p class="url" style="margin-top:4mm">{SITE}</p></body></html>'
to_pdf(wrap('חוברת תרגילים', head('חוברת תרגילים: מפגש 1', f'ריענון באלגברה ומיומנויות אלגבריות. {len(EX)} תרגילים בשבעה נושאים, מהקל אל הקשה.') + intro + body(False) + ans), os.path.join(H, '..', 'materials', 'booklet.pdf'))
to_pdf(wrap('פתרונות חוברת התרגילים', head('פתרונות חוברת התרגילים: מפגש 1', 'פתרון מלא לכל תרגיל, שלב אחר שלב, עם הסבר לכל שלב.') + body(True)), os.path.join(H, '..', 'materials', 'booklet-solutions.pdf'))
