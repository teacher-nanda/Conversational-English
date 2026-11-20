"""Move 'Check Answers'/'Reset' buttons out of the sticky bar (top) to right after the exercises."""
import re
from bs4 import BeautifulSoup

CHK = re.compile(r'^(check|reset)[A-Za-z]*\(\s*[\'"]([^\'"]+)[\'"]')

def single_char_selects_to_inputs(html):
    """Ordering / matching exercises (answer = one number or letter): typed short blank, inline, instead of a dropdown."""
    parts = re.split(r'(?=<div class="slide[ "])', html)
    out = [parts[0]]
    for seg in parts[1:]:
        end = seg.find('<!-- END #deck -->'); tail = ''
        if end > -1: seg, tail = seg[:end], seg[end:]
        if '<select class="gsel"' in seg:
            soup = BeautifulSoup(seg, 'html.parser'); changed = False
            for sel in soup.select('select.gsel'):
                opts = [o.get('value', '') for o in sel.find_all('option') if o.get('value', '')]
                if not opts or any(len(o) > 2 for o in opts): continue
                inp = soup.new_tag('input', attrs={'class': 'ans-input pick', 'data-ans': sel.get('data-ans', ''), 'maxlength': '2',
                                                   'aria-label': 'answer', 'autocomplete': 'off'})
                par = sel.parent
                if par is not None and par.name == 'span' and 'margin-left' in (par.get('style') or '') and len(par.contents) == 1:
                    prev = par.find_previous_sibling()
                    if prev is not None and prev.name == 'br' and prev.parent is par.parent: prev.decompose()
                    par.replace_with(inp)
                else:
                    sel.replace_with(inp)
                changed = True
            if changed:
                if not soup.select('select.gsel'):
                    for b in soup.find_all('button'):
                        oc = b.get('onclick', '')
                        b['onclick'] = oc.replace('checkSel(', 'checkSlide(').replace('resetSel(', 'resetSlide(')
                seg = str(soup)
        out.append(seg + tail)
    return ''.join(out)

def move_checks(html):
    parts = re.split(r'(?=<div class="slide[ "])', html)
    out = [parts[0]]
    for seg in parts[1:]:
        # only the slide's own markup: cut before the trailing non-slide content of the last slide
        end = seg.find('<!-- END #deck -->')
        tail = ''
        if end > -1: seg, tail = seg[:end], seg[end:]
        if 'btn-check' in seg:
            soup = BeautifulSoup(seg, 'html.parser')
            changed = False
            for bank in soup.select('.sticky-bank'):
                moved = []
                for b in bank.find_all('button'):
                    m = CHK.match(b.get('onclick', ''))
                    if m:
                        moved.append((b.extract(), m.group(2)))
                if not moved: continue
                changed = True
                target = soup.find(id=moved[0][1])
                row = soup.new_tag('div', attrs={'class': 'btn-row check-dock'})
                for b, _ in moved: row.append(b)
                if target is not None: target.insert_after(row)
                else: bank.parent.append(row)
                # drop empty sticky shells
                for r in bank.select('.stickyrow'):
                    if not r.get_text(strip=True) and not r.find(True): r.decompose()
                if not bank.get_text(strip=True) and not bank.find(True): bank.decompose()
            for row in soup.select('.btn-row'):
                if any(CHK.match(b.get('onclick', '')) for b in row.find_all('button')) and 'check-dock' not in (row.get('class') or []):
                    row['class'] = (row.get('class') or []) + ['check-dock']; changed = True
            if changed: seg = str(soup)
        out.append(seg + tail)
    return ''.join(out)


SHOWK = re.compile(r"showKeys\(this,\s*'([^']+)'\)")
def move_show_answers(html):
    """'Show answers' buttons never go before the exercise: they sit after it, in the same small button row as Check Answers."""
    parts = re.split(r'(?=<div class="slide[ "])', html)
    out = [parts[0]]
    for seg in parts[1:]:
        end = seg.find('<!-- END #deck -->')
        tail = ''
        if end > -1: seg, tail = seg[:end], seg[end:]
        if 'showKeys' in seg or 'Show the answer' in seg or 'Show answers' in seg:
            soup = BeautifulSoup(seg, 'html.parser'); changed = False
            # 1) showKeys buttons living in the sticky bar at the top
            for b in list(soup.find_all('button')):
                m = SHOWK.match(b.get('onclick', '') or '')
                if not m: continue
                target = soup.find(id=m.group(1))
                if target is None: continue
                nxt = target.find_next_sibling(class_='check-dock')
                bank = b.find_parent(class_='sticky-bank')
                if bank is None and nxt is not None and b.parent is nxt: continue
                b.extract(); b['style'] = ''
                if nxt is None:
                    nxt = soup.new_tag('div', attrs={'class': 'btn-row check-dock'}); target.insert_after(nxt)
                nxt.append(b); changed = True
                if bank is not None:
                    for r in bank.select('.stickyrow'):
                        if not r.get_text(strip=True) and not r.find(True): r.decompose()
                    if not bank.get_text(strip=True) and not bank.find(True): bank.decompose()
            # 2) 'Show the answer(s)' key buttons placed before the content: move button + key box to the end of the slide
            content = soup.select_one('.content')
            if content is not None:
                for b in list(soup.find_all('button')):
                    oc = b.get('onclick', '') or ''
                    if not oc.startswith('toggleSuggested') or not re.search(r'show (the )?answers?', b.get_text(' ', strip=True), re.I): continue
                    kid = re.search(r"toggleSuggested\('([^']+)'\)", oc).group(1)
                    kb = soup.find(id=kid)
                    kids = [x for x in content.descendants if getattr(x, 'name', None)]
                    pos = kids.index(b) if b in kids else -1
                    later = [x for x in kids[pos+1:] if x.name in ('input','select') or any(c in (x.get('class') or []) for c in ('read-box','qcard','ex-row','qline','circ-opt'))] if pos >= 0 else []
                    if not later: continue
                    b.extract(); b['style'] = ''
                    if kb is not None: kb.extract()
                    docks = [d for d in content.select('.check-dock')]
                    if docks:
                        row = docks[-1]; row.append(b)
                        if kb is not None: row.insert_after(kb)
                    else:
                        row = soup.new_tag('div', attrs={'class': 'btn-row check-dock'}); row.append(b)
                        content.append(row)
                        if kb is not None: row.insert_after(kb)
                    changed = True
            if changed: seg = str(soup)
        out.append(seg + tail)
    return ''.join(out)
