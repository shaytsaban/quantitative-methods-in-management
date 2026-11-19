# Syllabus PDF, from the official course syllabus (course 406010). Run: python3 build_syllabus.py  ->  ../materials/syllabus.pdf
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from pdfkit import *
exec(open(os.path.join(H, 'plan.py'), encoding='utf8').read())
n = lambda s: f'<span class="n">{s}</span>'
CSS = BASE + '''
table{width:100%;font-size:11pt;margin:1.2mm 0 2mm}th{background:var(--navy);color:#fff;text-align:right;padding:1mm 2mm}td{padding:1mm 2mm;border-bottom:.25mm solid var(--line);vertical-align:top}
table.meta td:first-child{font-weight:700;width:34mm;color:var(--navy)}td.c{text-align:center;font-weight:700;width:14mm}tr.hi td{background:#fff0d2}
h3{border-bottom:.5mm solid var(--coral);padding-bottom:.6mm;margin-top:4mm}
ol.en{direction:ltr;text-align:left;padding-left:6mm;padding-right:0;font-size:10.6pt}
'''
rows = ''.join(f'<tr{" class=hi" if i == 1 else ""}><td class="c">{n(i)}</td><td><b>{t}</b></td><td>{d}</td></tr>' for i, t, d, k in PLAN)
body = f'''
<div class="hd"><div class="k">המרכז האקדמי למשפט ולעסקים, רמת גן</div><h1 class="t">שיטות כמותיות בניהול</h1><div class="s"><span class="n">Quantitative Methods in Management</span> · סילבוס</div><div class="cr">{CR1}<br>{CR2}</div></div>
<table class="meta">
<tr><td>מספר הקורס</td><td>{n(406010)}</td></tr>
<tr><td>סוג הקורס</td><td>חובה</td></tr>
<tr><td>היקף</td><td>{n(3)} נקודות זכות</td></tr>
<tr><td>דרישות קדם</td><td>אין</td></tr>
<tr><td>מרצה</td><td>ד״ר שי צבאן</td></tr>
<tr><td>פיתוח הקורס</td><td>ד״ר אסף שריג</td></tr>
<tr><td>פניות למרצה</td><td>במייל: <span class="url">shay.tsaban@gmail.com</span>. יש לציין את שם המוסד ואת שם הקורס.</td></tr>
<tr><td>אתר הקורס</td><td><span class="url">{SITE}</span></td></tr>
</table>
<h3>תיאור הקורס</h3>
<p>הקורס עוסק בניסוח ובפתרון של בעיות החלטה מתחומי ניהול שונים, בלימוד טכניקות לבניית מודלים לקבלת החלטות, ובתרגול של שיטות שונות לפתרון בעיות החלטה.</p>
<h3>מטרת הקורס</h3>
<p>להקנות ידע בנושאים נבחרים מחקר ביצועים, ולהקנות מיומנויות וכלים לפתרון בעיות אופטימיזציה מתחומים שונים, בעיות החלטה חד שלביות ורב שלביות, ובעיות של תכנון פרויקטים.</p>
<h3>תוצרי למידה</h3>
<p>עם סיום הקורס בהצלחה, הסטודנטים יוכלו:</p>
<ul><li>להציג, לפתור ולנתח בעיות בתכנון לינארי.</li><li>לנסח באופן פורמלי בעיות אופטימיזציה מתחומים שונים, ולפתור אותן בעזרת התוסף Solver של Excel.</li><li>לפתור בעיות החלטה סדרתיות בעזרת עצי החלטה.</li><li>לפתור בעיות של תכנון פרויקטים.</li></ul>
<h3>אופן ההוראה</h3>
<p>הרצאות פרונטליות, שבהן נלמד החומר התיאורטי ונעשה תרגול בכיתה, כולל שימוש בתוסף Solver של Excel. לכל מפגש יש באתר הקורס מצגת אינטראקטיבית, סיכום כתוב וחוברת תרגילים עם פתרונות מלאים.</p>
<h3>דרישות הקורס והרכב הציון</h3>
<table><tr><th>מרכיב</th><th>הסבר</th><th>משקל</th></tr>
<tr><td><b>תרגילים</b></td><td>במהלך הסמסטר יינתנו {n(3)} תרגילים, ללא חובת הגשה. לכל תרגיל יפורסם פתרון מלא. התרגילים נועדו לתרגול אישי בלבד.</td><td class="c">{n('0%')}</td></tr>
<tr><td><b>בחינה מסכמת</b></td><td>חומר עזר מותר: מחשבון, ודפי נוסחאות שיצורפו לשאלון הבחינה.</td><td class="c">{n('100%')}</td></tr></table>
<h3>תוכנית המפגשים</h3>
<table><tr><th>מפגש</th><th>הנושא</th><th>פירוט</th></tr>{rows}</table>
<div class="note">ייתכנו שינויים בסדר הנושאים ובקצב ההתקדמות. הריענון באלגברה נפרס על מפגשים {n(1)} ו-{n(2)}, לפי קצב הכיתה. עדכונים מתפרסמים באתר הקורס.</div>
<h3>רשימת קריאה</h3>
<ol><li>קלבנר, חנה ({n(2004)}). חקר ביצועים: מדריך למידה. האוניברסיטה הפתוחה, תל אביב.</li>
<li>ארליך, צ׳, ליברמן, ג׳ והילר, פ׳ ({n(1995)}). מודלים דטרמיניסטיים בחקר ביצועים, כרכים א׳ ו-ב׳. האוניברסיטה הפתוחה, רעננה.</li>
<li>אנטון, הווארד. חשבון דיפרנציאלי ואינטגרלי, חלק א׳. האוניברסיטה העברית.</li>
<li>זאבי, אבי. מבוא לחקר ביצועים, חלק ראשון: תכנות ליניארי ויישומיו. הוצאת דקל, פרסומים אקדמיים.</li></ol>
<ol class="en" start="5"><li>Taha, H. A. (2003). Operations Research: An Introduction. Macmillan.</li><li>Hillier, F. S. (2012). Introduction to Operations Research. Tata McGraw-Hill Education.</li></ol>
<p>שיוך פרקי הקריאה למפגשים: מקור {n(3)} למפגשים {n(1)} עד {n(4)}; מקור {n(5)}, פרק {n(13)}, למפגשים {n(5)} ו-{n(6)}; מקורות {n(1)} ו-{n(2)} למפגשים {n(7)} עד {n(12)}.</p>
'''
to_pdf(f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>שיטות כמותיות בניהול | סילבוס</title><style>{CSS}</style></head><body>{body}</body></html>', os.path.join(H, '..', 'materials', 'syllabus.pdf'))
