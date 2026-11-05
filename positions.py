import re, json, os, time, requests, pandas as pd
from urllib.parse import unquote
H={"User-Agent":"research-script/1.0"}
df=pd.read_pickle('raw.pkl')
titles=sorted(set(df.wiki.dropna()))
titles=[unquote(t).replace('_',' ') for t in titles]
cache=json.load(open('pos_cache.json')) if os.path.exists('pos_cache.json') else {}
todo=[t for t in titles if t not in cache]
for i in range(0,len(todo),50):
    b=todo[i:i+50]
    for k in range(6):
        r=requests.get("https://en.wikipedia.org/w/api.php",params=dict(action="query",prop="revisions",rvprop="content",rvslots="main",titles="|".join(b),redirects=1,format="json",formatversion=2),headers=H)
        try: j=r.json(); break
        except Exception: time.sleep(5*(k+1))
    q=j['query']; alias={}
    for x in q.get('normalized',[])+q.get('redirects',[]): alias[x['from']]=x['to']
    pages={p['title']:p for p in q['pages']}
    for t in b:
        n=t
        while n in alias: n=alias[n]
        p=pages.get(n); w=p['revisions'][0]['slots']['main']['content'] if p and 'revisions' in p else ''
        m=re.search(r'\|\s*position\s*=\s*(.*?)(?=\n\s*\|\s*\w[\w\s]*=|\n\}\})',w,re.S|re.I)
        cache[t]=m.group(1).strip() if m else ''
    time.sleep(2); print(i,len(todo),flush=True)
    json.dump(cache,open('pos_cache.json','w'))
