"""Timestamp-only eligibility screen; never export IDs or precise dates/positions."""
import argparse,csv,hashlib,json
from collections import defaultdict,Counter
from datetime import datetime
from pathlib import Path

def screen(rows,animal_field='BirdID',time_field='timestamp'):
    days=defaultdict(set); rows_by_month=Counter(); animals=set(); rejected=0
    for r in rows:
        animal=(r.get(animal_field) or '').strip()
        try:t=datetime.fromisoformat((r.get(time_field) or '').strip().replace('Z','+00:00'))
        except (ValueError,TypeError):rejected+=1;continue
        if not animal:rejected+=1;continue
        days[(t.year,t.month,animal)].add(t.date())
        rows_by_month[(t.year,t.month)]+=1;animals.add(animal)
    monthly=[]; years=sorted({y for y,m in rows_by_month})
    for y,m in sorted(rows_by_month):
        counts=[len(ds) for (yy,mm,a),ds in days.items() if (y,m)==(yy,mm)]
        monthly.append({'year':y,'month':m,'rows':rows_by_month[y,m], 'animals':len(counts),'animals_at_least_seven_dates':sum(n>=7 for n in counts)})
    gates=[]
    for y in years:
        eligible={a for (yy,m,a),ds in days.items() if yy==y and m==2 and len(ds)>=7 and len(days.get((y,4,a),set()))>=7}
        common={m:len(set.intersection(*(days[(y,m,a)] for a in eligible))) if eligible else 0 for m in (2,4)}
        if not rows_by_month[y,2]:status='STOP_NO_FEBRUARY_OBSERVATIONS'
        elif len(eligible)<4:status='STOP_FEWER_THAN_FOUR_PAIRED_ANIMALS'
        elif min(common.values())<7:status='NEEDS_INDEPENDENT_SITE_COHORT_SELECTION'
        else:status='TIME_SUPPORT_PASSES_ONLY_NOT_SOURCE_OR_POPULATION_VALIDATION'
        gates.append({'year':y,'paired_animals_at_least_seven_dates_per_month':len(eligible),'common_dates_february':common[2],'common_dates_april':common[4],'status':status})
    return {'accepted_timestamp_rows':sum(rows_by_month.values()),'unusable_timestamp_or_id_rows':rejected,'source_animal_labels':len(animals),'monthly_support':monthly,'primary_time_gate':gates,'spatial_outcomes_computed':False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--sha256',required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--source-url',required=True)
    args=p.parse_args();raw=args.input.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=args.sha256:raise ValueError('Source bytes do not match pinned SHA256')
    with args.input.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f);columns=reader.fieldnames;result=screen(reader)
    result.update({'source_url':args.source_url,'source_sha256':args.sha256,'source_bytes':len(raw),'columns':columns})
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'rows':result['accepted_timestamp_rows'],'animals':result['source_animal_labels'],'time_gate':result['primary_time_gate'],'spatial_outcomes_computed':False}))

if __name__=='__main__':main()
