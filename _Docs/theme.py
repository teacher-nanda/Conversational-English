"""Editorial theme system for Conversational English lessons.
apply_theme(html, theme) post-processes an existing lesson HTML (idempotent: strips an earlier theme)."""
import re

# ---------- line icons (24x24, stroke only) ----------
def _i(p): return ('<svg class="ico" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" '
                   'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+p+'</svg>')
ICONS = {
 'leadin':   _i('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r=".6"/>'),
 'listening':_i('<path d="M4 15v-3a8 8 0 0 1 16 0v3"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/>'),
 'speaking': _i('<path d="M4 5h16v11H11l-5 4v-4H4z"/><path d="M8 9.5h8M8 12.5h5"/>'),
 'grammar':  _i('<path d="M4 20l1-4L16 5l3 3L8 19z"/><path d="M14 7l3 3"/>'),
 'pron':     _i('<path d="M4 10v4M8 7v10M12 4v16M16 8v8M20 10.5v3"/>'),
 'reading':  _i('<path d="M12 6c-2-1.5-5-2-8-1.5V19c3-.5 6 0 8 1.5 2-1.5 5-2 8-1.5V4.5C17 4 14 4.5 12 6z"/><path d="M12 6v14.5"/>'),
 'vocab':    _i('<path d="M3 12l9-9h8v8l-9 9z"/><circle cx="15.5" cy="8.5" r="1.2"/>'),
 'bridge':   _i('<path d="M2 17h20"/><path d="M4 17c0-5 3-8 8-8s8 3 8 8"/><path d="M8 17v-6M12 17V9M16 17v-6"/>'),
 'review':   _i('<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>'),
 'hw':       _i('<rect x="5" y="3.5" width="14" height="17" rx="1.5"/><path d="M8.5 8h7M8.5 12h7M8.5 16h4"/>'),
 'video':    _i('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M10.5 9l4.5 3-4.5 3z"/>'),
 'home':     _i('<path d="M4 11l8-7 8 7"/><path d="M6 10v10h12V10"/>'),
 'compass':  _i('<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>'),
}

# ---------- cover scenes (SVG band, 1600x400, paints with theme colors) ----------
def scene(kind, t):
    a,b,c,d,sun = t['scene']  # far, mid, near, foreground, sun/moon
    W,H = 1600,400
    out=[f'<svg class="cv-art" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice" aria-hidden="true">']
    out.append(f'<circle cx="1180" cy="200" r="64" fill="{sun}" opacity=".9"/>')
    def hills(col,y,amp,seed,op=1):
        import math
        pts=[]
        for x in range(0,W+81,80):
            yy=y+amp*math.sin(x/230+seed)+amp*.5*math.sin(x/97+seed*2)
            pts.append(f'{x},{yy:.0f}')
        return f'<polygon points="0,{H} '+' '.join(pts)+f' {W},{H}" fill="{col}" opacity="{op}"/>'
    if kind=='forest':
        out.append(hills(a,230,28,1))
        out.append(hills(b,285,26,2.4))
        # tall trees
        import random; r=random.Random(7)
        for x in range(40,W,95):
            h=r.randint(120,210); w=r.randint(22,34); y0=330+r.randint(-10,10)
            out.append(f'<path d="M{x} {y0} L{x-w} {y0-h*.35:.0f} L{x-w*.6:.0f} {y0-h*.35:.0f} L{x-w*.85:.0f} {y0-h*.65:.0f} L{x-w*.35:.0f} {y0-h*.65:.0f} L{x} {y0-h} L{x+w*.35:.0f} {y0-h*.65:.0f} L{x+w*.85:.0f} {y0-h*.65:.0f} L{x+w*.6:.0f} {y0-h*.35:.0f} L{x+w} {y0-h*.35:.0f} Z" fill="{c}"/>')
        out.append(hills(d,350,14,5))
    elif kind=='jungle':
        out.append(hills(a,240,26,1))
        out.append(hills(b,290,22,2.1))
        import random; r=random.Random(11)
        for x in range(60,W,170):
            tx=x+r.randint(-30,30); top=r.randint(110,170)
            out.append(f'<path d="M{tx} 360 C{tx-6} 280 {tx+8} 220 {tx} {top}" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>')
            for k,(dx,dy) in enumerate([(-80,34),(-55,-6),(55,-6),(80,34),(0,-30)]):
                out.append(f'<path d="M{tx} {top} Q{tx+dx*.5:.0f} {top+dy-40} {tx+dx} {top+dy+10}" stroke="{c}" stroke-width="9" fill="none" stroke-linecap="round"/>')
        out.append(hills(d,345,16,4))
    elif kind=='city':
        out.append(hills(a,300,8,1))
        import random; r=random.Random(5)
        x=0
        while x<W:
            w=r.randint(50,110); h=r.randint(90,250); col=r.choice([b,c])
            out.append(f'<rect x="{x}" y="{H-60-h}" width="{w}" height="{h+60}" fill="{col}"/>')
            for wy in range(H-60-h+16,H-70,26):
                for wx in range(x+10,x+w-14,22):
                    if r.random()<.35: out.append(f'<rect x="{wx}" y="{wy}" width="8" height="12" fill="{sun}" opacity=".55"/>')
            x+=w+r.randint(0,10)
        out.append(f'<rect x="0" y="{H-40}" width="{W}" height="40" fill="{d}"/>')
    elif kind=='sea':
        out.append(hills(a,260,14,1)); out.append(hills(b,300,12,3)); out.append(hills(c,335,10,5)); out.append(hills(d,370,8,7))
    else:  # 'hills' / mountains
        import random; r=random.Random(3)
        for col,y,amp in ((a,200,60),(b,260,50)):
            pts=[]; x=0
            while x<=W:
                pts.append(f'{x},{y-r.randint(0,amp)}'); x+=r.randint(90,170)
            out.append(f'<polygon points="0,{H} '+' '.join(pts)+f' {W},{y} {W},{H}" fill="{col}"/>')
        out.append(hills(c,320,18,2)); out.append(hills(d,365,10,6))
    out.append('</svg>'); return ''.join(out)

THEMES = {
 'survival': dict(
    label='Unit 5 · Lesson A', scene_kind='jungle', icon='compass',
    paper='#FBF8F1', ink='#1F2A24', muted='#5C665E', accent='#B4562B', accent2='#2F5D4A', soft='#EFE6D2', rule='#D9CFB8',
    cover_bg='#F3ECDB', scene=('#BFCDB5','#8FA98B','#4F7360','#2B4A3C','#E3B766'),
    banner={'leadin':'#2F5D4A','listening':'#2F5D4A','speaking':'#2F5D4A','grammar':'#2F5D4A','pron':'#2F5D4A',
            'reading':'#2F5D4A','vocab':'#2F5D4A','bridge':'#2F5D4A','review':'#2F5D4A','hw':'#2F5D4A','video':'#2F5D4A'}),
}

def css(t):
    return f'''
/* ===== EDITORIAL THEME ({t['name']}) ===== */
:root {{ --navy:{t['ink']}; --coral:{t['accent']}; --sky:{t['soft']}; --mint:{t['accent2']}; --lemon:{t['soft']}; --lilac:{t['rule']}; --paper:{t['paper']}; --mist:{t['soft']};
  --serif:'Fraunces','Playfair Display',Georgia,'Times New Roman',serif; }}
body {{ background:{t['paper']} !important; color:{t['ink']} !important; }}
.slide {{ background:{t['paper']}; }}
h2 {{ font-family:var(--serif) !important; font-weight:600 !important; letter-spacing:-.01em; color:{t['ink']} !important; }}
h2::after {{ width:56px !important; height:2px !important; border-radius:0 !important; margin-top:10px !important; background:{t['accent']} !important; }}
h3,h4 {{ font-family:var(--serif); color:{t['ink']}; }}
.banner {{ background:transparent !important; color:{t['accent2']} !important; text-shadow:none !important; font-family:'DM Sans','Segoe UI',sans-serif !important;
  font-size:1rem !important; font-weight:700 !important; letter-spacing:.2em !important; text-transform:uppercase; padding:16px 48px 12px !important;
  border-bottom:1px solid {t['rule']}; gap:12px !important; }}
.banner .ico {{ color:{t['accent']}; flex:none; }}
.instruction {{ border-left:2px solid {t['accent']} !important; color:{t['ink']} !important; }}
.gram-note {{ background:{t['soft']} !important; border:none !important; border-left:3px solid {t['accent']} !important; border-radius:2px !important; color:{t['ink']} !important; }}
.person-card, .tf-row, .card {{ border-radius:4px !important; box-shadow:none !important; border:1px solid {t['rule']} !important; background:#fff; }}
.btn-check, .btn-reset, .btn-suggest, .btn-akey, .btn-roul {{ border-radius:2px !important; box-shadow:none !important; border:1.5px solid {t['ink']} !important;
  background:{t['ink']} !important; color:#fff !important; font-weight:600; letter-spacing:.04em; }}
.btn-reset, .btn-akey {{ background:transparent !important; color:{t['ink']} !important; }}
.btn-check:hover, .btn-reset:hover, .btn-suggest:hover, .btn-akey:hover, .btn-roul:hover {{ transform:none !important; box-shadow:none !important; background:{t['accent']} !important; border-color:{t['accent']} !important; color:#fff !important; }}
.example-badge {{ background:{t['accent2']} !important; border-radius:50% !important; }}
.sticky-bank {{ background:{t['paper']} !important; border-bottom:1px solid {t['rule']} !important; }}
#nav {{ background:rgba(31,42,36,.96) !important; }}
.dot.active {{ background:{t['accent']} !important; }}
#progBar {{ background:{t['accent']} !important; height:3px !important; }}
.pe, .person-card .pe {{ filter:grayscale(.55) contrast(.95); }}
/* boxes */
.read-box, .qcard, .audio-box, .gb-box, .step-card {{ border:1px solid {t['rule']} !important; border-radius:4px !important; box-shadow:none !important; background:#fff; }}
.read-box h3, .gb-box h3, .qcard h3 {{ color:{t['accent']} !important; }}
.ans-input {{ background:{t['soft']} !important; border-bottom:1.5px solid {t['ink']} !important; border-radius:2px !important; }}
button {{ border-radius:2px; }}
.audio-box, .audio-box.pending {{ background:{t['soft']} !important; color:{t['ink']} !important; border:1px dashed {t['muted']} !important; }}
/* chrome */
.banner::after, .banner::before {{ display:none !important; content:none !important; }}
#notesBtn, #homeBtn {{ background:{t['paper']} !important; color:{t['ink']} !important; border:1px solid {t['rule']} !important; border-radius:2px !important; box-shadow:none !important; font-weight:600; letter-spacing:.05em; }}
#notesBtn:hover, #homeBtn:hover {{ background:{t['soft']} !important; }}
#nav button {{ border-radius:2px !important; background:rgba(255,255,255,.1) !important; color:#fff !important; }}
#nav button[onclick*="saveNotesPDF"], #nav button[onclick*="Save"], #nav button[title*="Save"] {{ background:{t['accent2']} !important; }}
#nav button[onclick*="clearAllNotes"] {{ background:transparent !important; border:1px solid rgba(255,255,255,.35) !important; }}
/* cover */
#s1, #hw-cover {{ background:{t['cover_bg']} !important; color:{t['ink']}; display:flex; flex-direction:column; align-items:stretch !important; justify-content:flex-start !important; padding:0 !important; overflow:hidden; }}
#s1 .cv-top, #hw-cover .cv-top {{ flex:1; display:flex; flex-direction:column; justify-content:center; padding:48px 9vw 20px; position:relative; z-index:2; }}
.cv-kicker {{ font-family:'DM Sans',sans-serif; font-size:1.05rem; font-weight:700; letter-spacing:.28em; text-transform:uppercase; color:{t['accent']}; display:flex; align-items:center; gap:12px; }}
.cv-kicker .ico {{ width:26px; height:26px; }}
.cv-brand {{ font-family:'DM Sans',sans-serif; font-size:1.2rem; letter-spacing:.06em; color:{t['muted']}; margin-top:6px; }}
.cv-title {{ font-family:var(--serif); font-weight:600; font-size:clamp(3.2rem,8vw,7rem); line-height:1.02; letter-spacing:-.025em; color:{t['ink']}; margin:26px 0 18px; max-width:1100px; }}
.cv-title em {{ font-style:italic; font-weight:500; color:{t['accent']}; }}
.cv-rule {{ width:84px; height:2px; background:{t['accent']}; margin:4px 0 20px; }}
.cv-sub {{ font-family:'DM Sans',sans-serif; font-size:1.35rem; color:{t['muted']}; max-width:760px; line-height:1.5; }}
.cv-art {{ display:block; width:100%; height:34vh; min-height:200px; flex:none; }}
.cv-actions {{ position:absolute; left:0; right:0; bottom:calc(34vh + 14px); display:flex; justify-content:space-between; padding:0 9vw; z-index:3; pointer-events:none; }}
.cv-actions > * {{ pointer-events:auto; }}
.cv-home {{ color:{t['ink']}; text-decoration:none; display:inline-flex; align-items:center; gap:8px; font-weight:600; letter-spacing:.06em; font-size:.95rem; }}
#s1 button[onclick^="goToId"] {{ background:{t['ink']} !important; color:#fff !important; border:none !important; border-radius:2px !important; box-shadow:none !important; font-weight:700 !important; letter-spacing:.14em; text-transform:uppercase; font-size:.9rem !important; padding:13px 26px !important; }}
#s1 button[onclick^="goToId"]:hover {{ background:{t['accent']} !important; }}
.cover-bubble, .cover-heart {{ display:none !important; }}
'''

COVER_RE = re.compile(r'(<div class="slide active" id="s1">).*?(</div>\s*\n\s*\n?<!--|\n</div>\n)', re.S)

def cover(t, title_html, sub, label, art):
    return (f'<div class="cv-top"><div class="cv-kicker">{ICONS[t["icon"]]}<span>{label}</span></div>'
            f'<div class="cv-brand">Conversational English &middot; with teacher Nanda</div>'
            f'<div class="cv-title">{title_html}</div><div class="cv-rule"></div>'
            + (f'<div class="cv-sub">{sub}</div>' if sub else '') + '</div>')

def apply_theme(html, tname, title_html, sub='', label=None, scene_kind=None):
    t = dict(THEMES[tname]); t['name']=tname
    html = re.sub(r'/\* ===== EDITORIAL THEME.*?(?=</style>)', '', html, count=1, flags=re.S)
    # fonts
    if 'family=Fraunces' not in html:
        html = html.replace('</head>', '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&display=swap" rel="stylesheet">\n</head>',1)
    # style: append LAST style block end
    k = html.rindex('</style>', 0, html.index('<script')); html = html[:k]+css(t)+html[k:]
    # banners: replace leading emoji by line icon
    def ban(m):
        kind=m.group(1); rest=m.group(3)
        rest=re.sub(r'^[^\w<]+\s*','',rest)
        return f'<div class="banner banner-{kind}">{ICONS.get(kind,ICONS["leadin"])}<span>{rest}</span></div>'
    html = re.sub(r'<div class="banner banner-([a-z]+)"([^>]*)>(.*?)</div>', ban, html)
    art = scene(scene_kind or t['scene_kind'], t); lab = label or t['label']
    # cover s1
    i = html.index('<div class="slide active" id="s1">'); j = html.index('<!--', i)
    s1 = ('<div class="slide active" id="s1">'+cover(t,title_html,sub,lab,art)+
          '<div class="cv-actions"><a class="cv-home" href="../index.html" title="All Courses">'+ICONS['home']+'<span>All courses</span></a>'
          '<button onclick="goToId(\'hw-cover\')">Homework</button></div>'+art+'</div>\n\n')
    html = html[:i]+s1+html[j:]
    # homework cover
    i = html.index('<div class="slide" id="hw-cover">'); j = html.index('<!--', i)
    hw = ('<div class="slide" id="hw-cover">'+cover(t,title_html,'Homework','Homework',art).replace(ICONS[t['icon']], ICONS['hw'],1)+art+'</div>\n')
    html = html[:i]+hw+html[j:]
    return html
