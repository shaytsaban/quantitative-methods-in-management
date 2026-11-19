# Meeting 1, in deck order. Run through build_deck.py / build_summary.py.
LMETA = dict(date='', h1=('ריענון באלגברה:', 'מיומנויות אלגבריות'), title='ריענון באלגברה ומיומנויות אלגבריות',
             sub='מחזקה וסדר פעולות, דרך משתנים, כינוס איברים, חוקי חזקות ופתיחת סוגריים, ועד נוסחאות הכפל המקוצר ופירוק לגורמים. כל נושא נבנה מדוגמה במספרים, לאט ובהדרגה.',
             cover='חזקה וסדר פעולות חשבון; משתנה, ביטוי אלגברי והצבה; כינוס איברים דומים; חוקי חזקות; פתיחת סוגריים ופישוט ביטויים; נוסחאות הכפל המקוצר; הוצאת גורם משותף ופירוק לגורמים; תרגילים מסכמים ותרגול עצמי לבית.',
             next_h='משוואות, אחוזים ואי שוויונים', next_t='פתרון משוואה ממעלה ראשונה עם נעלם אחד, מערכת של שתי משוואות עם שני נעלמים, בעיות אחוזים ואי שוויונים. כל אלה נשענים על המיומנויות של המפגש הזה: פתיחת סוגריים, כינוס איברים והצבה.')
TOTAL_PARTS = 8
for _f in ('content_l1a.py', 'content_l1b.py', 'content_l1c.py', 'content_l1d.py'):
    if os.path.exists(os.path.join(H, _f)): exec(R(_f))

# The meeting is two hours long. The class route keeps, in every part, the example, the rule, one worked example and one activity.
# Further drill moves, as it is, to the home practice section at the end of the deck (Shay, 2026-11-19: do not stretch the slides).
DROP = ['s-sign-chk']
HOME = ['s-ops2', 's-like-try2', 's-pw-neg', 's-pw-try', 's-simp-try2', 's-bin-try', 's-sq-try', 'h-a', 's-fac-dif-try', 's-fac-group', 's-fac-e', 'h-b']
_by = {x['id']: x for x in SL}
assert all(k in _by for k in DROP + HOME)
SL[:] = [x for x in SL if x['id'] not in DROP + HOME]
_at = next(i for i, x in enumerate(SL) if x['id'] == 's-home') + 1
for _j, _k in enumerate(HOME):
    _x = _by[_k]
    _x['part'] = 8
    _x['kick'] = 'חלק 8 · תרגול עצמי לבית'
    _x['h'] = 'לבית: ' + re.sub(r'^(תרגול|פעילות): ', '', _x['h'])
    if not _x['title'].startswith('לבית'): _x['title'] = 'לבית: ' + re.sub(r'^(תרגול|פעילות): ', '', _x['title'])
    SL.insert(_at + _j, _x)
