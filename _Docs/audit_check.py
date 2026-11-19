import sys
from playwright.sync_api import sync_playwright
JS = """(function(){
 var out=[];
 document.querySelectorAll('.slide').forEach(function(s){
  var ex=s.querySelectorAll('.ans-input,.gsel,.circ-opt,.wb-blank,.wo-chip,.wo-line,.classify-cols,.fcard,.strbtn,[data-stress],.sentbtn,.feelbtn,.tf-row button,.ex-row');
  s.querySelectorAll('button').forEach(function(b){
    var oc=(b.getAttribute('onclick')||'');
    if(!/^(check|reset)[A-Za-z]*\\(/.test(oc)) return;
    var after=0; ex.forEach(function(e){ if(b.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING) after++; });
    if(after>0) out.push([s.id, b.textContent.trim(), oc.slice(0,30), after, !!b.closest('.sticky-bank')]);
  });
 });
 return out;})()"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1440,'height':900})
    pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    tot=0
    for f in sys.argv[1:]:
        pg.goto('file://'+f); pg.wait_for_timeout(500)
        r=pg.evaluate(JS); seen=set(); 
        print('==',f.split('/')[-2], len(r))
        for x in r:
            if x[0] in seen: continue
            seen.add(x[0]); print('  ',x)
        tot+=len(seen)
    print('slides with Check BEFORE exercises:',tot)
