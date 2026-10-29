"""Descriptive audit for synthetic interview attachments; no causal claims."""
import csv
import json
from pathlib import Path
BASE = Path(__file__).resolve().parent

def rows(name):
    with (BASE / name).open() as file:
        return list(csv.DictReader(file))

def main():
    metrics=rows('tool_metrics.csv')
    groups={v:{r['bucket']:(int(r['correct']),int(r['total'])) for r in metrics if r['version']==v} for v in ['baseline','new']}
    base_n=sum(n for c,n in groups['baseline'].values())
    result={}
    for v,buckets in groups.items():
        result[v]={'raw':sum(c for c,n in buckets.values())/sum(n for c,n in buckets.values()), 'fixed_mix':sum(groups['baseline'][k][1]/base_n*c/n for k,(c,n) in buckets.items())}
    assert abs(result['baseline']['raw']-.58)<1e-9
    assert abs(result['new']['raw']-.77)<1e-9
    assert abs(result['new']['fixed_mix']-.53)<1e-9
    judges=rows('judge_swaps.csv')
    counts=dict(stable_a=0,stable_b=0,stable_tie=0,inconsistent=0)
    score=first=non_tie=0
    for r in judges:
        ab={'first':'A','second':'B','tie':'tie'}[r['ab']]
        ba={'first':'B','second':'A','tie':'tie'}[r['ba']]
        counts[{'A':'stable_a','B':'stable_b','tie':'stable_tie'}[ab] if ab==ba else 'inconsistent']+=1
        score+=sum({'A':1,'B':0,'tie':.5}[a] for a in (ab,ba))
        for value in (r['ab'],r['ba']):
            non_tie+=value!='tie'; first+=value=='first'
    counts.update(swap_score=score/(2*len(judges)),first_rate=first/non_tie)
    assert counts['inconsistent']==3 and counts['stable_tie']==1
    print(json.dumps({'tool_metrics':result,'judge_swaps':counts,'reward_sweep':rows('reward_sweep.csv'),'limits':'Synthetic purposive samples; no population prevalence, paired significance or causal attribution.'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
