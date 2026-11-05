"""Récupère la photo principale (infobox) de chaque joueur + télécharge photos et drapeaux."""
import json, os, re, time, requests, pandas as pd
from urllib.parse import unquote
H={"User-Agent":"research-script/1.0 (ballon d'or dataset)"}
df=pd.read_pickle('raw.pkl')
titles=sorted({unquote(t).replace('_',' ') for t in df.wiki.dropna()})
cache=json.load(open('photo_cache.json')) if os.path.exists('photo_cache.json') else {}
todo=[t for t in titles if t not in cache]
for i in range(0,len(todo),50):
    b=todo[i:i+50]
    for k in range(6):
        r=requests.get("https://en.wikipedia.org/w/api.php",params=dict(action="query",prop="pageimages",piprop="thumbnail",pithumbsize=300,titles="|".join(b),redirects=1,format="json",formatversion=2),headers=H)
        try: q=r.json()['query']; break
        except Exception: time.sleep(5*(k+1))
    alias={x['from']:x['to'] for x in q.get('normalized',[])+q.get('redirects',[])}
    pages={p['title']:p for p in q['pages']}
    for t in b:
        n=t
        while n in alias: n=alias[n]
        cache[t]=pages.get(n,{}).get('thumbnail',{}).get('source','')
    json.dump(cache,open('photo_cache.json','w')); time.sleep(2); print(i,len(todo),flush=True)

def dl(url,path):
    if not url or os.path.exists(path): return
    for k in range(6):
        try: r=requests.get(url,headers=H,timeout=30)
        except requests.RequestException as e: print('err',path,type(e).__name__,flush=True); time.sleep(10*(k+1)); continue
        if r.status_code==200: open(path,'wb').write(r.content); break
        time.sleep(int(r.headers.get('Retry-After',3*(k+1)))); print('retry',r.status_code,path,flush=True)
    time.sleep(1.0)
def slug(s): return re.sub(r'[^\w]+','_',s).strip('_')
os.makedirs('images/players',exist_ok=True); os.makedirs('images/flags',exist_ok=True)
for t,u in cache.items():
    if u: dl(u,f"images/players/{slug(t)}.jpg")
for c,u in df[['flag_country','flag_url']].drop_duplicates().itertuples(index=False):
    dl(u,f"images/flags/{slug(c)}.png")
print(len(os.listdir('images/players')),'photos',len(os.listdir('images/flags')),'drapeaux')
