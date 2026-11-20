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
 'globe':  _i('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>'),
 'home':     _i('<path d="M4 11l8-7 8 7"/><path d="M6 10v10h12V10"/>'),
 'mountain': _i('<path d="M2 20l7-12 4 6 3-4 6 10z"/><path d="M9 8l-2 3.5M16 10l1.5 2.5"/>'),
 'wave':     _i('<path d="M2 9c2.5-3 5-3 7.5 0s5 3 7.5 0 3-2 5-1"/><path d="M2 14c2.5-3 5-3 7.5 0s5 3 7.5 0 3-2 5-1"/><path d="M2 19c2.5-3 5-3 7.5 0s5 3 7.5 0 3-2 5-1"/>'),
 'lifebuoy': _i('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.8"/><path d="M5.6 5.6l3.7 3.7M14.7 14.7l3.7 3.7M18.4 5.6l-3.7 3.7M9.3 14.7l-3.7 3.7"/>'),
 'plane':    _i('<path d="M21 3L3 10.5l6 2.5 2.5 6z"/><path d="M9 13l12-10"/>'),
 'tree':     _i('<path d="M12 21v-6"/><path d="M12 3l5 7h-3l4 6H6l4-6H7z"/>'),
 'pin':      _i('<path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>'),
 'compass':  _i('<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>'),
}

FONTS = {
 'fraunces': ("Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500", "'Fraunces','Playfair Display',Georgia,serif"),
 'bitter':   ("Bitter:ital,wght@0,600;0,800;1,600", "'Bitter',Georgia,serif"),
 'dmserif':  ("DM+Serif+Display:ital@0;1", "'DM Serif Display',Georgia,serif"),
 'baskerville': ("Libre+Baskerville:ital,wght@0,700;1,400", "'Libre Baskerville',Georgia,serif"),
 'oswald':   ("Oswald:wght@500;600", "'Oswald','Arial Narrow',sans-serif"),
 'sourcesans': ("Source+Sans+3:wght@400;600;700", "'Source Sans 3','Segoe UI',sans-serif"),
 'worksans': ("Work+Sans:wght@400;600;700", "'Work Sans','Segoe UI',sans-serif"),
 'dmsans':   ("DM+Sans:wght@400;700;800", "'DM Sans','Segoe UI',sans-serif"),
}
def font_link(t):
    fam = {t['tfont'], t['bfont'], 'dmsans'}
    q = '&'.join('family=' + FONTS[k][0] for k in sorted(fam))
    return '<link data-theme-font href="https://fonts.googleapis.com/css2?%s&display=swap" rel="stylesheet">' % q

def IC(name, t):
    return ICONS[name].replace('stroke-width="1.6"', 'stroke-width="%s"' % t.get('sw', '1.6'))

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
    elif kind=='night':
        import random; r=random.Random(9)
        for _ in range(70):
            out.append(f'<circle cx="{r.randint(10,W-10)}" cy="{r.randint(8,230)}" r="{r.choice([1,1,1.5,2])}" fill="#FFFFFF" opacity="{r.choice([.35,.5,.8])}"/>')
        out.append(hills(a,270,12,1)); out.append(hills(b,305,12,3)); out.append(hills(c,338,10,5)); out.append(hills(d,372,8,7))
        out.append(f'<path d="M1040 372 l16 -34 l16 34z M1056 338 v-34" stroke="{sun}" stroke-width="2" fill="{sun}" opacity=".0"/>')
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

THEMES = {}
_BAN = lambda c: {k: c for k in ('leadin','listening','speaking','grammar','pron','reading','vocab','bridge','review','hw','video')}
THEMES['survival'] = dict(   # AEF 4 - 5A  "I'm a survivor": dark forest poster
    label='Unit 5 · Lesson A', scene_kind='jungle', icon='tree', emblem='tree', tfont='bitter', bfont='sourcesans', layout='poster', tcase='none', sw='1.8',
    paper='#FAF7F0', ink='#1E2B23', muted='#5A6459', accent='#B4562B', accent2='#2F5D4A', soft='#EBE5D3', rule='#D6CDB5',
    cover_bg='#1F3A2E', cover_ink='#F4EEDD', cover_accent='#EBA765', cover_muted='#B9C7B8',
    scene=('#2C4C3C','#25402F','#1B3225','#12261B','#E3B766'), banner=_BAN('#2F5D4A'), kind_icons={'leadin':'compass'})
THEMES['world'] = dict(      # Empower A1 1A  "I'm from Mexico": travel / world, emblem cover
    label='Unit 1 · Lesson A', scene_kind='hills', icon='globe', emblem='globe', tfont='dmserif', bfont='dmsans', layout='emblem', tcase='none', sw='1.5',
    paper='#FBF8F1', ink='#1F2A33', muted='#5C6670', accent='#C2573A', accent2='#2E5A74', soft='#EFE7D9', rule='#DDD2BD',
    cover_bg='#F1EADC', cover_ink='#1F2A33', cover_accent='#C2573A', cover_muted='#5C6670',
    scene=('#CAD7DE','#9DB8C6','#5E8296','#2F4E63','#E5B06A'), banner=_BAN('#2E5A74'), kind_icons={'leadin':'pin'})
THEMES['welcome'] = dict(    # Empower A1 Welcome: friendly, centered cover
    label='Welcome', scene_kind='sea', icon='speaking', emblem='speaking', tfont='baskerville', bfont='dmsans', layout='center', tcase='none', sw='1.6',
    paper='#FCF9F3', ink='#2A2433', muted='#6A6275', accent='#A0526B', accent2='#2F5F66', soft='#EEE6DB', rule='#DDD2C2',
    cover_bg='#F2EBDF', cover_ink='#2A2433', cover_accent='#A0526B', cover_muted='#6A6275',
    scene=('#D3E2E0','#A9CBC7','#72A5A2','#3F7A7C','#EBC27F'), banner=_BAN('#2F5F66'), kind_icons={})
THEMES['b2lost'] = dict(     # Empower B2 2A "It was getting late and I was lost": night at sea, poster cover
    label='Unit 2 · Lesson A', scene_kind='night', icon='lifebuoy', emblem='lifebuoy', tfont='bitter', bfont='dmsans', layout='poster', tcase='none', sw='1.7',
    paper='#F6F4EE', ink='#14222F', muted='#556573', accent='#C4532D', accent2='#1F4A66', soft='#E6E4DA', rule='#CFCFC4',
    cover_bg='#12263A', cover_ink='#F3EEDF', cover_accent='#F0A468', cover_muted='#A9BACB',
    scene=('#1D3A56','#173049','#10253B','#0A1A2B','#F2E4B8'), banner=_BAN('#1F4A66'), kind_icons={'leadin':'lifebuoy','bridge':'wave'})

def LAYOUT_CSS(t):
    L = t['layout']; out = ''
    if L == 'poster':
        out += f"""#s1, #hw-cover {{ background:{t['cover_bg']} !important; color:{t['cover_ink']}; }}
#s1 .cv-title, #hw-cover .cv-title {{ color:{t['cover_ink']}; }} #s1 .cv-title em, #hw-cover .cv-title em {{ color:{t['cover_accent']}; }}
#s1 .cv-kicker, #hw-cover .cv-kicker {{ color:{t['cover_accent']}; }} #s1 .cv-brand, #hw-cover .cv-brand, #s1 .cv-sub, #hw-cover .cv-sub {{ color:{t['cover_muted']}; }}
#s1 .cv-rule, #hw-cover .cv-rule {{ background:{t['cover_accent']}; }}

#s1 .cv-top, #hw-cover .cv-top {{ border-left:6px solid {t['cover_accent']}; margin:40px 0 0 6vw; padding-left:3vw; }}"""
    elif L == 'center':
        out += """#s1 .cv-top, #hw-cover .cv-top { align-items:center; text-align:center; }
#s1 .cv-kicker, #hw-cover .cv-kicker { justify-content:center; } .cv-rule { margin-left:auto; margin-right:auto; } .cv-sub { margin:0 auto; }
#s1 .cv-title, #hw-cover .cv-title { margin-left:auto; margin-right:auto; }"""
    elif L == 'emblem':
        out += f"""#s1 .cv-top, #hw-cover .cv-top {{ padding-right:44vw; }}
.cv-emblem {{ position:absolute; right:7vw; top:50%; transform:translateY(-58%); width:30vw; max-width:420px; aspect-ratio:1; border-radius:50%; border:2px solid {t['accent']}; display:flex; align-items:center; justify-content:center; color:{t['accent']}; background:{t['soft']}; }}
.cv-emblem .ico {{ width:58%; height:58%; stroke-width:1.1; }}"""
    return out

def css(t):
    return f'''
/* ===== EDITORIAL THEME ({t['name']}) ===== */
:root {{ --navy:{t['ink']}; --coral:{t['accent']}; --sky:{t['soft']}; --mint:{t['accent2']}; --lemon:{t['soft']}; --lilac:{t['rule']}; --paper:{t['paper']}; --mist:{t['soft']};
  --serif:{FONTS[t['tfont']][1]}; --sans:{FONTS[t['bfont']][1]}; }}
body, button, input, select, textarea {{ font-family:var(--sans) !important; }}
body {{ background:{t['paper']} !important; color:{t['ink']} !important; }}
.slide {{ background:{t['paper']}; }}
h2 {{ font-family:var(--serif) !important; font-weight:{'500' if t['tfont']=='oswald' else '600'} !important; letter-spacing:{'.04em' if t['tcase']=='upper' else '-.01em'}; text-transform:{'uppercase' if t['tcase']=='upper' else 'none'}; color:{t['ink']} !important; }}
h2::after {{ width:56px !important; height:2px !important; border-radius:0 !important; margin-top:10px !important; background:{t['accent']} !important; }}
h3,h4 {{ font-family:var(--serif); color:{t['ink']}; }}
.banner {{ background:transparent !important; color:{t['accent2']} !important; text-shadow:none !important; font-family:var(--sans) !important;
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
#notesPanel #notesToolbar button[title="Yellow"] {{ background:#FFE600 !important; }}
#notesPanel #notesToolbar button[title="Green"] {{ background:#90EE90 !important; }}
#notesPanel #notesToolbar button[title="Pink"] {{ background:#FFB3C6 !important; }}
#notesPanel #notesToolbar button[title="Blue"] {{ background:#ADD8E6 !important; }}
#notesPanel #notesToolbar button[title="Remove highlight"] {{ color:{t['muted']} !important; }}
/* chrome */
.banner::after, .banner::before {{ display:none !important; content:none !important; }}
#notesBtn, #homeBtn {{ background:{t['soft']} !important; color:{t['ink']} !important; border:none !important; outline:none !important; border-radius:3px !important; box-shadow:none !important; font-weight:600; letter-spacing:.05em; display:inline-flex; align-items:center; gap:8px; }}
#notesBtn:hover, #homeBtn:hover {{ background:{t['rule']} !important; }}
#notesBtn .ico, #homeBtn .ico {{ width:18px; height:18px; color:{t['accent']}; }}
#nav button {{ border:none !important; outline:none !important; box-shadow:none !important; border-radius:3px !important; background:transparent !important; color:#fff !important; font-weight:600; letter-spacing:.04em; }}
#nav button:hover:not(:disabled) {{ background:rgba(255,255,255,.12) !important; }}
#dlNotesBtn {{ background:transparent !important; color:#E6D3A8 !important; }}
#nav button[onclick*="clearAllNotes"] {{ background:transparent !important; color:rgba(255,255,255,.6) !important; border:none !important; }}
/* notes panel */
#notesPanel {{ background:{t['paper']} !important; border:1px solid {t['rule']} !important; border-radius:4px !important; box-shadow:0 8px 30px rgba(31,42,36,.14) !important; }}
#notesPanel #notesToolbar {{ background:{t['soft']} !important; border-radius:3px 3px 0 0 !important; border-bottom:1px solid {t['rule']} !important; }}
#notesPanel #notesToolbar button {{ background:transparent !important; color:{t['ink']} !important; border:none !important; border-radius:3px !important; }}
#notesPanel #notesToolbar button:hover {{ background:{t['rule']} !important; }}
#notesPanel #notesToolbar button[title="Yellow"], #notesPanel #notesToolbar button[title="Green"], #notesPanel #notesToolbar button[title="Pink"], #notesPanel #notesToolbar button[title="Blue"] {{ border-radius:50% !important; width:16px !important; height:16px !important; opacity:.85; }}
#notesPanel #notesTA {{ background:{t['paper']} repeating-linear-gradient(transparent,transparent 31px,{t['rule']} 31px,{t['rule']} 32px) !important; background-attachment:local !important; color:{t['ink']} !important; font-weight:500 !important; border-radius:0 0 3px 3px !important; line-height:32px !important; padding:0 16px !important; font-size:1.2rem !important; }}
#notesPanel #notesTA:empty::before {{ content:none !important; display:none !important; }}
#notesPanel #notesTA * {{ line-height:32px; }}
#notesPanel #notesToolbar .nt-emojis {{ display:flex; gap:2px; align-items:center; margin-left:8px; padding-left:8px; border-left:1px solid {t['rule']}; }}
#notesPanel #notesToolbar .nt-emojis button {{ font-size:1.15rem !important; line-height:1; padding:3px 6px !important; cursor:pointer; }}
#notesPanel #notesTA [style*="background-color"] {{ color:{t['ink']} !important; }}
/* cover */
#s1, #hw-cover {{ background:{t['cover_bg']} !important; color:{t['ink']}; display:flex; flex-direction:column; align-items:stretch !important; justify-content:flex-start !important; padding:0 !important; overflow:hidden; }}
#s1 .cv-top, #hw-cover .cv-top {{ flex:1; display:flex; flex-direction:column; justify-content:center; padding:48px 9vw 20px; position:relative; z-index:2; }}
.cv-kicker {{ font-family:var(--sans); font-size:1.05rem; font-weight:700; letter-spacing:.28em; text-transform:uppercase; color:{t['accent']}; display:flex; align-items:center; gap:12px; }}
.cv-kicker .ico {{ width:26px; height:26px; }}
.cv-brand {{ font-family:var(--sans); font-size:1.2rem; letter-spacing:.06em; color:{t['muted']}; margin-top:6px; }}
.cv-title {{ font-family:var(--serif); font-weight:{'600' if t['tfont']=='oswald' else '700' if t['tfont']=='bitter' else '600'}; font-size:clamp(3.2rem,8vw,7rem); line-height:{'1.08' if t['tcase']=='upper' else '1.02'}; letter-spacing:{'.03em' if t['tcase']=='upper' else '-.025em'}; text-transform:{'uppercase' if t['tcase']=='upper' else 'none'}; color:{t['ink']}; margin:26px 0 18px; max-width:1100px; }}
.cv-title em {{ font-style:{'normal' if t['tfont']=='oswald' else 'italic'}; font-weight:{'600' if t['tfont']=='oswald' else '500'}; color:{t['accent']}; }}
.cv-rule {{ width:84px; height:2px; background:{t['accent']}; margin:4px 0 20px; }}
.cv-sub {{ font-family:var(--sans); font-size:1.35rem; color:{t['muted']}; max-width:760px; line-height:1.5; }}
.cv-art {{ display:block; width:100%; height:34vh; min-height:200px; flex:none; }}
.cv-actions {{ display:flex; align-items:center; gap:36px; margin-top:34px; }}
.cv-home {{ color:{t['muted']}; text-decoration:none; display:inline-flex; align-items:center; gap:8px; font-weight:600; letter-spacing:.14em; text-transform:uppercase; font-size:.9rem; }}
.cv-home:hover {{ color:{t['accent']}; }}
.cv-home .ico {{ width:18px; height:18px; }}
.cover-bubble, .cover-heart {{ display:none !important; }}

#nav .nav-cover {{ display:none; position:absolute; top:50%; transform:translateY(-50%); margin:0 !important; padding:8px 18px !important; background:transparent !important; color:#fff !important; border:1.5px solid rgba(255,255,255,.55) !important; border-radius:2px !important; font-size:.85rem !important; font-weight:700 !important; letter-spacing:.14em !important; text-transform:uppercase; text-decoration:none; cursor:pointer; align-items:center; gap:8px; box-shadow:none !important; font-family:var(--sans); }}
#nav .nav-cover .ico {{ width:16px; height:16px; }}
#navHome {{ left:20px; }} #navHw {{ right:20px; }}
body.on-cover #nav .nav-cover {{ display:inline-flex; }}
#nav .nav-cover:hover {{ background:{t['accent']} !important; border-color:{t['accent']} !important; }}
/* hide the placeholder text once the audio file is wired */
.audio-box:not(.pending) .ph {{ display:none !important; }}
/* Check Answers / Reset: right after the exercises, small buttons, no docking */
.check-dock {{ position:static !important; background:transparent !important; border:none !important; padding:0 !important; margin:10px 0 4px !important; display:flex; justify-content:center; gap:10px; }}
.check-dock .btn-check, .check-dock .btn-reset, .check-dock .btn-suggest {{ padding:7px 20px !important; font-size:.95rem !important; min-width:0 !important; width:auto !important; }}
.ans-input.pick {{ width:64px !important; min-width:0; text-align:center; font-weight:800; padding:2px 4px !important; margin:0 6px; }}
/* compact audio player: full seek line + play, time, volume, options */
.ins-audio {{ flex:none !important; width:340px; max-width:30vw; }}
.audio-box:not(.pending) {{ background:{t['soft']} !important; border:1px solid {t['rule']} !important; padding:3px !important; margin:0 !important; border-radius:999px !important; display:block !important; width:100%; box-shadow:none !important; }}
.audio-box:not(.pending) audio {{ display:block; width:100% !important; height:38px !important; min-width:0; }}
/* cover layout: {t['layout']} */
{LAYOUT_CSS(t)}
'''

COVER_RE = re.compile(r'(<div class="slide active" id="s1">).*?(</div>\s*\n\s*\n?<!--|\n</div>\n)', re.S)

def cover(t, title_html, sub, label, art):
    emb = f'<div class="cv-emblem">{IC(t["emblem"], t)}</div>' if t['layout'] == 'emblem' else ''
    return (emb + f'<div class="cv-top"><div class="cv-kicker">{IC(t["icon"], t)}<span>{label}</span></div>'
            f'<div class="cv-brand">Conversational English &middot; with teacher Nanda</div>'
            f'<div class="cv-title">{title_html}</div><div class="cv-rule"></div>'
            + (f'<div class="cv-sub">{sub}</div>' if sub else '') + '@@ACT@@</div>')

def apply_theme(html, tname, title_html=None, sub='', label=None, scene_kind=None):
    if title_html is None:
        m = re.search(r'<div class="title-main">(.*?)</div>', html, re.S) or re.search(r'<div class="cv-title">(.*?)</div>', html, re.S); title_html = m.group(1).replace("'", '&rsquo;')
        title_html = re.sub(r'<span class="title-accent">(.*?)</span>', r'<em>\1</em>', title_html)
    t = dict(THEMES[tname]); t['name']=tname
    html = re.sub(r'/\* ===== EDITORIAL THEME.*?(?=</style>)', '', html, count=1, flags=re.S)
    # fonts
    html = re.sub(r'<link data-theme-font[^>]*>\n?', '', html)
    html = re.sub(r'<link href="https://fonts.googleapis.com/css2\?family=Fraunces[^>]*>\n?', '', html)
    html = html.replace('</head>', font_link(t) + '\n</head>', 1)
    # style: append LAST style block end
    k = html.rindex('</style>', 0, html.index('<script')); html = html[:k]+css(t)+html[k:]
    # banners: replace leading emoji by line icon
    def ban(m):
        kind=m.group(1); rest=m.group(3)
        rest=re.sub(r'^(<svg.*?</svg>)+','',rest,flags=re.S); rest=re.sub(r'^[^\w<]+\s*','',rest)
        return f'<div class="banner banner-{kind}">{IC(t.get("kind_icons",{}).get(kind, kind if kind in ICONS else "leadin"), t)}<span>{rest}</span></div>'
    html = re.sub(r'<div class="banner banner-([a-z]+)"([^>]*)>(.*?)</div>', ban, html)
    html = re.sub(r"document\.getElementById\('notesBtn'\)\.textContent = notesOpen \? '[^']*' : '.*?';",
                  lambda m: "document.getElementById('notesBtn').innerHTML = notesOpen ? 'Close' : '" + IC('hw', t) + " Notes';", html, count=1)
    html = html.replace('>🏠</button>','>'+ICONS['home']+'</button>').replace('📝 Notes','NOTESICO Notes').replace('NOTESICO',ICONS['hw'])
    html = html.replace("notesOpen ? '✕ Close' : '📝 Notes'","notesOpen ? '✕ Close' : 'Notes'").replace('💾 Save Notes','Save Notes').replace('🗑️ Clear Notes','Clear Notes')
    # notes: no placeholder, emoji stamps
    html = html.replace(' data-placeholder="Your notes for this slide…"', '')
    html = re.sub(r'<span class="nt-emojis">.*?</span>\s*', '', html, flags=re.S)
    EM = [('✅','Correct'),('❌','Mistake'),('🔊','Pronunciation'),('📐','Grammar'),('🏷️','Vocabulary'),('💬','Expression'),('⭐','Important'),('❓','Question')]
    emo = '<span class="nt-emojis">' + ''.join(f'<button onmousedown="event.preventDefault()" onclick="notesEmoji(\'{e}\')" title="{n}">{e}</button>' for e, n in EM) + '</span>\n  '
    k = html.index('<div id="notesTA"'); k = html.rindex('</div>', 0, k)
    html = html[:k] + '  ' + emo + html[k:]
    html = re.sub(r'/\* notes-emoji-js \*/.*?/\* end notes-emoji-js \*/\s*', '', html, flags=re.S)
    j = html.rindex('</script>')
    html = html[:j] + "/* notes-emoji-js */\nfunction notesEmoji(e){ var ta = document.getElementById('notesTA'); ta.focus(); document.execCommand('insertText', false, e + ' '); saveNotes(); }\n/* end notes-emoji-js */\n" + html[j:]
    # nav buttons for the cover (All courses = left, Homework = right)
    html = re.sub(r'<a id="navHome".*?</a>\s*', '', html, flags=re.S); html = re.sub(r'<button id="navHw".*?</button>\s*', '', html, flags=re.S)
    html = re.sub(r'/\* cover-nav-js \*/.*?/\* end cover-nav-js \*/\s*', '', html, flags=re.S)
    html = html.replace('<div id="nav">', '<div id="nav">\n  <a id="navHome" class="nav-cover" href="../index.html" title="All Courses">'+IC('home', t)+'<span>All courses</span></a>', 1)
    k = html.index('</div>', html.index('id="dlNotesBtn"')); k = html.index('</div>', html.index('Clear Notes')) if 'Clear Notes' in html else k
    html = html[:k] + '  <button id="navHw" class="nav-cover" onclick="goToId(\'hw-cover\')">Homework &rarr;</button>\n' + html[k:]
    j = html.rindex('</script>')
    html = html[:j] + "/* cover-nav-js */\n(function(){ var g = goTo; goTo = function(n){ g(n); document.body.classList.toggle('on-cover', current === 0); }; document.body.classList.toggle('on-cover', current === 0); })();\n/* end cover-nav-js */\n" + html[j:]
    art = scene(scene_kind or t['scene_kind'], t); lab = label or t['label']
    # cover s1
    i = html.index('<div class="slide active" id="s1">'); j = html.index('<div class="slide"', i); j = html.rfind('<!--',i,j) if html.rfind('<!--',i,j)>i else j
    act = ('<a class="cv-home" href="../index.html" title="All Courses">'+IC('home', t)+'<span>All courses</span></a>'
           '<button class="cv-hw" onclick="goToId(\'hw-cover\')">Homework &rarr;</button>')
    s1 = ('<div class="slide active" id="s1">'+cover(t,title_html,sub,lab,art).replace('@@ACT@@','')+art+'</div>\n\n')
    html = html[:i]+s1+html[j:]
    # homework cover
    i = html.index('<div class="slide" id="hw-cover">'); j = html.index('<div class="slide"', i+10); j = html.rfind('<!--',i,j) if html.rfind('<!--',i,j)>i else j
    hw = ('<div class="slide" id="hw-cover">'+cover(t,title_html,'Homework','Homework',art).replace('@@ACT@@','').replace(IC(t['icon'], t), IC('hw', t),1)+art+'</div>\n')
    html = html[:i]+hw+html[j:]
    from normalize import move_checks, move_show_answers, single_char_selects_to_inputs
    html = single_char_selects_to_inputs(html)
    html = move_checks(html)
    html = move_show_answers(html)
    return html
