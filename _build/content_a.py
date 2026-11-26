# Lesson content helpers, shared by the deck and the summary. Executed with MODE = 'deck' or 'pdf'.
# The lesson itself is in content_l<N>*.py. Every worked line is checked numerically while the deck is built (qlib.chain).
from qlib import *
from qlib import _holds, _close
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
MAN = []           # manifest for the tests: what every activity must accept and reject, written independently of the page


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
    MAN.append(dict(kind='mc', id=qid, right=_html.unescape(re.sub('<[^>]+>', '', TX(opts[a]))), n=len(opts)))
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
    MAN.append(dict(kind='sorter', id=aid + '-w', rows=[_html.unescape(re.sub('<[^>]+>', '', TX(options[b]))) for _, b, _ in rows]))
    NACT[0] += 1
    r = ''
    for a, b, c in rows:
        bs = ''.join(f'<button class="so" data-i="{i}">{TX(o)}</button>' for i, o in enumerate(options))
        r += f'<tr class="srow" data-a="{b}" data-w="{_html.escape(TX(c), quote=True)}"><td>{TX(a)}</td><td>{bs}</td></tr>'
    body = (f'<div class="act sorter" id="{aid}-w"><div class="tasktxt"><b>המשימה:</b> {TX(task)}</div><table class="stbl">{r}</table>'
            f'<div class="fbbar">בחרו תשובה בכל שורה.</div><div class="actbar">{RST}<span class="score">0 / {len(rows)}</span></div></div>')
    S(aid, title, h, body, kick=KICK('פעילות'))


# ---------------------------------------------------------------- worked solutions and typed answers
def _line(x, target, sol=None):
    """One stage: (math, note). '~...' is not checked. With sol (an equation, a system or an inequality), every line must keep
    the solution. Without it, '=...' must equal the target and anything else is checked side against side."""
    m, note = x
    if m.startswith('~'):
        m = m[1:]
    elif ';' in m:
        for part in m.split(';'):
            step_check(part, target, sol); NCHK[0] += 1
    else:
        step_check(m, target, sol); NCHK[0] += 1
    return m, note


def _MI(m):
    """Inline (summary PDF): a system 'e1;e2' is stacked; anything else is a math run."""
    if ';' in m:
        return '<span class="sysq" dir="ltr">' + ''.join(f'<span class="sysl">{PM(p)}</span>' for p in m.split(';')) + '</span>'
    return MI(m)


def _EQ(m):
    """One worked line; two equations 'e1;e2' are shown as a system, one under the other."""
    if ';' in m:
        return '<div class="eq sysq" dir="ltr">' + ''.join(f'<span class="sysl">{PM(p)}</span>' for p in m.split(';')) + '</div>'
    return EQ(m)


def _sol_of(expr, a):
    """The solution that every line must keep, read from the question and its answer; the question itself is checked too."""
    sol = solution_of(expr, a)
    if sol is not None: NCHK[0] += 1
    return sol


def _nterms(a):
    s, d, n = strip(a), 0, 1
    for i, c in enumerate(s):
        if c == '(': d += 1
        elif c == ')': d -= 1
        elif c in '+-' and d == 0 and i and s[i - 1] not in '^*/(': n += 1
    return n


def _c2(size, n):
    """Long solutions (lesson 2 on): two columns of steps, the right one first, so a calculation never leaves the slide."""
    return f' style="grid-template-rows:repeat({(n + 1) // 2},auto)"' if 'c2' in size.split() else ''


def WORK(sid, tag, title, stem, steps, expr=None, ans=None, tip=None, extra='', size='', layout='', kick=None, sol=None, show=None):
    """A worked example: the full question beside its solution, one stage per click, the note above each equation.
    expr: the expression of the question, shown large in the question card. ans: the target of every '=' line."""
    target = ans if ans is not None else expr
    if sol is None and expr and ans is not None: sol = _sol_of(expr, ans)
    rows = [_line(x[:2], target, sol) for x in steps]
    ext = [x[2] if len(x) > 2 else '' for x in steps]   # optional html under a line (labels)
    stem_html = ''.join(f'<p>{TX(x)}</p>' for x in stem) + (show if show is not None else (EQ(expr) if expr else ''))
    if MODE == 'pdf':
        li = ''.join(f'<li>{TX(note)} {_MI(m) if m else ""}</li>' for m, note in rows)
        S(sid, title, title, f'<div class="qstem">{stem_html}</div>{extra}<ol class="steps">{li}</ol>' + (BAND('tip', tip) if tip else ''))
        return
    r = ''
    for i, (m, note) in enumerate(rows):
        fin = ' fin' if i == len(rows) - 1 else ''
        r += ST(i + 1, f'<div class="wn"><b>{i + 1}</b><span>{TX(note)}</span></div>{_EQ(m) if m else ""}{ext[i]}', cls='wkr' + fin)
    end = BAND('tip', tip, len(rows) + 1) if tip else ''
    body = f'<div class="qg {layout}"><div class="qr"><div class="card qstem">{stem_html}</div>{extra}</div><div class="solw"><div class="wk {size}"{_c2(size, len(rows))}>{r}</div>{end}</div></div>'
    S(sid, title, title, body, kick=kick or KICK(tag), cls='qslide')


def _form(a, form):
    if form: return form
    if REL.search(strip(a)): return 'ineq'
    return 'exp' if re.search(r'[a-z]', strip(a)) else 'num'


def _trydata(a, form, terms, out, nb, traps):
    letters = sorted(set(re.findall(r'[a-z]', strip(a))))
    form = _form(a, form)
    d = f' data-a="{_html.escape(strip(a), quote=True)}" data-form="{form}"'
    if form == 'exp': d += f' data-terms="{terms or _nterms(a)}"'
    if out: d += f' data-out="{strip(out)}"'
    if nb: d += f' data-nb="{nb}"'
    if traps:
        for x, _ in traps:
            if form != 'ineq': ev(x)
        d += ' data-traps="' + _html.escape(json.dumps([[strip(x), TX(m)] for x, m in traps], ensure_ascii=False), quote=True) + '"'
    return d, letters


def _trysol(a, steps, sol=None):
    rows = [_line(x, a, sol) for x in steps]
    h = ''.join(f'<div class="tstep{" fin" if i == len(rows) - 1 else ""}"><div class="wn">{TX(note)}</div>{_EQ(m) if m else ""}</div>' for i, (m, note) in enumerate(rows))
    return rows, h


def _kp(text, a):
    """Extra keypad keys: a fraction bar when the question has fractions, relation signs for an inequality."""
    k = ''
    if '{f|' in text or '/' in strip(a): k += '/'
    if REL.search(strip(a)) and not isinstance(a, dict): k += '<>≤≥'
    return k


BTN = '<button class="abtn chk">בדיקה</button><button class="abtn ghost hintb">רמז</button><button class="abtn ghost solb">פתרון בשלבים</button>'
IDLE = 'הקלידו תשובה ולחצו ״בדיקה״. חזקה כותבים עם הסימן <span class="n">^</span>, למשל <span class="n">x^2</span>.'
IDLES = {'ineq': 'הקלידו אי שוויון, למשל <span class="n">x&lt;5</span>. קטן או שווה: <span class="n">&lt;=</span>. גדול או שווה: <span class="n">&gt;=</span>.',
         'eq': 'הקלידו את הפתרון: מספר, או בצורה <span class="n">x=4</span>. שבר כותבים עם <span class="n">/</span>, למשל <span class="n">15/7</span>.',
         'num': 'הקלידו מספר ולחצו ״בדיקה״.'}


def _idle(form, expr):
    if form == 'ineq': return IDLES['ineq']
    if form == 'num': return IDLES['eq'] if expr and REL.search(strip(expr)) else IDLES['num']
    return IDLE


def TRY(qid, q, a, hints=(), steps=(), form=None, terms=None, out=None, nb=None, traps=(), w='', num=None, vars_=None):
    """A compact question with a typed answer. The answer is checked as an expression, not as text."""
    d, letters = _trydata(a, form, terms, out, nb, traps)
    _qe = re.findall(r'\$([^$]*)\$', q)
    rows, sol = _trysol(a, steps, _sol_of(_qe[-1] if _qe else '', a))
    vs = vars_ or ''.join(sorted(set(letters) | set(re.findall(r'[a-z]', strip(' '.join(re.findall(r'\$([^$]*)\$', q))))))) or 'x'
    lab = f'<span class="tn">{num}</span>' if num else ''
    _qe = re.findall(r'\$([^$]*)\$', q)
    MAN.append(dict(kind='try', id=qid, a=strip(a), form=_form(a, form), expr=(strip(_qe[-1]) if _qe else ''), traps=[[strip(x), TX(m)] for x, m in traps], nsteps=len(steps), nhints=len(hints), out=strip(out) if out else ''))
    if MODE == 'pdf':
        li = ' '.join(f'{TX(note)} {_MI(m)}.' for m, note in rows)
        return f'<div class="tryp"><p><b>{num + ". " if num else ""}</b>{TX(q)}</p><p class="tsl"><b>פתרון:</b> {li}</p><p><b>תשובה:</b> {MI(a)}</p></div>'
    NACT[0] += 1
    hh = ''.join(f'<div>{TX(x)}</div>' for x in hints)
    return (f'<div class="act try" id="{qid}"{d} data-vars="{vs}" data-kp="{_kp(q, a)}" data-w="{_html.escape(TX(w), quote=True)}"><div class="tq">{lab}<span>{TX(q)}</span></div>'
            f'<div class="trow"><input class="ex" dir="ltr" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="תשובה">{BTN}</div>'
            f'<div class="fbbar">{_idle(_form(a, form), _qe[-1] if _qe else "")}</div><div class="hints">{hh}</div><div class="tsol" hidden>{sol}</div></div>')


def RECIPE(items):
    """The order of work for this kind of exercise, as numbered chips: always on screen beside the practice."""
    if MODE == 'pdf':
        return '<p class="recp"><b>דרך הפתרון:</b> ' + '; '.join(f'({i}) {TX(t)}' for i, t in enumerate(items, 1)) + '.</p>'
    return '<div class="recipe"><b>דרך הפתרון</b>' + ''.join(f'<span><i>{i}</i><em>{TX(t)}</em></span>' for i, t in enumerate(items, 1)) + '</div>'


def TRYS(sid, title, h, items, intro=None, cols=2, kick='נסו בעצמכם', after='', recipe=None):
    pre = (RECIPE(recipe) if recipe else '') + (f'<p class="lead">{TX(intro)}</p>' if intro else '')
    if MODE == 'pdf':
        S(sid, title, h, pre + ''.join(items) + after); return
    S(sid, title, h, pre + f'<div class="trys c{cols}">' + ''.join(items) + '</div>' + after, kick=KICK(kick))


def TRYBIG(sid, tag, title, stem, a, hints=(), steps=(), expr=None, form=None, terms=None, out=None, nb=None, traps=(), w='', tip=None, extra='', vars_=None, show=None):
    """One exercise on its own slide: the full question and the answer box on the right, the staged solution on the left."""
    d, letters = _trydata(a, form, terms, out, nb, traps)
    rows, sol = _trysol(a, steps, _sol_of(expr, a))
    stem_html = ''.join(f'<p>{TX(x)}</p>' for x in stem) + (show if show is not None else (EQ(expr) if expr else ''))
    vs = vars_ or ''.join(sorted(set(letters) | set(re.findall(r'[a-z]', strip(expr or ''))))) or 'x'
    MAN.append(dict(kind='try', id=sid + '-t', a=strip(a), form=_form(a, form), expr=strip(expr or ''), traps=[[strip(x), TX(m)] for x, m in traps], nsteps=len(steps) + (1 if tip else 0), nhints=len(hints), out=strip(out) if out else ''))
    if MODE == 'pdf':
        li = ''.join(f'<li>{TX(note)} {_MI(m)}</li>' for m, note in rows)
        S(sid, title, title, f'<div class="qstem">{stem_html}</div>{extra}<ol class="steps">{li}</ol><div class="band ans"><b>תשובה:</b> {MI(a)}</div>' + (BAND('tip', tip) if tip else ''))
        return
    NACT[0] += 1
    hh = ''.join(f'<div>{TX(x)}</div>' for x in hints)
    tipb = f'<div class="tstep"><div class="wn"><b>טיפ:</b> {TX(tip)}</div></div>' if tip else ''
    body = (f'<div class="act try big qg" id="{sid}-t"{d} data-vars="{vs}" data-kp="{_kp(" ".join(stem) + (expr or ""), a)}" data-w="{_html.escape(TX(w), quote=True)}"><div class="qr"><div class="card qstem">{stem_html}</div>{extra}'
            f'<div class="trow"><input class="ex" dir="ltr" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="תשובה">{BTN}</div>'
            f'<div class="fbbar">{_idle(_form(a, form), expr)}</div><div class="hints">{hh}</div></div>'
            f'<div class="solw"><div class="tsol" hidden>{sol}{tipb}</div><div class="solph">נסו לפתור לבד. נתקעתם? ״רמז״ נותן כיוון, ו״פתרון בשלבים״ מציג את הדרך, שלב אחד בכל לחיצה.</div></div></div>')
    S(sid, title, title, body, kick=KICK(tag), cls='qslide')


def _cellbar(show=True):
    return '<div class="actbar"><button class="abtn chk">בדיקה</button>' + ('<button class="abtn ghost shw">הציגו את התשובות</button>' if show else '') + RST + '</div>'


def FILLT(qid, head, rows, w='', vars_='x', idle='מלאו את התאים ולחצו ״בדיקה״.'):
    """A table of typed answers. rows: (label in math, [answers], hint)."""
    if MODE == 'pdf':
        return TABLE(head, [[f'${lab}$'] + [f'${a}$' for a in ans] for lab, ans, _ in rows])
    MAN.append(dict(kind='cells', id=qid, ans=[strip(x) for _, an, _ in rows for x in an]))
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
    MAN.append(dict(kind='cells', id=qid, ans=[strip(x) for row in cells for x in row] + [strip(final)]))
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
    MAN.append(dict(kind='ops', id=sid + '-w', kinds=[k for _, k, _ in states], final=str(final)))
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


def VEQ(s, cls=''):
    """A displayed line, checked: an identity (every side equal) or a chain of true numeric relations."""
    sides, ops = rel_split(s)
    if all(o == '=' for o in ops):
        chain(s)
    else:
        vals = [ev(x) for x in sides]
        assert all(_holds(vals[k], o, vals[k + 1]) for k, o in enumerate(ops)), 'false relation: ' + s
    NCHK[0] += 1
    return EQ(s, cls)


def SUMMARY(sid, title, items, c3=False):
    """What we learned in this part: plain cards."""
    cards = ''.join(f'<div class="lcard"><b>{TX(t)}</b><p>{TX(d)}</p></div>' for t, d in items)
    if MODE == 'pdf':
        S(sid, title, title, '<ul class="pl">' + ''.join(f'<li><b>{TX(t)}:</b> {TX(d)}</li>' for t, d in items) + '</ul>'); return
    S(sid, title, title, f'<div class="learn{" c3" if c3 else ""}">{cards}</div>', kick=KICK('סיכום ביניים'))


def TRYXY(qid, q, ans, hints=(), steps=(), w='', num=None, expr=None, show=True):
    """A system of two equations: one box for each unknown. ans: {'x': '1', 'y': '4'}. expr: the two equations, 'eq1;eq2'."""
    sol = _sol_of(expr, ans) if expr else None
    rows, solh = _trysol('', steps, sol)
    MAN.append(dict(kind='try2', id=qid, a={k: strip(v) for k, v in ans.items()}, nsteps=len(steps), nhints=len(hints)))
    show = ''.join(f'<span class="sysl">{MI(e)}</span>' for e in (expr or '').split(';')) if expr and show else ''
    if MODE == 'pdf':
        li = ' '.join(f'{TX(note)} {_MI(m)}.' for m, note in rows if m or note)
        return f'<div class="tryp"><p><b>{num + ". " if num else ""}</b>{TX(q)}</p>{f"<div class=sys>{show}</div>" if show else ""}<p class="tsl"><b>פתרון:</b> {li}</p><p><b>תשובה:</b> ' + MI('(' + ', '.join(ans) + ') = (' + ', '.join(ans.values()) + ')') + '</p></div>'
    NACT[0] += 1
    hh = ''.join(f'<div>{TX(x)}</div>' for x in hints)
    lab = f'<span class="tn">{num}</span>' if num else ''
    boxes = ''.join(f'<label class="xin" dir="ltr"><i>{k}</i> =<input class="ex" dir="ltr" autocomplete="off" autocapitalize="off" spellcheck="false" data-a="{strip(v)}" data-form="num" data-v="{k}" aria-label="{k}"></label>' for k, v in ans.items())
    return (f'<div class="act try xy" id="{qid}" data-vars="{"".join(ans)}" data-kp="/" data-w="{_html.escape(TX(w), quote=True)}"><div class="tq">{lab}<span>{TX(q)}</span></div>'
            + (f'<div class="sys">{show}</div>' if show else '') +
            f'<div class="trow"><span class="xyb" dir="ltr">{boxes}</span>{BTN}</div>'
            f'<div class="fbbar">הקלידו את שני הערכים ולחצו ״בדיקה״.</div><div class="hints">{hh}</div><div class="tsol" hidden>{solh}</div></div>')


# ---------------------------------------------------------------- lesson 2 diagrams (no Hebrew inside SVG: only numbers and math)
def BAL(left, right, op=None, W=520, H=176, n=0, tilt=0):
    """A balance scale: the two sides of an equation on two pans. op: the operation done to both pans (math), shown under each pan."""
    cx, by = W / 2, 92
    dy = tilt * 14
    g = (f'<polygon points="{cx},{by + 4} {cx - 26},{by + 62} {cx + 26},{by + 62}" fill="#1b2d55"/>'
         f'<line x1="{cx - 190}" y1="{by + dy}" x2="{cx + 190}" y2="{by - dy}" stroke="#1b2d55" stroke-width="6" stroke-linecap="round"/>'
         f'<circle cx="{cx}" cy="{by}" r="8" fill="#ff6a4d"/>')
    for sx, txt, yy in ((cx - 170, left, by + dy), (cx + 170, right, by - dy)):
        g += (f'<line x1="{sx - 60}" y1="{yy}" x2="{sx - 70}" y2="{yy + 34}" stroke="#8a93aa" stroke-width="2"/><line x1="{sx + 60}" y1="{yy}" x2="{sx + 70}" y2="{yy + 34}" stroke="#8a93aa" stroke-width="2"/>'
              f'<path d="M{sx - 82} {yy + 34} Q{sx} {yy + 62} {sx + 82} {yy + 34} Z" fill="#fff0d2" stroke="#a86703" stroke-width="2.5"/>'
              + _t(sx, yy - 12, txt, 26, '#1b2d55'))
        if op: g += _t(sx, yy + 86, op, 22, '#c4421f')
    svg = f'<svg class="diag bal" dir="ltr" viewBox="0 0 {W} {H + (30 if op else 0)}" role="img">{g}</svg>'
    return ST(n, svg, cls='diagw pop') if n else f'<div class="diagw">{svg}</div>'


def NUMLINE(lo, hi, bound, op, n0=0, lab=None, W=560, H=110, step=1):
    """A number line from lo to hi, the boundary as an open (strict) or filled circle, and the solution ray."""
    x0, x1, y = 30, W - 30, 62
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    g = f'<line x1="{x0 - 16}" y1="{y}" x2="{x1 + 16}" y2="{y}" stroke="#1b2d55" stroke-width="2.5"/>'
    v = lo
    while v <= hi + 1e-9:
        g += f'<line x1="{X(v):.1f}" y1="{y - 7}" x2="{X(v):.1f}" y2="{y + 7}" stroke="#1b2d55" stroke-width="2"/>' + _t(X(v), y + 32, str(int(v)) if v == int(v) else str(v), 19, '#5d6a86', 600)
        v += step
    bx = X(bound)
    right = op in '>≥'
    end = x1 + 16 if right else x0 - 16
    ray = (f'<line x1="{bx:.1f}" y1="{y}" x2="{end:.1f}" y2="{y}" stroke="#ff6a4d" stroke-width="9" stroke-linecap="round" opacity=".85"/>'
           f'<polygon points="{end + (12 if right else -12):.1f},{y} {end:.1f},{y - 11} {end:.1f},{y + 11}" fill="#ff6a4d"/>')
    dot = f'<circle cx="{bx:.1f}" cy="{y}" r="10" fill="{"#c4421f" if op in "≤≥" else "#fff"}" stroke="#c4421f" stroke-width="4"/>'
    lab_t = _t(bx, y - 22, lab, 22, '#c4421f') if lab else ''
    parts = [_g(n0, g, 'fade'), _g(n0 + 1 if n0 else 0, dot + lab_t), _g(n0 + 2 if n0 else 0, ray, 'draw')]
    return f'<div class="diagw"><svg class="diag nl" dir="ltr" viewBox="0 0 {W} {H}" role="img">{"".join(parts)}</svg></div>'


def GRID100(k, n0=0, col='#ff6a4d', W=260):
    """A square of 100 small squares, k of them coloured: k percent."""
    c, g = W / 10, ''
    for i in range(100):
        r, q = divmod(i, 10)
        g += f'<rect x="{q * c + 1:.1f}" y="{r * c + 1:.1f}" width="{c - 2:.1f}" height="{c - 2:.1f}" rx="3" fill="#e9e4d8"/>'
    hi = ''.join(f'<rect x="{(i % 10) * c + 1:.1f}" y="{(i // 10) * c + 1:.1f}" width="{c - 2:.1f}" height="{c - 2:.1f}" rx="3" fill="{col}"/>' for i in range(k))
    return f'<svg class="diag g100" dir="ltr" viewBox="0 0 {W} {W}" role="img">{g}{_g(n0, hi, "fade")}</svg>'


def PBAR(rows, n0=1, W=560, unit=None):
    """Horizontal bars, one per click. rows: (label, [(value, colour, text)]). The label and texts are numbers or math only."""
    mx = max(sum(v for v, _, _ in segs) for _, segs in rows)
    bw, x0, h, g = W - 120, 104, 40, ''
    for i, (lab, segs) in enumerate(rows):
        y = 10 + i * 58
        x, inner = x0, _t(x0 - 10, y + 28, lab, 22, '#1b2d55', 700, 'end')
        for v, colr, txt in segs:
            w = v / mx * bw
            inner += f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="6" fill="{colr}"/>' + (_t(x + w / 2, y + 27, txt, 19, '#16213a', 700) if txt else '')
            x += w
        g += _g(n0 + i, inner, 'fade')
    return f'<div class="diagw"><svg class="diag pbar" dir="ltr" viewBox="0 0 {W} {20 + len(rows) * 58}" role="img">{g}</svg></div>'


# ---------------------------------------------------------------- find the mistake
def _sol_wrong(sol, wrong):
    if wrong is None: return None, None
    if isinstance(sol, tuple): return ineq_parts(wrong), None
    if isinstance(sol, dict):
        return ({k: ev(v) for k, v in wrong.items()} if isinstance(wrong, dict) else {next(iter(sol)): ev(wrong)}), None
    return None, wrong


def ERR(sid, title, h, q, lines, bad, why, fix, expr=None, ans=None, wrong=None, show=None, kick=None):
    """A solution written by a student, with one wrong line. The student clicks the first wrong line.
    lines: (math, note); the note says why a right line is right. Lines before `bad` are checked like a worked solution,
    the line `bad` must FAIL the check, and the lines from it on must agree with the student's wrong answer `wrong`.
    fix: the right continuation from line `bad`, (math, note), checked. Without expr, '=' lines are checked against ans."""
    sol = _sol_of(expr, ans) if expr else None
    target = ans
    labels = [x[2] if len(x) > 2 else '' for x in lines]
    lines = [(x[0], x[1]) for x in lines]
    for x in lines[:bad]: _line(x, target, sol)
    m = lines[bad][0]
    try:
        step_check(m, target, sol); ok = True
    except AssertionError:
        ok = False
    assert not ok, ('the wrong line passes the check', sid, m)
    NCHK[0] += 1
    sw, tw = _sol_wrong(sol, wrong)
    for x in lines[bad:]:
        if not x[0].startswith('~'): step_check(x[0], tw, sw); NCHK[0] += 1
    fixr = [_line(x, target, sol) for x in fix]
    if MODE == 'pdf': q = q.replace('לחצו על השורה הראשונה', 'מצאו את השורה הראשונה')
    stem = f'<p>{TX(q)}</p>' + (show if show is not None else (EQ(expr) if expr else ''))
    fixh = ''.join(f'<div class="efr"><span>{TX(n)}</span>{EQ(mm) if mm else ""}</div>' for mm, n in fixr)
    MAN.append(dict(kind='err', id=sid + '-w', bad=bad, n=len(lines)))
    if MODE == 'pdf':
        li = ''.join(f'<li{" class=ebad" if i == bad else ""}>{TX(labels[i])} {_MI(mm.lstrip("~")) if mm.strip("~") else ""}' + (' <b>כאן הטעות.</b>' if i == bad else '') + '</li>' for i, (mm, n) in enumerate(lines))
        S(sid, title, h, f'<div class="qstem">{stem}</div><ol class="steps">{li}</ol>' + BAND('trap', why) + f'<div class="efix">{fixh}</div>')
        return
    NACT[0] += 1
    ls = ''
    for i, (mm, n) in enumerate(lines):
        body = EQ(mm.lstrip('~')) if mm.strip('~') else ''
        lab = TX(labels[i]) if labels[i] else (TX(n) if not body else '')
        ls += f'<button class="el" data-i="{i}" data-w="{_html.escape(TX(n), quote=True)}"><b class="eln">{i + 1}</b>' + (f'<span class="eln2">{lab}</span>' if lab else '') + f'{body}</button>'
    body = (f'<div class="act err qg" id="{sid}-w" data-bad="{bad}" data-w="{_html.escape(TX(why), quote=True)}"><div class="qr"><div class="card qstem">{stem}</div>'
            f'<div class="fbbar">לחצו על השורה הראשונה שבה נפלה הטעות. כל שורה שתבחרו תקבל הסבר.</div>'
            f'<div class="actbar">{RST}</div></div>'
            f'<div class="solw"><div class="elines">{ls}</div><div class="efix" hidden><b class="ct">הפתרון הנכון, מהשורה שתוקנה</b>{fixh}</div></div></div>')
    S(sid, title, h, body, kick=kick or KICK('מצאו את הטעות'), cls='qslide')
