import sys, os
BASE = (sys.argv[1] if len(sys.argv)>1 else os.path.expanduser('~/Desktop/Conversational-English')).rstrip('/') + '/'
import re
from bs4 import BeautifulSoup
EXC=('circ-opt','wb-blank','pr-s','ex-row','gsel','ans-input','qline','qcard','mp-item','sent','tf-row','cls-item','cs-item','dk-card','read-box')
def exlike(e):
    n=getattr(e,'name',None)
    if not n: return False
    if n in('input','select','textarea'): return True
    c=e.get('class') or []
    return any(x in EXC for x in c)
for f in ['Empower-B2-2A','AEF4-5A','Empower-A1-1A','Empower-A1-0-Welcome']:
    sp=BeautifulSoup(open(BASE+f+'/index.html',encoding='utf-8').read(),'html.parser')
    for sc in sp.select('script,style'): sc.decompose()
    for s in sp.select('.slide'):
        body=s.select_one('.content') or s
        els=[e for e in body.descendants if getattr(e,'name',None)]
        for i,e in enumerate(els):
            if e.name!='button': continue
            oc=e.get('onclick','') or ''; tx=e.get_text(' ',strip=True)
            if not (re.search(r'(^|[^a-z])check[A-Za-z]*\(|showKeys|toggleSuggested|mpCheck|prCheck',oc) ): continue
            if e.find_parent('button'): continue
            after=[x for x in els[i+1:] if exlike(x) and not x.find_parent('button') and not x.find_parent(class_=['sticky-bank','keybox'])]
            # exclude things inside the button's own key box
            kb=None
            if after: print(f,s.get('id'),'| BUTTON before %d exercise elements |'%len(after),tx[:40],'|',oc[:30])
