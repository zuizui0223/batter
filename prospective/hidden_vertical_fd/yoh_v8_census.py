"""V8 audit of single-height Borneo bat source; no biological fitting."""
import collections as C, json, hashlib, io, urllib.request, math, zipfile
from pathlib import Path
from openpyxl import load_workbook
def get(url,cap):
    req=urllib.request.Request(url,headers={'User-Agent':'batter-public-source-audit/1.0'})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read(cap+1)
    if len(b)>cap:raise ValueError('size gate')
    return b
def norm(x):return ' '.join(str(x if x is not None else '').strip().split())
def main():
    out={}
    try:
        meta=json.loads(get('https://zenodo.org/api/records/7740421',2097152))
        f=next(x for x in meta['files'] if x['key']=='SAFE_data_archive_Yoh2.xlsx')
        b=get(f['links']['self'],8911914)
        assert len(b)==8911914 and hashlib.sha256(b).hexdigest()=='0c874b45b265d326c9cff12db30f96fa6cbf5f19cbfe24530a64bc72fcf25da2'
        a,h=f['checksum'].split(':');assert hashlib.new(a,b).hexdigest()==h
        with zipfile.ZipFile(io.BytesIO(b)) as z:assert z.testzip() is None and sum(x.file_size for x in z.infolist())<=384*1024**2
        w=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
        s=w['MasterData'];meta=list(s.iter_rows(min_row=1,max_row=10,values_only=True))
        assert norm(meta[9][0]).lower()=='field_name' and norm(meta[1][0]).lower()=='description'
        out['header']=[norm(x) for x in meta[9]];out['source_descriptions']=[norm(x) for x in meta[1]]
        assert 'final' in norm(meta[1][8]).lower() and 'habitat' in norm(meta[1][9]).lower() and 'height' in norm(meta[1][11]).lower()
        taxa=[{'name':norm(x[0]),'taxon_name':norm(x[1]),'type':norm(x[2])} for x in w['Taxa'].iter_rows(min_row=2,values_only=True) if x[0] is not None]
        out['author_taxa']=taxa
        site=C.defaultdict(C.Counter);dates=C.defaultdict(set);hab=C.defaultdict(set);structures=C.defaultdict(set);all_rows=0;labels=C.Counter();by_hab=C.defaultdict(C.Counter);bad=C.Counter();loc=C.defaultdict(set)
        for r in w['Locations'].iter_rows(min_row=2,values_only=True):
            if r[0] is None:continue
            try:
                lat,lon=float(r[2]),float(r[3])
                assert 0<lat<10 and 110<lon<125
                loc[norm(r[0]).casefold()].add((lon,lat))
            except (ValueError,TypeError,AssertionError):bad['invalid_coordinate']+=1
        for r in s.iter_rows(min_row=11,values_only=True):
            if all(x is None for x in r):continue
            all_rows+=1;k=norm(r[1]).casefold();final=norm(r[8]) or '<blank>';ht=norm(r[9]) or '<blank>'
            labels[final]+=1;by_hab[ht][final]+=1
            if not k:bad['missing_location']+=1;continue
            site[k][final]+=1;hab[k].add(ht)
            if r[2] is not None:dates[k].add(str(r[2]))
            vals=[]
            for x in r[10:14]:
                try:
                    y=float(x);vals.append(y if math.isfinite(y) else None)
                except (TypeError,ValueError):vals.append(None)
            structures[k].add(tuple(vals))
        out['rows']=all_rows;out['final_labels']=dict(labels);out['label_by_habitat']={k:dict(v) for k,v in by_hab.items()}
        out['site_support']={'n':len(site),'location_keys':len(loc),'exact_unique_coordinate':sum(len(loc[k])==1 for k in site),'record_date_count_distribution':dict(C.Counter(len(dates[k]) for k in site)),'multiple_habitat_sites':sum(len(hab[k])!=1 for k in site),'multiple_structure_vectors':sum(len(structures[k])!=1 for k in site),'single_complete_structure_vector':sum(len(structures[k])==1 and None not in next(iter(structures[k])) for k in site),'sites_by_single_habitat':dict(C.Counter(next(iter(v)) for v in hab.values() if len(v)==1))}
        out['bad']=dict(bad);out['status']='census_complete';w.close()
    except Exception as e:out.update(status='stopped',error=type(e).__name__+': '+str(e)[:240])
    Path('yoh_v8_census.json').write_text(json.dumps(out,indent=2,ensure_ascii=False));print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
