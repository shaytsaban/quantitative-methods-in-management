# Lesson content helpers, shared by the deck and the summary. Executed with MODE = 'deck' or 'pdf'.
# The lesson itself is in content_l<N>*.py. Every worked line is checked numerically while the deck is built (qlib.chain).
from qlib import *
from toons import TOONS
import json, re, html as _html

COURSE = 'שיטות כמותיות בניהול'
INST = 'המרכז האקדמי למשפט ולעסקים, רמת גן'
CREDIT = 'קרדיט לתכנים עצמם וליצירת תוכן הקורס: ד״ר אסף שריג. קרדיט לעיצוב הפדגוגי, ההמחשות, הדוגמאות, בניית המצגת ותהליך הלמידה: ד״ר שי צבאן.'
LESSON = globals().get('LESSON', 1)
SL = []            # every slide, in order
CUR = [None]       # current part number
NACT = [0]         # activities
NCHK = [0]         # math lines verified


def S(sid, title, h, body, kick=None, cls='', kind='slide'):
    assert not any(s['id'] == sid for s in SL), 'duplicate slide id ' + sid
    SL.append(dict(id=sid, title=title, h=h, body=body, kick=kick, cls=cls, kind=kind, part=CUR[0]))


def ST(n, html, tag='div', cls=''):
    return f'<{tag} class="st {cls}" data-n="{n * 10}">{html}</{tag}>'


def KICK(t):
    return f'חלק {CUR[0]} · {t}' if CUR[0] else t


def DEF(name, text, demo, n=0, trm=None, cls=''):
    """One definition with its small demonstration. The English name, in brackets at the end, is isolated."""
    m = re.search(r'\s*\(([A-Za-z][^()]*)\)$', name)
    en = f' <bdi class="den" dir="ltr">({m.group(1)})</bdi>' if m else ''
    if m: name = name[:m.start()]
    hd = f'[[{trm}|{name}]]' if trm else name
    inner = f'<b class="dn">{TX(hd)}{en}</b><p>{TX(text)}</p><div class="demo"><b>דוגמה:</b> {TX(demo)}</div>'
    return ST(n, inner, cls='card def ' + cls) if n else f'<div class="card def {cls}">{inner}</div>'


def BAND(kind, text, n=0):
    lab = {'dg': 'דגש', 'trap': 'המלכודת', 'tip': 'טיפ', 'real': 'בעולם האמיתי'}.get(kind, '')
    k = 'note' if kind == 'real' else kind
    inner = (f'<b>{lab}:</b> ' if lab else '') + TX(text)
    return ST(n, inner, cls='band ' + k) if n else f'<div class="band {k}">{inner}</div>'


def TABLE(head, rows, cls='', n0=0):
    """n0: when set, row k is revealed at step n0 + k."""
    h = ''.join(f'<th>{TX(x)}</th>' for x in head)
    b = ''.join(f'<tr{(" class=" + chr(34) + "st" + chr(34) + " data-n=" + chr(34) + str((n0 + i) * 10) + chr(34)) if n0 else ""}>' + ''.join(f'<td>{TX(c)}</td>' for c in r) + '</tr>' for i, r in enumerate(rows))
    return f'<table class="tbl2 {cls}"><tr>{h}</tr>{b}</table>'


def CARD(html, n=0, cls=''):
    return ST(n, html, cls='card ' + cls) if n else f'<div class="card {cls}">{html}</div>'


def P(t, cls='lg'):
    return f'<p class="{cls}">{TX(t)}</p>'


def opener(n, title, q, learn, mins, note=''):
    CUR[0] = n
    SL.append(dict(id=f'p-{n}', title=f'פתיחת חלק {n}: {title}', h=title, kind='opener', part=n, q=q, learn=learn, mins=mins, note=note, cls='', kick=None, body=''))


def _svg(inner, vb='0 0 120 120', cls=''):
    return f'<svg viewBox="{vb}" dir="ltr" class="{cls}" role="img" aria-hidden="true">{inner}</svg>'


def TOON(key, punch, n=0):
    """A small cartoon with a punchline, in the empty corner of a slide. Not printed in the summary."""
    if MODE == 'pdf': return ''
    inner = f'{_svg(TOONS[key])}<div class="bub">{TX(punch)}</div>'
    return ST(n, inner, cls='toon') if n else f'<div class="toon">{inner}</div>'


# ---------------------------------------------------------------- multiple choice
def mc(qid, q, opts, why):
    """Options are written with the right answer first; a fixed rotation per question places it."""
    r = sum(map(ord, qid)) % len(opts)
    opts = opts[-r:] + opts[:-r] if r else opts
    a = r % len(opts)
    o = ''
    for i, t in enumerate(opts):
        mark = ' correct' if MODE == 'pdf' and i == a else ''
        o += f'<button class="o{mark}" data-i="{i}">{"אבגדה"[i]}. {TX(t)}</button>'
    return f'<div class="mc" data-a="{a}" id="{qid}"><div class="q">{TX(q)}</div>{o}<div class="w"><b>הסבר:</b> {TX(why)}</div></div>'


def MC1(sid, title, q, opts, why, art=None, story=None):
    """One multiple choice question on its own slide, in large type, with an illustration beside it."""
    item = mc(sid + '-q', q, opts, why)
    if MODE == 'pdf':
        S(sid, title, title, (f'<p>{TX(story)}</p>' if story else '') + item); return
    NACT[0] += 1
    side = f'<div class="mc1art">{_svg(TOONS[art])}</div>' if art else ''
    st = f'<div class="card qstem mc1s"><p>{TX(story)}</p></div>' if story else ''
    S(sid, title, title, f'<div class="mc1">{side}<div class="mc1q">{st}{item}</div></div>', kick=KICK('בדיקת הבנה'))


# ---------------------------------------------------------------- sorter
RST = '<button class="abtn ghost rst">איפוס</button>'


def SORTER(aid, title, h, task, options, rows):
    """Each row gets one right answer out of options. rows: (text, answer index, why)."""
    if MODE == 'pdf':
        t = ''.join(f'<tr><td>{TX(a)}</td><td><b>{TX(options[b])}</b></td><td>{TX(c)}</td></tr>' for a, b, c in rows)
        S(aid, title, h, f'<p>{TX(task)}</p><table class="tbl2"><tr><th>השורה</th><th>תשובה</th><th>נימוק</th></tr>{t}</table>')
        return
    NACT[0] += 1
    r = ''
    for a, b, c in rows:
        bs = ''.join(f'<button class="so" data-i="{i}">{TX(o)}</button>' for i, o in enumerate(options))
        r += f'<tr class="srow" data-a="{b}" data-w="{_html.escape(TX(c), quote=True)}"><td>{TX(a)}</td><td>{bs}</td></tr>'
    body = (f'<div class="act sorter" id="{aid}-w"><div class="tasktxt"><b>המשימה:</b> {TX(task)}</div><table class="stbl">{r}</table>'
            f'<div class="fbbar">בחרו תשובה בכל שורה.</div><div class="actbar">{RST}<span class="score">0 / {len(rows)}</span></div></div>')
    S(aid, title, h, body, kick=KICK('פעילות'))


# ---------------------------------------------------------------- worked solutions and typed answers
def _line(x, target):
    """One stage: (math, note). '=...' must equal the target, '~...' is not checked, anything else is checked side against side."""
    m, note = x
    if m.startswith('~'):
        m = m[1:]
    elif m.startswith('='):
        chain(m[1:], target); NCHK[0] += 1
    else:
        chain(m); NCHK[0] += 1
    return m, note


def _nterms(a):
    s, d, n = strip(a), 0, 1
    for i, c in enumerate(s):
        if c == '(': d += 1
        elif c == ')': d -= 1
        elif c in '+-' and d == 0 and i and s[i - 1] not in '^*/(': n += 1
    return n


def WORK(sid, tag, title, stem, steps, expr=None, ans=None, tip=None, extra='', size='', layout='', kick=None):
    """A worked example: the full question beside its solution, one stage per click, the note above each equation.
    expr: the expression of the question, shown large in the question card. ans: the target of every '=' line."""
    target = ans if ans is not None else expr
    rows = [_line(x, target) for x in steps]
    stem_html = ''.join(f'<p>{TX(x)}</p>' for x in stem) + (EQ(expr) if expr else '')
    if MODE == 'pdf':
        li = ''.join(f'<li>{TX(note)} {MI(m) if m else ""}</li>' for m, note in rows)
        S(sid, title, title, f'<div class="qstem">{stem_html}</div>{extra}<ol class="steps">{li}</ol>' + (BAND('tip', tip) if tip else ''))
        return
    r = ''
    for i, (m, note) in enumerate(rows):
        fin = ' fin' if i == len(rows) - 1 else ''
        r += ST(i + 1, f'<div class="wn"><b>{i + 1}</b><span>{TX(note)}</span></div>{EQ(m) if m else ""}', cls='wkr' + fin)
    end = BAND('tip', tip, len(rows) + 1) if tip else ''
    body = f'<div class="qg {layout}"><div class="qr"><div class="card qstem">{stem_html}</div>{extra}</div><div class="solw"><div class="wk {size}">{r}</div>{end}</div></div>'
    S(sid, title, title, body, kick=kick or KICK(tag), cls='qslide')


def _trydata(a, form, terms, out, nb, traps):
    letters = sorted(set(re.findall(r'[a-z]', strip(a))))
    if form is None: form = 'exp' if letters else 'num'
    d = f' data-a="{strip(a)}" data-form="{form}"'
    if form == 'exp': d += f' data-terms="{terms or _nterms(a)}"'
    if out: d += f' data-out="{strip(out)}"'
    if nb: d += f' data-nb="{nb}"'
    if traps:
        for x, _ in traps: ev(x)
        d += ' data-traps="' + _html.escape(json.dumps([[strip(x), TX(m)] for x, m in traps], ensure_ascii=False), quote=True) + '"'
    return d, letters


def _trysol(a, steps):
    rows = [_line(x, a) for x in steps]
    h = ''.join(f'<div class="tstep{" fin" if i == len(rows) - 1 else ""}"><div class="wn">{TX(note)}</div>{EQ(m) if m else ""}</div>' for i, (m, note) in enumerate(rows))
    return rows, h


BTN = '<button class="abtn chk">בדיקה</button><button class="abtn ghost hintb">רמז</button><button class="abtn ghost solb">פתרון בשלבים</button>'
IDLE = 'הקלידו תשובה ולחצו ״בדיקה״. חזקה כותבים עם הסימן <span class="n">^</span>, למשל <span class="n">x^2</span>.'


def TRY(qid, q, a, hints=(), steps=(), form=None, terms=None, out=None, nb=None, traps=(), w='', num=None, vars_=None):
    """A compact question with a typed answer. The answer is checked as an expression, not as text."""
    d, letters = _trydata(a, form, terms, out, nb, traps)
    rows, sol = _trysol(a, steps)
    vs = vars_ or ''.join(sorted(set(letters) | set(re.findall(r'[a-z]', strip(' '.join(re.findall(r'\$([^$]*)\$', q))))))) or 'x'
    lab = f'<span class="tn">{num}</span>' if num else ''
    if MODE == 'pdf':
        li = ' '.join(f'{TX(note)} {MI(m)}.' for m, note in rows)
        return f'<div class="tryp"><p><b>{num + ". " if num else ""}</b>{TX(q)}</p><p class="tsl"><b>פתרון:</b> {li}</p><p><b>תשובה:</b> {MI(a)}</p></div>'
    NACT[0] += 1
    hh = ''.join(f'<div>{TX(x)}</div>' for x in hints)
    return (f'<div class="act try" id="{qid}"{d} data-vars="{vs}" data-w="{_html.escape(TX(w), quote=True)}"><div class="tq">{lab}<span>{TX(q)}</span></div>'
            f'<div class="trow"><input class="ex" dir="ltr" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="תשובה">{BTN}</div>'
            f'<div class="fbbar">{IDLE}</div><div class="hints">{hh}</div><div class="tsol" hidden>{sol}</div></div>')


def TRYS(sid, title, h, items, intro=None, cols=2, kick='נסו בעצמכם', after=''):
    pre = f'<p class="lead">{TX(intro)}</p>' if intro else ''
    if MODE == 'pdf':
        S(sid, title, h, pre + ''.join(items) + after); return
    S(sid, title, h, pre + f'<div class="trys c{cols}">' + ''.join(items) + '</div>' + after, kick=KICK(kick))


def TRYBIG(sid, tag, title, stem, a, hints=(), steps=(), expr=None, form=None, terms=None, out=None, nb=None, traps=(), w='', tip=None, extra='', vars_=None):
    """One exercise on its own slide: the full question and the answer box on the right, the staged solution on the left."""
    d, letters = _trydata(a, form, terms, out, nb, traps)
    rows, sol = _trysol(a, steps)
    stem_html = ''.join(f'<p>{TX(x)}</p>' for x in stem) + (EQ(expr) if expr else '')
    vs = vars_ or ''.join(sorted(set(letters) | set(re.findall(r'[a-z]', strip(expr or ''))))) or 'x'
    if MODE == 'pdf':
        li = ''.join(f'<li>{TX(note)} {MI(m)}</li>' for m, note in rows)
        S(sid, title, title, f'<div class="qstem">{stem_html}</div>{extra}<ol class="steps">{li}</ol><div class="band ans"><b>תשובה:</b> {MI(a)}</div>' + (BAND('tip', tip) if tip else ''))
        return
    NACT[0] += 1
    hh = ''.join(f'<div>{TX(x)}</div>' for x in hints)
    tipb = f'<div class="tstep"><div class="wn"><b>טיפ:</b> {TX(tip)}</div></div>' if tip else ''
    body = (f'<div class="act try big qg" id="{sid}-t"{d} data-vars="{vs}" data-w="{_html.escape(TX(w), quote=True)}"><div class="qr"><div class="card qstem">{stem_html}</div>{extra}'
            f'<div class="trow"><input class="ex" dir="ltr" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="תשובה">{BTN}</div>'
            f'<div class="fbbar">{IDLE}</div><div class="hints">{hh}</div></div>'
            f'<div class="solw"><div class="tsol" hidden>{sol}{tipb}</div><div class="solph">נסו לפתור לבד. נתקעתם? ״רמז״ נותן כיוון, ו״פתרון בשלבים״ מציג את הדרך, שלב אחד בכל לחיצה.</div></div></div>')
    S(sid, title, title, body, kick=KICK(tag), cls='qslide')


def _cellbar(show=True):
    return '<div class="actbar"><button class="abtn chk">בדיקה</button>' + ('<button class="abtn ghost shw">הציגו את התשובות</button>' if show else '') + RST + '</div>'


def FILLT(qid, head, rows, w='', vars_='x', idle='מלאו את התאים ולחצו ״בדיקה״.'):
    """A table of typed answers. rows: (label in math, [answers], hint)."""
    if MODE == 'pdf':
        return TABLE(head, [[f'${lab}$'] + [f'${a}$' for a in ans] for lab, ans, _ in rows])
    NACT[0] += 1
    hd = ''.join(f'<th>{TX(x)}</th>' for x in head)
    b = ''
    for lab, ans, hint in rows:
        tds = ''.join(f'<td><input class="ex" dir="ltr" autocomplete="off" spellcheck="false" data-a="{strip(a)}" data-form="{"exp" if re.search("[a-z]", strip(a)) else "num"}" data-h="{_html.escape(TX(hint), quote=True)}" aria-label="תשובה"></td>' for a in ans)
        b += f'<tr><td class="lab" dir="ltr">{PM(lab)}</td>{tds}</tr>'
    return (f'<div class="act cells" id="{qid}" data-vars="{vars_}" data-w="{_html.escape(TX(w), quote=True)}"><table class="ctab"><tr>{hd}</tr>{b}</table>'
            f'<div class="fbbar">{idle}</div>{_cellbar()}</div>')


def GRIDQ(qid, rowh, colh, cells, final, w='', hint='', vars_='x'):
    """The grid of products of two brackets: the student types each product, then the collected sum."""
    for r, rh in enumerate(rowh):
        for c, ch in enumerate(colh):
            assert same(f'({rh})*({ch})', cells[r][c]), (rh, ch, cells[r][c])
    assert same('+'.join(f'({x})' for row in cells for x in row), final); NCHK[0] += 1
    g = ['g1', 'g2', 'g3', 'g4']
    if MODE == 'pdf':
        t = '<tr><th>×</th>' + ''.join(f'<th>{MI(c)}</th>' for c in colh) + '</tr>' + ''.join(f'<tr><th>{MI(rh)}</th>' + ''.join(f'<td>{MI(x)}</td>' for x in cells[r]) + '</tr>' for r, rh in enumerate(rowh))
        return f'<table class="tbl2 gqp">{t}</table><p><b>אחרי כינוס:</b> {MI(final)}</p>'
    NACT[0] += 1
    inp = lambda a, extra='': f'<input class="ex" dir="ltr" autocomplete="off" spellcheck="false" data-a="{strip(a)}" data-h="{_html.escape(TX(hint), quote=True)}" {extra} aria-label="תשובה">'
    t = '<tr><th class="cn">×</th>' + ''.join(f'<th>{PM(c)}</th>' for c in colh) + '</tr>'
    for r, rh in enumerate(rowh):
        t += f'<tr><th>{PM(rh)}</th>' + ''.join(f'<td class="{g[(r * len(colh) + c) % 4]}">{inp(x, "data-form=" + chr(34) + "exp" + chr(34) + " data-terms=" + chr(34) + "1" + chr(34))}</td>' for c, x in enumerate(cells[r])) + '</tr>'
    fin = inp(final, f'data-form="exp" data-terms="{_nterms(final)}"')
    return (f'<div class="act cells" id="{qid}" data-vars="{vars_}" data-w="{_html.escape(TX(w), quote=True)}"><table class="gq">{t}</table>'
            f'<div class="gsum"><span>סכום כל המכפלות, אחרי כינוס איברים דומים:</span>{fin}</div><div class="fbbar">מלאו בכל תא את המכפלה של ראש השורה בראש העמודה.</div>{_cellbar()}</div>')


def OPS(sid, title, h, intro, states, final, w):
    """Which operation comes first? states: (tokens, kind, result note). A token is text, or (symbol, kind) for a clickable
    operation, or (symbol, kind, True) for the right one. kinds: par, pow, mul, add."""
    out, chainp = [], []
    for toks, kind, res in states:
        hh, plain, ok, i = '', '', None, 0
        for t in toks:
            if isinstance(t, str):
                hh += PM(t).strip() if t.strip() not in ('(', ')') else t.strip(); plain += t
            else:
                sym, k = t[0], t[1]
                if len(t) > 2: ok = i
                if k == 'pow' and sym.isdigit():
                    hh += f'<sup><button class="op" data-i="{i}" data-k="{k}">{sym}</button></sup>'; plain += '^' + sym
                else:
                    hh += f'<button class="op" data-i="{i}" data-k="{k}">{sym}</button>'; plain += {'·': '*', '÷': '/', '−': '-'}.get(sym, sym)
                i += 1
        assert ok is not None, toks
        assert abs(ev(plain) - final) < 1e-9, (plain, ev(plain), final); NCHK[0] += 1
        out.append(dict(h=hh, ok=ok, kind=kind, res=TX(res))); chainp.append(plain)
    fin = PM(str(final) if final >= 0 else f'-{abs(final)}')
    if MODE == 'pdf':
        li = ''.join(f'<li>{MI(p)}: {s["res"]}</li>' for p, s in zip(chainp, out))
        S(sid, title, h, f'<p>{TX(intro)}</p><ol class="steps">{li}</ol><div class="band ans"><b>תשובה:</b> {MI(str(final))}</div>'); return
    NACT[0] += 1
    cfg = _html.escape(json.dumps(dict(states=out, final=fin, w=TX(w)), ensure_ascii=False), quote=True)
    body = (f'<div class="act ops" id="{sid}-w" data-cfg="{cfg}"><div class="tasktxt"><b>המשימה:</b> {TX(intro)}</div><div class="opx"></div>'
            f'<div class="opg"><div><div class="fbbar">לחצו על סימן הפעולה שמבצעים ראשונה.</div><div class="actbar"><button class="abtn ghost shw">הראו לי את השלב הבא</button>{RST}</div></div><ol class="oplog"></ol></div></div>')
    S(sid, title, h, body, kick=KICK('פעילות'))


# ---------------------------------------------------------------- diagrams
def SVM(s, fs):
    """Plain math as SVG tspans: ^n superscript, italic letters, spaces around = and binary + and -."""
    out, i, prev = '', 0, False
    s = s.replace(' ', '')
    while i < len(s):
        c = s[i]
        if c == '^':
            m = re.match(r'-?\w+', s[i + 1:]); a = m.group(0)
            out += f'<tspan dy="{-fs * .4:.1f}" font-size="{fs * .68:.1f}">{a.replace("-", "−")}</tspan><tspan dy="{fs * .4:.1f}" font-size="1">&#8203;</tspan>'; i += 1 + len(a); prev = True
        elif c.isalpha():
            out += f'<tspan class="mi" font-size="{fs * 1.12:.1f}">{c}</tspan>'; i += 1; prev = True
        elif c in '+-':
            sym = '+' if c == '+' else '−'
            out += f' {sym} ' if prev else sym; i += 1; prev = False
        elif c == '=':
            out += ' = '; i += 1; prev = False
        elif c == '*':
            out += '·'; i += 1; prev = False
        else:
            out += _html.escape(c); i += 1; prev = c.isdigit() or c == ')'
    return out


def _t(x, y, s, fs=24, fill='#16213a', w=700, anchor='middle', math=True):
    rtl = ' direction="rtl"' if HEB.search(s) else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" text-anchor="{anchor}" fill="{fill}" font-weight="{w}"{rtl}>{SVM(s, fs) if math and not rtl else _html.escape(s)}</text>'


def _g(n, inner, cls='pop'):
    return f'<g class="st an-{cls}" data-n="{n * 10}">{inner}</g>' if n else f'<g>{inner}</g>'


FILL = ['#ffe3dc', '#dff5f2', '#ece8ff', '#fff0d2']
INK = ['#b8391f', '#087469', '#4f33c9', '#a86703']


def AREA(rl, cl, cells, n0=1, W=520, H=300, sizes=None, total=None, strike=()):
    """Area model. rl, cl: labels of the rows and the columns; cells[r][c]: the product in each cell.
    Step n0 shows the frame and the labels; each cell then appears on its own click. strike: cells whose text is struck (they cancel)."""
    rs, cs = sizes or ([1] * len(rl), [1] * len(cl))
    x0, y0, x1, y1 = 78, 54, W - 14, H - (34 if total else 12)
    xs = [x0 + (x1 - x0) * sum(cs[:i]) / sum(cs) for i in range(len(cs) + 1)]
    ys = [y0 + (y1 - y0) * sum(rs[:i]) / sum(rs) for i in range(len(rs) + 1)]
    p = [_g(n0, f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="10" fill="#fff" stroke="#1b2d55" stroke-width="3"/>'
            + ''.join(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}" stroke="#1b2d55" stroke-width="2" stroke-dasharray="6 5"/>' for x in xs[1:-1])
            + ''.join(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#1b2d55" stroke-width="2" stroke-dasharray="6 5"/>' for y in ys[1:-1])
            + ''.join(_t((xs[i] + xs[i + 1]) / 2, y0 - 16, c, 27, '#1b2d55') for i, c in enumerate(cl))
            + ''.join(_t(x0 - 34, (ys[i] + ys[i + 1]) / 2 + 9, r, 27, '#1b2d55') for i, r in enumerate(rl)), 'fade')]
    k = n0 + 1
    for r in range(len(rl)):
        for c in range(len(cl)):
            j = (r * len(cl) + c) % 4
            cx, cy = (xs[c] + xs[c + 1]) / 2, (ys[r] + ys[r + 1]) / 2
            dead = (r, c) in strike
            g = (f'<rect x="{xs[c] + 4:.1f}" y="{ys[r] + 4:.1f}" width="{xs[c + 1] - xs[c] - 8:.1f}" height="{ys[r + 1] - ys[r] - 8:.1f}" rx="8" fill="{FILL[j]}"/>'
                 + _t(cx, cy + 10, cells[r][c], 28, INK[j]))
            p.append(_g(k, g)); k += 1
    if strike:
        g = ''
        for r, c in strike:
            cx, cy = (xs[c] + xs[c + 1]) / 2, (ys[r] + ys[r + 1]) / 2
            g += f'<line x1="{cx - 44:.1f}" y1="{cy + 16:.1f}" x2="{cx + 44:.1f}" y2="{cy - 14:.1f}" stroke="#e0454f" stroke-width="4" stroke-linecap="round" opacity=".7"/>'
        p.append(_g(k, g, 'fade')); k += 1
    if total:
        p.append(_g(k, _t((x0 + x1) / 2, H - 6, total, 26, '#1b2d55'), 'fade'))
    return f'<div class="diagw"><svg class="diag" dir="ltr" viewBox="0 0 {W} {H}" role="img">{"".join(p)}</svg></div>'


def SUMMARY(sid, title, items, c3=False):
    """What we learned in this part: plain cards."""
    cards = ''.join(f'<div class="lcard"><b>{TX(t)}</b><p>{TX(d)}</p></div>' for t, d in items)
    if MODE == 'pdf':
        S(sid, title, title, '<ul class="pl">' + ''.join(f'<li><b>{TX(t)}:</b> {TX(d)}</li>' for t, d in items) + '</ul>'); return
    S(sid, title, title, f'<div class="learn{" c3" if c3 else ""}">{cards}</div>', kick=KICK('סיכום ביניים'))
