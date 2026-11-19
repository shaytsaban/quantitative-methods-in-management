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
    s = re.sub(r'\{\w\|', '', s).replace('}', '').replace('_', '').replace('·', '*').replace('÷', '/').replace('−', '-')
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


def ev(s, k=0):
    s = strip(s)
    env = {ch: (2.718281828459045 if ch == 'e' else 0.6 + ((ord(ch) * 7 + k * 13) % 19) / 9) for ch in 'abcdefghijklmnopqrstuvwxyz'}
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
