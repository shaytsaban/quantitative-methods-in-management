# Shared helpers for the deck, the summary PDF and the booklet: plain-syntax math, prose markup, a numeric checker.
# Math is written once in a plain syntax (8x^2-6x-5, x^(a+b), {1|6x} for a colour) and is used three ways:
# rendered as HTML (PM), checked numerically in Python (same/ev), and checked in the browser (act.js, same grammar).
import re, html as _h

HEB = re.compile(r'[֐-׿]')


# ---------------------------------------------------------------- rendering
def _grp(s, i, o='(', c=')'):
    """s[i] == o. Return (inner, index after the matching close)."""
    d = 0
    for j in range(i, len(s)):
        if s[j] == o: d += 1
        elif s[j] == c:
            d -= 1
            if d == 0: return s[i + 1:j], j + 1
    raise ValueError('unbalanced: ' + s)


def _top_split(body, sep='|'):
    """Split at the first separator that is not inside braces or brackets."""
    d = 0
    for j, ch in enumerate(body):
        if ch in '{(': d += 1
        elif ch in '})': d -= 1
        elif ch == sep and d == 0: return body[:j], body[j + 1:]
    raise ValueError('no top level separator: ' + body)


def _unfrac(s):
    """{f|a|b} -> ((a)/(b)), recursively, so the checker reads a fraction as a division."""
    out, i = '', 0
    while i < len(s):
        if s.startswith('{f|', i):
            a, i = _grp(s, i, '{', '}')
            n, d = _top_split(a[2:])
            out += f'(({_unfrac(n)})/({_unfrac(d)}))'
        else:
            out += s[i]; i += 1
    return out


def PM(s):
    """Plain math to HTML. ^2, ^(a+b) -> superscript; * -> middle dot; - -> minus; letters italic;
    {1|...} colour 1 to 4, {x|...} struck out, {b|...} boxed; "..." Hebrew words; _ a thin gap."""
    out, i, prev = [], 0, False   # prev: the last thing written was an operand, so a following + or - is binary
    s = s.strip()
    while i < len(s):
        c = s[i]
        if c == ' ':
            i += 1
        elif c == '^':
            if s[i + 1] == '(':
                a, i = _grp(s, i + 1)
            else:
                m = re.match(r'-?(?:\d+|[a-zA-Z])', s[i + 1:]); a = m.group(0); i += 1 + len(a)
            out.append(f'<sup>{PM(a)}</sup>'); prev = True
        elif c == '{' and s[i + 1:i + 3] == 'f|':
            a, i = _grp(s, i, '{', '}')
            num, den = _top_split(a[2:])
            out.append(f'<span class="frac"><span>{PM(num)}</span><span>{PM(den)}</span></span>'); prev = True
        elif c == '{':
            a, i = _grp(s, i, '{', '}')
            k, body = a.split('|', 1)
            inner = PM(body)
            # a coloured piece that starts with a sign after an operand: the sign is binary, so it gets its spaces
            if prev and body.lstrip()[:1] in '+-':
                inner = ' ' + inner[0] + ' ' + inner[1:]
            out.append(f'<span class="k{k}">{inner}</span>'); prev = True
        elif c == '"':
            j = s.index('"', i + 1)
            out.append(f'<span class="mh" dir="rtl">{s[i + 1:j]}</span>'); i = j + 1; prev = True
        elif c in '+-':
            sym = '+' if c == '+' else '−'
            out.append(f' {sym} ' if prev else sym); prev = False; i += 1
        elif c in '=≠≈':
            out.append(f' {c} '); prev = False; i += 1
        elif c in '<>≤≥':
            if s[i + 1:i + 2] == '=': c = {'<': '≤', '>': '≥'}[c]; i += 1
            out.append(f' {_h.escape(c)} '); prev = False; i += 1
        elif c in '*·':
            out.append('·'); prev = False; i += 1
        elif c in '/÷':
            out.append(' ÷ ' if c == '÷' else '/'); prev = False; i += 1
        elif c == '_':
            out.append(' '); i += 1
        elif c.isalpha() and not HEB.match(c):
            out.append(f'<i>{c}</i>'); prev = True; i += 1
        elif c == '(':
            out.append('('); prev = False; i += 1
        elif c == ',':
            out.append(', '); prev = False; i += 1
        else:
            out.append(_h.escape(c)); prev = c.isdigit() or c in ')]?'; i += 1
    return ''.join(out)


def MI(s):
    return f'<span class="m" dir="ltr">{PM(s)}</span>'


def EQ(s, cls=''):
    return f'<div class="eq {cls}" dir="ltr">{PM(s)}</div>'


# a number, with its minus sign when it has one, so the minus stays on the left inside the LTR run
NUM = re.compile(r'(?:(?<![^\s(>])[−-]|(?<![\w.,/]))(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?%?|\d+(?:\.\d+)*%?)')


def TX(s):
    """Prose markup: $math$, [[key|text]] for a glossary term, **bold**, and LTR isolation of every number."""
    s = re.sub(r'\[\[(\w+)\|([^\]]+)\]\]', r'<span class="term" data-t="\1">\2</span>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s, flags=re.S)
    out = []
    for p in re.split(r'(\$[^$]+\$)', s):
        if p.startswith('$') and p.endswith('$') and len(p) > 1:
            out.append(MI(p[1:-1]))
        else:
            out.append(''.join(seg if seg.startswith('<') else NUM.sub(lambda m: f'<span class="n">{m.group(0)}</span>', seg) for seg in re.split(r'(<[^>]+>)', p)))
    return ''.join(out)


# ---------------------------------------------------------------- numeric checker (the same grammar as act.js)
def strip(s):
    """Plain syntax without the display markup."""
    s = _unfrac(s)
    s = re.sub(r'\{\w\|', '', s).replace('}', '').replace('_', '').replace('·', '*').replace('÷', '/').replace('−', '-')
    s = s.replace('<=', '≤').replace('>=', '≥')
    return re.sub(r'"[^"]*"', '', s).replace(' ', '')


class _P:
    def __init__(self, s, env): self.s, self.i, self.env = s, 0, env
    def pk(self): return self.s[self.i] if self.i < len(self.s) else ''
    def expr(self):
        v = self.term()
        while self.pk() in ('+', '-'):
            c = self.pk(); self.i += 1; t = self.term(); v = v + t if c == '+' else v - t
        return v
    def term(self):
        v = self.unary()
        while True:
            c = self.pk()
            if c == '*': self.i += 1; v *= self.unary()
            elif c == '/': self.i += 1; v /= self.unary()
            elif c and (c.isalnum() or c == '('): v *= self.power()
            else: return v
    def unary(self):
        if self.pk() == '-': self.i += 1; return -self.unary()
        if self.pk() == '+': self.i += 1; return self.unary()
        return self.power()
    def power(self):
        b = self.atom()
        if self.pk() == '^': self.i += 1; return b ** self.unary()
        return b
    def atom(self):
        c = self.pk()
        if c == '(':
            self.i += 1; v = self.expr(); assert self.pk() == ')', 'missing ) in ' + self.s; self.i += 1; return v
        m = re.match(r'\d+(?:\.\d+)?', self.s[self.i:])
        if m: self.i += len(m.group(0)); return float(m.group(0))
        if c.isalpha(): self.i += 1; return self.env[c]
        raise ValueError(f'cannot read {self.s!r} at {self.i}')


def ev(s, k=0, at=None):
    s = strip(s)
    env = {ch: (2.718281828459045 if ch == 'e' else 0.6 + ((ord(ch) * 7 + k * 13) % 19) / 9) for ch in 'abcdefghijklmnopqrstuvwxyz'}
    env.update(at or {})
    p = _P(s, env); v = p.expr()
    assert p.i == len(s), f'trailing text in {s!r} at {p.i}'
    return v


def same(a, b):
    return all(abs(ev(a, k) - ev(b, k)) <= 1e-7 * max(1, abs(ev(a, k))) for k in range(4))


def chain(line, ans=None):
    """Every side of A = B = C is the same expression (and equals ans when given)."""
    sides = [x for x in strip(line).split('=') if x]
    for x in sides[1:]:
        assert same(sides[0], x), f'not equal: {sides[0]}  vs  {x}   in {line}'
    if ans is not None:
        assert same(sides[-1], ans), f'does not reach the answer {ans}: {line}'


# ---------------------------------------------------------------- equations and inequalities
REL = re.compile(r'(≤|≥|<|>|=)')
FLIP = {'<': '>', '>': '<', '≤': '≥', '≥': '≤'}


def rel_split(line):
    p = REL.split(strip(line))
    return p[0::2], p[1::2]


def _close(a, b):
    return abs(a - b) <= 1e-9 * max(1, abs(a), abs(b))


def _holds(a, op, b):
    return {'=': _close(a, b), '<': a < b - 1e-12, '>': a > b + 1e-12, '≤': a <= b + 1e-12, '≥': a >= b - 1e-12}[op]


def ineq_parts(ans):
    """'x<-3' -> ('x', '<', -3.0)."""
    sides, ops = rel_split(ans)
    assert len(ops) == 1 and ops[0] != '=' and re.fullmatch(r'[a-z]', sides[0]), ans
    return sides[0], ops[0], ev(sides[1])


def eq_check(line, sol):
    """Every side of an equation line has the same value at the solution (a dict of the unknowns)."""
    sides, ops = rel_split(line)
    assert ops and all(o == '=' for o in ops), 'not an equation: ' + line
    vals = [ev(x, at=sol) for x in sides]
    assert all(_close(vals[0], v) for v in vals[1:]), f'the solution {sol} does not satisfy: {line}  {vals}'


def ineq_check(line, var, op, bound):
    """A step of an inequality keeps the same solution set: equality on the boundary, true inside, false outside."""
    sides, ops = rel_split(line)
    if all(o == '=' for o in ops):
        return eq_check(line, {var: bound})
    assert len(ops) == 1, 'one relation per line: ' + line
    o = ops[0]
    L, R = sides
    assert _close(ev(L, at={var: bound}), ev(R, at={var: bound})), f'boundary {bound} lost in: {line}'
    inside = bound - 1 if op in '<≤' else bound + 1
    outside = bound + 1 if op in '<≤' else bound - 1
    assert _holds(ev(L, at={var: inside}), o, ev(R, at={var: inside})), f'{var}={inside} should satisfy: {line}'
    assert not _holds(ev(L, at={var: outside}), o, ev(R, at={var: outside})), f'{var}={outside} should not satisfy: {line}'
    assert (o in '≤≥') == (op in '≤≥'), f'strict and non strict mixed: {line}'


def step_check(line, target=None, sol=None):
    """One worked line. sol: a dict (equation or system) or (var, op, bound) for an inequality."""
    if isinstance(sol, tuple): return ineq_check(line, *sol)
    if isinstance(sol, dict) and REL.search(strip(line)) and not (('=' in strip(line)) and target is not None and line.startswith('=')):
        return eq_check(line, sol)
    if line.startswith('='): return chain(line[1:], target)
    return chain(line)


def solution_of(expr, a):
    """From a question (an equation, an inequality, or two equations 'e1;e2') and its answer: the solution every
    worked line must keep. The question itself is checked against the answer. None when the question is an expression."""
    if not expr or not REL.search(strip(expr)): return None
    if isinstance(a, dict): sol = {k: ev(v) for k, v in a.items()}
    elif REL.search(strip(a)): sol = ineq_parts(a)
    else:
        vs = sorted(set(re.findall(r'[a-z]', strip(expr))) - {'e'})
        assert len(vs) == 1, ('one unknown expected', expr)
        sol = {vs[0]: ev(a)}
    for part in strip(expr).split(';'):
        step_check(part, None, sol)
    return sol
