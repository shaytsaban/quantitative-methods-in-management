# Meeting 3, in deck order. Run through build_deck.py 3 / build_summary.py 3.
# Built 2026-11-26. At the academic supervisor's request percentages are TAUGHT in class (part 1), and inequalities are not
# taught for now (content_later_ineq.py). Then the syllabus topics of meeting 3: the function, domain and range; the linear
# function; parallel and perpendicular lines; intersection points.
# Lessons from meeting 2 (Shay's board annotations, 26.11), applied on every slide here:
#  - no expression "in the air": every expression is built from the story or from the previous line, in view;
#  - a numeric example under every rule; nothing decorative (the balance-scale slide was dropped);
#  - one technique per task, his: move terms so the unknown's coefficient stays positive, the operation beside the line
#    ("/ :2"), substitution with the substituted expression highlighted and in brackets;
#  - in class, a worked slide (one line per click, the reason on every line) before students try alone;
#  - the question never prescribes a different technique from the one taught.
import math as _math

LMETA = dict(date='', h1=('אחוזים, פונקציות', 'והקו הישר'), title='אחוזים, פונקציות והקו הישר',
             sub='אחוזים: מקדם שינוי, שינויים ברצף ושיעור שינוי. פונקציה, תחום וטווח. הקו הישר: שיפוע, משוואה משתי נקודות, מקבילים ומאונכים, ונקודת חיתוך. כל נושא נפתח בדוגמה, ומגיע לכלל רק אחריה.',
             cover='חזרה על מפגש 2; אחוזים: אחוז מסכום, מקדם שינוי, שני שינויים ברצף, שיעור שינוי ומחיר מקורי בעזרת משוואה; מושג הפונקציה, הצבה, תחום הגדרה וטווח; הפונקציה הלינארית: שיפוע ונקודת חיתוך עם ציר y, חיתוך עם הצירים, משוואת ישר דרך שתי נקודות, ישרים מקבילים ומאונכים; נקודת חיתוך של שני ישרים; תרגול עצמי לפי נושאים, עם פתרון מפורט.',
             next_h='משוואה ממעלה שנייה, והפרבולה', next_t='מפגש 4 ממשיך מהקו הישר אל הפרבולה: פתרון משוואה ממעלה שנייה, נקודות החיתוך של פרבולה עם הצירים, הקודקוד שלה, וחיתוך בין שתי פרבולות.')
TOTAL_PARTS = 5

G.update({
 'func': dict(h='פונקציה', en='Function', p='כלל שנותן לכל מספר שנכנס מספר אחד בלבד שיוצא.', f='התאמה שמתאימה לכל ערך של $x$ בתחום ההגדרה ערך אחד ויחיד של $y$.', ex='במונית $f(x) = 4x + 10$: לכל מרחק $x$, מחיר אחד.', tr='מותר ששני מספרים שונים ייתנו אותו $y$. אסור ש-$x$ אחד ייתן שני ערכים.'),
 'range': dict(h='טווח', en='Range', p='כל הערכים ש-$y$ יכול לקבל.', f='קבוצת הערכים שהפונקציה מקבלת, כאשר $x$ עובר על כל תחום ההגדרה.', ex='$y = x^2$: הטווח הוא $y ≥ 0$, כי ריבוע אף פעם לא שלילי.', tr='תחום: מה נכנס ($x$). טווח: מה יוצא ($y$).'),
 'linear': dict(h='פונקציה לינארית', en='Linear function', p='פונקציה שהגרף שלה הוא קו ישר.', f='פונקציה מהצורה $y = mx + b$.', ex='$y = 4x + 10$.', tr='$x$ מופיע בחזקה 1 בלבד. $y = x^2$ אינה לינארית.'),
 'slope': dict(h='שיפוע', en='Slope', p='בכמה $y$ משתנה כש-$x$ גדל ב-1.', f='המקדם $m$ במשוואה $y = mx + b$. משתי נקודות: ההפרש ב-$y$ חלקי ההפרש ב-$x$.', ex='מ-$(1, 14)$ ל-$(3, 22)$: $m = 8/2 = 4$.', tr='שיפוע שלילי: הקו יורד. שיפוע 0: הקו אופקי.'),
 'yint': dict(h='נקודת החיתוך עם ציר y', en='y-intercept', p='הערך של $y$ כש-$x = 0$.', f='המספר $b$ במשוואה $y = mx + b$: הישר חותך את ציר $y$ בנקודה $(0, b)$.', ex='$y = 2x - 4$ חותך את ציר $y$ ב-$(0, -4)$.', tr='$b$ נקרא עם הסימן שלו.'),
 'parallel': dict(h='ישרים מקבילים', en='Parallel lines', p='ישרים עם אותו שיפוע, שלא נפגשים אף פעם.', f='שני ישרים מקבילים כאשר $m_1 = m_2$, ו-$b$ שונה.', ex='$y = 2x + 1$ ו-$y = 2x + 5$.', tr='אותו שיפוע ואותו $b$: זה אותו ישר.'),
 'perp': dict(h='ישרים מאונכים', en='Perpendicular lines', p='ישרים שנחתכים בזווית ישרה.', f='שני ישרים מאונכים כאשר מכפלת השיפועים שלהם היא $-1$.', ex='$y = 2x + 1$ ו-$y = -0.5x + 4$: $2·(-0.5) = -1$.', tr='השיפוע המאונך: הופכים את השבר ומחליפים סימן. 2 הופך ל-$-1/2$.'),
 'inter': dict(h='נקודת חיתוך', en='Intersection point', p='נקודה שנמצאת על שני הגרפים.', f='זוג $(x, y)$ שמקיים את שתי המשוואות. זה הפתרון של מערכת המשוואות.', ex='$y = 4x + 10$ ו-$y = 6x + 4$ נחתכים ב-$(3, 22)$.', tr='אחרי שמוצאים את $x$, חוזרים לאחת המשוואות כדי למצוא את $y$.'),
})


# ---------------------------------------------------------------- lesson 3 helpers
def SYS(*eqs, n=0):
    """Two equations, one under the other, with the system bracket on the left."""
    h = '<div class="sys" dir="ltr">' + ''.join(f'<span class="sysl">{PM(e)}</span>' for e in eqs) + '</div>'
    return ST(n, h, cls='pop') if n else h


def CHK(line_, *ats, **at):
    """A worked line that is true only at given values (a slope, an intercept, a point): checked there, then shown
    unchecked by the generic line check (which would read the letters as free variables)."""
    for a in (ats or (at,)):
        eq_check(line_, {k: float(v) for k, v in a.items()}); NCHK[0] += 1
    return '~' + line_


def TAIL(m):
    """A line 'f(3) = 4·3 + 10 = 22': everything after the first '=' is checked as a numeric chain."""
    chain(m.split('=', 1)[1]); NCHK[0] += 1
    return '~' + m


def MINI(n0, rows):
    """A short worked solution inside a slide: one numbered line per click. Rows are already checked (CHK / TAIL / '~')."""
    out = ''
    for i, (m, note) in enumerate(rows):
        if not m.startswith('~'): chain(m); NCHK[0] += 1
        m = m.lstrip('~')
        out += ST(n0 + i, f'<div class="wn"><b>{i + 1}</b><span>{TX(note)}</span></div>{EQ(m) if m else ""}', cls='wkr' + (' fin' if i == len(rows) - 1 else ''))
    return f'<div class="wk xs">{out}</div>'


def _num(v):
    v = round(v, 6)
    s = str(int(v)) if v == int(v) else str(v)
    return s.replace('-', '−')


def PLANE(xr, yr, lines=(), pts=(), tris=(), marks=(), W=440, H=None, xs=1, ys=1, xt=None, yt=None, eq=False, n=0, mw=None):
    """A coordinate plane. lines: dicts m, b, col, n (click), lab (math), at (x of the label). pts: (x, y, col, n, label).
    tris: slope triangles (x1, y1, x2, y2, col, n). marks: right angles (x, y, m1, m2, n). eq: the same unit on both axes,
    so perpendicular lines look perpendicular. No Hebrew inside the SVG: numbers and math only."""
    L, R, T, B = 40, 16, 14, 32
    x0, x1 = xr; y0, y1 = yr
    if eq or H is None:
        H = int(round(T + B + (W - L - R) * (y1 - y0) / (x1 - x0))) if eq else 340
    sx = (W - L - R) / (x1 - x0); sy = (H - T - B) / (y1 - y0)
    X = lambda v: L + (v - x0) * sx
    Y = lambda v: T + (y1 - v) * sy
    xt, yt = xt or xs, yt or ys
    g = ''
    v = _math.ceil(x0 / xs) * xs
    while v <= x1 + 1e-9:
        g += f'<line x1="{X(v):.1f}" y1="{T}" x2="{X(v):.1f}" y2="{H - B}" stroke="#ebe6da" stroke-width="1.2"/>'; v += xs
    v = _math.ceil(y0 / ys) * ys
    while v <= y1 + 1e-9:
        g += f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W - R}" y2="{Y(v):.1f}" stroke="#ebe6da" stroke-width="1.2"/>'; v += ys
    ay = Y(0) if y0 <= 0 <= y1 else Y(y0)
    ax = X(0) if x0 <= 0 <= x1 else X(x0)
    g += (f'<line x1="{L - 6}" y1="{ay:.1f}" x2="{W - R + 6}" y2="{ay:.1f}" stroke="#1b2d55" stroke-width="2.2"/>'
          f'<polygon points="{W - R + 12},{ay:.1f} {W - R + 2},{ay - 5:.1f} {W - R + 2},{ay + 5:.1f}" fill="#1b2d55"/>'
          f'<line x1="{ax:.1f}" y1="{H - B + 6}" x2="{ax:.1f}" y2="{T - 6}" stroke="#1b2d55" stroke-width="2.2"/>'
          f'<polygon points="{ax:.1f},{T - 12} {ax - 5:.1f},{T - 2} {ax + 5:.1f},{T - 2}" fill="#1b2d55"/>'
          + _t(W - R + 4, ay - 10, 'x', 18, '#1b2d55') + _t(ax + 12, T + 2, 'y', 18, '#1b2d55'))
    v = _math.ceil(x0 / xt) * xt
    while v <= x1 + 1e-9:
        if abs(v) > 1e-9: g += _t(X(v), min(ay + 20, H - 6), _num(v), 14, '#5d6a86', 600, math=False)
        v += xt
    v = _math.ceil(y0 / yt) * yt
    while v <= y1 + 1e-9:
        if abs(v) > 1e-9: g += _t(ax - 8, Y(v) + 5, _num(v), 14, '#5d6a86', 600, 'end', math=False)
        v += yt
    if x0 <= 0 <= x1 and y0 <= 0 <= y1: g += _t(ax - 8, ay + 18, '0', 14, '#5d6a86', 600, 'end', math=False)
    parts = [g]
    for ln in lines:
        m, b = ln['m'], ln['b']
        xa, xb = x0, x1
        if m:
            c0, c1 = sorted(((y0 - b) / m, (y1 - b) / m))
            xa, xb = max(x0, c0), min(x1, c1)
        col = ln.get('col', '#ff6a4d')
        seg = f'<line x1="{X(xa):.1f}" y1="{Y(m * xa + b):.1f}" x2="{X(xb):.1f}" y2="{Y(m * xb + b):.1f}" stroke="{col}" stroke-width="3.2" stroke-linecap="round" pathLength="1"/>'
        lab = ''
        if ln.get('lab'):
            lx = ln.get('at', xb - (xb - xa) * .12)
            ly = m * lx + b
            lab = _t(X(lx) + ln.get('dx', 0), Y(ly) + ln.get('dy', -12), ln['lab'], 16, col, 800, ln.get('anchor', 'end'))
        parts.append(_g(ln.get('n', 0), seg, 'draw') + (_g(ln.get('n', 0), lab, 'fade') if lab else ''))
    for tr in tris:
        xa, ya, xb, yb, col, k = tr[:6]
        k2 = tr[6] if len(tr) > 6 else k
        run = (f'<line x1="{X(xa):.1f}" y1="{Y(ya):.1f}" x2="{X(xb):.1f}" y2="{Y(ya):.1f}" stroke="{col}" stroke-width="2.6" stroke-dasharray="6 5"/>'
               + _t((X(xa) + X(xb)) / 2, Y(ya) + (20 if yb > ya else -10), ('+' if xb > xa else '') + _num(xb - xa), 16, col, 800, math=False))
        rise = (f'<line x1="{X(xb):.1f}" y1="{Y(ya):.1f}" x2="{X(xb):.1f}" y2="{Y(yb):.1f}" stroke="{col}" stroke-width="2.6" stroke-dasharray="6 5"/>'
                + _t(X(xb) + 8, (Y(ya) + Y(yb)) / 2 + 5, ('+' if yb > ya else '') + _num(yb - ya), 16, col, 800, 'start', math=False))
        parts.append(_g(k, run, 'fade') + _g(k2, rise, 'fade'))
    for xa, ya, m1, m2, k in marks:
        def u(m):
            dx, dy = sx, -m * sy
            r = (dx * dx + dy * dy) ** .5
            return dx / r * 13, dy / r * 13
        (ux, uy), (vx, vy) = u(m1), u(m2)
        if vx * 1 < 0: vx, vy = -vx, -vy
        px, py = X(xa), Y(ya)
        parts.append(_g(k, f'<path d="M{px + ux:.1f} {py + uy:.1f} L{px + ux + vx:.1f} {py + uy + vy:.1f} L{px + vx:.1f} {py + vy:.1f}" fill="none" stroke="#1b2d55" stroke-width="2"/>', 'fade'))
    for p in pts:
        xa, ya, col, k = p[:4]
        lab = p[4] if len(p) > 4 else f'({_num(xa)}, {_num(ya)})'
        anc = p[5] if len(p) > 5 else 'start'
        dx = 10 if anc == 'start' else -10
        parts.append(_g(k, f'<circle cx="{X(xa):.1f}" cy="{Y(ya):.1f}" r="6.5" fill="{col}" stroke="#fff" stroke-width="2"/>'
                        + (_t(X(xa) + dx, Y(ya) - 10, lab, 15, col, 800, anc, math=False) if lab else ''), 'pop'))
    st = f' style="max-width:{mw}px;margin:0 auto"' if mw else ''
    return f'<div class="diagw plane"{st}><svg class="diag" dir="ltr" viewBox="-4 -8 {W + 10} {H + 12}" role="img">{"".join(parts)}</svg></div>'


for _f in ('content_l3a.py', 'content_l3b.py', 'content_l3c.py', 'content_l3h.py'):
    exec(R(_f))

# Home practice, after s-home, by topic; the kick shows the topic.
HOME_T = {'hx-p': 'אחוזים', 'h-p': 'אחוזים', 'h-p2': 'אחוזים',
          'hx-f': 'פונקציות', 'h-f': 'פונקציות',
          'hx-l': 'משוואת הישר', 'h-l': 'משוואת הישר', 'h-l2': 'משוואת הישר',
          'h-pp': 'מקבילים ומאונכים',
          'hx-i': 'נקודות חיתוך', 'h-i': 'נקודות חיתוך', 'hw-i': 'נקודות חיתוך'}
HOME = list(HOME_T)
_by = {x['id']: x for x in SL}
assert all(k in _by for k in HOME), [k for k in HOME if k not in _by]
SL[:] = [x for x in SL if x['id'] not in HOME]
_at = next(i for i, x in enumerate(SL) if x['id'] == 's-home') + 1
for _j, _k in enumerate(HOME):
    _x = _by[_k]
    _x['part'] = 5
    _x['kick'] = 'חלק 5 · תרגול עצמי · ' + HOME_T[_k]
    SL.insert(_at + _j, _x)

# The purpose of every slide, shown beside the part label.
GOAL = {
 's-recap': 'להיזכר בטכניקות של מפגש 2 שנשתמש בהן היום', 's-recap-try': 'לוודא שהטכניקות של מפגש 2 זמינות', 's-role': 'לדעת מה כל נושא משרת בהמשך', 's-route': 'לראות את הדרך כולה',
 'pc-def': 'להבין מהו אחוז, ולחשב אחוז מסכום', 'pc-of': 'לחשב אחוז מסכום, בכמה סכומים', 'pc-up': 'להבין מאיפה בא מקדם השינוי', 'pc-fac': 'לתרגם עלייה או ירידה למקדם',
 'pc-two': 'לחשב שני שינויים ברצף', 'pc-mc': 'לגלות למה אחוזים לא מתבטלים זה בזה', 'pc-change': 'למדוד בכמה אחוזים השתנה מחיר', 'pc-try': 'לתרגל שיעור שינוי, בעלייה ובירידה',
 'pc-back': 'למצוא מחיר מקורי בעזרת משוואה', 'pc-btry': 'לפתור לבד: מחיר מקורי אחרי שני שינויים',
 'f-story': 'לראות קשר שבו כל מספר נותן מספר אחד', 'f-def': 'להכיר את המילה פונקציה ואת הסימון f(x)', 'f-try': 'להציב בפונקציה, ולחזור ממנה למשוואה', 'f-is': 'להבחין בין פונקציה למה שאינו פונקציה',
 'f-domain': 'למצוא אילו מספרים אסור להציב', 'f-range': 'להבין מה הפונקציה יכולה לתת', 'f-dtry': 'לתרגל תחום הגדרה', 'f-rmc': 'לבדוק שהטווח ברור',
 'l-story': 'לראות שהמונית היא קו ישר, ולקרוא ממנו שני מספרים', 'l-def': 'להכיר את שני המספרים שקובעים קו ישר: m ו-b', 'l-read': 'לקרוא שיפוע ו-b ממשוואה',
 'l-axes': 'לשרטט ישר בעזרת החיתוך עם הצירים', 'l-slope': 'לחשב שיפוע משתי נקודות', 'l-two': 'למצוא משוואת ישר משתי נקודות, בארבעה שלבים', 'l-try': 'לתרגל משוואת ישר משתי נקודות',
 'l-par': 'למצוא ישר מקביל דרך נקודה', 'l-perp': 'למצוא ישר מאונך דרך נקודה', 'l-sort': 'לזהות מקבילים ומאונכים לפי השיפוע', 'l-try2': 'לתרגל ישרים מקבילים ומאונכים',
 'i-story': 'למצוא נקודת חיתוך בשיטת ההצבה', 'i-try': 'לתרגל נקודת חיתוך',
 's-rules': 'כל הכללים במקום אחד, לחזרה ולתרגול', 's-split': 'לדעת מה עושים בבית, ובאיזה סדר', 'x-1': 'לבדוק לבד: אחוזים מסיפור', 'x-2': 'לבדוק לבד: נקודת איזון כנקודת חיתוך', 'x-3': 'לבדוק לבד: קו ישר מסיפור',
 's-home': 'לבחור נושא לתרגול', 'hx-p': 'לזהות אחוז שנלקח מהמחיר הלא נכון', 'h-p': 'לתרגל אחוזים, מהקל אל הקשה', 'h-p2': 'לתרגל שינויים ברצף ומחיר מקורי',
 'hx-f': 'לזהות סימן שגוי בהצבה של מספר שלילי', 'h-f': 'לתרגל הצבה, תחום וטווח', 'hx-l': 'לזהות שיפוע שחושב הפוך', 'h-l': 'לתרגל משוואת ישר משתי נקודות', 'h-l2': 'לתרגל חיתוך עם הצירים',
 'h-pp': 'לתרגל מקבילים ומאונכים', 'hx-i': 'לזהות סימן שלא התהפך בהעברת אגף', 'h-i': 'לתרגל נקודות חיתוך', 'hw-i': 'לפתור בעיה מילולית בעזרת נקודת חיתוך'}
for _s in SL:
    if _s['kind'] == 'opener': continue
    _s['goal'] = 'לעצור, ולוודא שהעיקר ברור לפני שממשיכים' if _s['id'].startswith('s-sum') else GOAL[_s['id']]
assert not set(GOAL) - {x['id'] for x in SL}, set(GOAL) - {x['id'] for x in SL}
