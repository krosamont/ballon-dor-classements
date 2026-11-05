from urllib.parse import unquote
import re, json, os, time, requests, pandas as pd
from bs4 import BeautifulSoup as B
from scrape import page, H

def txt(c):
    for s in c.find_all(['sup','style']): s.decompose()
    return re.sub(r'\s+',' ',c.get_text(' ',strip=True)).replace(' ,',',').strip()

def grid(t):
    rows=[];span={}
    for tr in t.find_all('tr'):
        row=[];ci=0;cells=tr.find_all(['th','td'],recursive=False)
        it=iter(cells)
        while True:
            while ci in span and span[ci][0]>0:
                n,c=span[ci];row.append(c);span[ci]=(n-1,c);ci+=1
            c=next(it,None)
            if c is None: break
            rs=int(re.sub(r'\D','',c.get('rowspan','1')) or 1);cs=int(re.sub(r'\D','',c.get('colspan','1')) or 1)
            for _ in range(cs):
                row.append(c)
                if rs>1: span[ci]=(rs-1,c)
                ci+=1
        while ci in span and span[ci][0]>0:
            n,c=span[ci];row.append(c);span[ci]=(n-1,c);ci+=1
        rows.append(row)
    return rows

def link(c):
    for a in c.find_all('a',href=True):
        h=a['href']
        if h.startswith('/wiki/') and ':' not in h[6:] and 'cite_note' not in h and a.get_text(strip=True): return re.sub(r'#.*','',h[6:])
    return None

SCORE={'points':'Points','pts':'Points','percent':'Percent','goals':'Goals','votes':'Votes','total':'Points'}
def norm_h(h):
    h=re.sub(r'\[.*?\]','',h).strip().lower()
    return h
def flag(*cells):
    for c in cells:
        if c is None: continue
        for im in c.find_all('img'):
            m=re.search(r'(//[^"\s]*?)/thumb/(.*?/(Flag_of_[^/]+))/\d+px-',im.get('src',''))
            if m:
                name=re.sub(r'^the ','',re.sub(r'\s*\(.*?\)','',unquote(re.sub(r'\.svg|\.png','',m.group(3))[8:]).replace('_',' ')).strip())
                return name,'https://upload.wikimedia.org/wikipedia/'+m.group(2).split('/Flag_of')[0]+'/Flag_of'+m.group(2).split('/Flag_of',1)[1] if False else 'https://upload.wikimedia.org'+m.group(1).split('wikimedia.org',1)[1]+'/thumb/'+m.group(2)+'/120px-'+m.group(3)+('.png' if m.group(3).endswith('.svg') else '')
    return '',''
out=[]
for y in list(range(1976,2020))+list(range(2021,2027)):
    s=B(page(y),'lxml')
    seen={}
    for t in s.select('table.wikitable'):
        g=grid(t)
        if not g: continue
        hdr=[norm_h(txt(B(str(c),'lxml'))) for c in g[0]]
        if 'rank' not in hdr or not any(h in('player','name') for h in hdr): continue
        hd=t.find_previous(['h2','h3']); head=txt(hd).replace('[edit]','').strip()
        cap=t.find('caption'); 
        seen[head]=seen.get(head,0)+1
        low=head.lower()
        women = ('féminin' in low or 'women' in low)
        if 'gerd' in low and seen[head]==2: women=True
        base=re.sub(r"^(men's|women's)\s+",'',head,flags=re.I)
        if 'ballon' in base.lower() and 'féminin' in base.lower(): base="Ballon d'Or"
        cat=base
        sex='Women' if women else 'Men'
        idx={h:i for i,h in enumerate(hdr)}
        def col(*names):
            for n in names:
                if n in idx: return idx[n]
        ip,ir=idx.get('player',idx.get('name')),idx['rank']
        inat=col('nationality','national team'); ipos=col('position'); icl=col('club(s)','club','team')
        isc=col('points','percent','goals','total','votes'); sct=hdr[isc] if isc is not None else None
        for r in g[1:]:
            if len(r)<=max(ip,ir) or r[ip].name=='th' and not r[ip].find('a'): continue
            name=txt(B(str(r[ip]),'lxml'))
            if not name: continue
            get=lambda i: txt(B(str(r[i]),'lxml')) if i is not None and i<len(r) else ''
            out.append(dict(year=y,competition=cat,sex=sex,rank=get(ir),player=name,wiki=link(r[ip]),
              nationality=get(inat),club=get(icl),position_table=get(ipos),
              flag_country=flag(r[inat] if inat is not None and inat<len(r) else None, r[ip])[0],flag_url=flag(r[inat] if inat is not None and inat<len(r) else None, r[ip])[1],score=get(isc),score_type=SCORE.get(sct,sct) if sct else ''))
df=pd.DataFrame(out); df.to_pickle('raw.pkl')
print(df.groupby(['year','competition','sex']).size().to_string())
print(df.wiki.isna().sum(),df.wiki.nunique())
