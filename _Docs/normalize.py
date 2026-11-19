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
