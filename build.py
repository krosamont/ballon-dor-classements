import re, json, os, pandas as pd
from urllib.parse import unquote
df=pd.read_pickle('raw.pkl'); c=json.load(open('pos_cache.json'))
photos=json.load(open('photo_cache.json')) if os.path.exists('photo_cache.json') else {}
def slug(s): return re.sub(r'[^\w]+','_',s).strip('_')
def clean(w):
    w=re.sub(r'<ref[^>]*/>|<ref.*?</ref>|<!--.*?-->','',w,flags=re.S)
    w=re.sub(r'\{\{(?:hlist|plainlist|flatlist|unbulleted list|ubl)\s*\|','',w,flags=re.I)
    w=re.sub(r'\{\{[^{}]*\}\}','',w); w=w.replace('}}','')
    w=re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]',r'\1',w)
    out=[]
    for p in re.split(r'\n\*|\||,|/|<br\s*/?>|\n',w):
        p=re.sub(r"'''?|<[^>]+>",'',p).strip(' *\n')
        if p and p.lower() not in [o.lower() for o in out]: out.append(p[0].upper()+p[1:])
    return out
# Postes anglais: Goalkeeper, Defender, Defensive midfielder, Midfielder, Attacking midfielder, Winger, Forward
def pos(p):
    l=p.lower()
    if 'goalkeeper' in l: return 'Goalkeeper'
    if 'attacking midfield' in l or 'playmaker' in l or 'trequartista' in l or 'second striker' in l and False: return 'Attacking midfielder'
    if 'defensive midfield' in l or 'holding' in l or 'regista' in l or 'anchor' in l: return 'Defensive midfielder'
    if 'midfield' in l: return 'Midfielder'
    if any(k in l for k in ('back','defender','sweeper','libero')): return 'Defender'
    if 'wing' in l: return 'Winger'
    if any(k in l for k in ('forward','striker','attacker')): return 'Forward'
GRP={'Goalkeeper':'G','Defender':'D','Defensive midfielder':'M','Midfielder':'M','Attacking midfielder':'M','Winger':'F','Forward':'F'}
TAB={'goalkeeper':'G','defender':'D','midfielder':'M','forward':'F'}
rows=[]
for _,r in df.iterrows():
    d=r.to_dict(); t=unquote(r.wiki).replace('_',' ') if r.wiki else ''
    det=clean(c.get(t,'')) if r.wiki else []
    if r.player=='Petr Čech': det=['Goalkeeper']
    cand=[pos(p) for p in det if pos(p)]
    tg=TAB.get(r.position_table.lower())
    p=next((x for x in cand if tg and GRP[x]==tg),None) or (cand[0] if cand else None)
    if not p and tg: p={'G':'Goalkeeper','D':'Defender','M':'Midfielder','F':'Forward'}[tg]
    d['position']=p; d['position_detail']=' / '.join(det)
    d['nationality']=r.nationality or r.flag_country
    d['photo_url']=photos.get(t,''); d['photo_file']=f"images/players/{slug(t)}.jpg" if os.path.exists(f"images/players/{slug(t)}.jpg") else ''
    d['flag_file']=f"images/flags/{slug(r.flag_country)}.png" if os.path.exists(f"images/flags/{slug(r.flag_country)}.png") else ''
    d['url']='https://en.wikipedia.org/wiki/'+r.wiki if r.wiki else ''
    rows.append(d)
o=pd.DataFrame(rows)
o['competition']=o.competition.replace({"Rankings":"Ballon d'Or","Voted players":"Ballon d'Or","Striker of the Year":'Gerd Müller Trophy'})
o['rank']=o['rank'].str.replace(r'(?<=\d)(st|nd|rd|th)\b','',regex=True)
num=pd.to_numeric(o['rank'].str.extract(r'(\d+)')[0])
o['position_rank']=num.groupby([o.year,o.competition,o.sex,o.position]).rank(method='min').astype('Int64')
o['position_count']=o.groupby(['year','competition','sex','position'])['player'].transform('size')
cols=['year','competition','sex','rank','position','position_rank','position_count','player','nationality','club','position_detail','score','score_type','photo_file','flag_file','photo_url','flag_url','url']
o=o[cols]
print(o.position.isna().sum(),'sans position'); print(o.position.value_counts().to_string())
print((o.photo_file=='').sum(),'lignes sans photo locale',(o.flag_file=='').sum(),'sans drapeau local')
o.to_csv('ballon_dor_classements_1976_2026.csv',index=False,encoding='utf-8-sig')
