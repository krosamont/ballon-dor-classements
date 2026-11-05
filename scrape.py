import time, requests, json, re, os
from bs4 import BeautifulSoup as B
H={"User-Agent":"research-script/1.0"}
os.makedirs("cache",exist_ok=True)
def page(y):
    f=f"cache/{y}.html"
    if os.path.exists(f): return open(f).read()
    h=''
    for k in range(5):
        resp=requests.get("https://en.wikipedia.org/w/api.php",params=dict(action="parse",page=f"{y} Ballon d'Or",prop="text",redirects=1,format="json",formatversion=2),headers=H)
        try: h=resp.json().get('parse',{}).get('text',''); break
        except Exception: print(y,resp.status_code,resp.text[:100]); time.sleep(5*(k+1))
    time.sleep(1)
    open(f,'w').write(h); return h
if __name__=="__main__":
    for y in range(2006,2027):
        s=B(page(y),'lxml')
        print(y)
        for i,t in enumerate(s.select('table.wikitable')):
            ths=[th.get_text(' ',strip=True) for th in t.find_all('tr')[0].find_all(['th','td'])]
            cap=t.find_previous(['h2','h3']).get_text(' ',strip=True)
            print('  ',i,cap[:30],'|',ths,len(t.find_all('tr')))
