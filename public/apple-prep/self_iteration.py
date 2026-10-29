"""Toy verified self-iteration, CPU only. Not an LLM or multimodal result.
Student proposes rounded arithmetic predictions plus bounded search offsets.
Only exact verified proposals become new training targets. Development selects
rounds; a disjoint final test is read once after stopping. No network required.
"""
import json
import torch

def features(pairs):
    return torch.tensor([[a/20,b/20,1.] for a,b in pairs],dtype=torch.float32)

def fit(model, pairs, targets, steps=120):
    optimizer=torch.optim.SGD(model.parameters(),lr=.3)
    x=features(pairs); y=torch.tensor(targets,dtype=torch.float32)/40
    model.train()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss=((model(x).squeeze(-1)-y)**2).mean()
        loss.backward(); optimizer.step()

def evaluate(model,pairs):
    model.eval()
    with torch.no_grad():
        pred=model(features(pairs)).squeeze(-1)*40
        target=torch.tensor([a+b for a,b in pairs],dtype=torch.float32)
        return {'mae':(pred-target).abs().mean().item(),'rounded_accuracy':(pred.round()==target).float().mean().item()}

def main():
    torch.set_num_threads(1)
    with torch.random.fork_rng(devices=[]):
        model=torch.nn.Linear(3,1,bias=False)
    with torch.no_grad(): model.weight.zero_()
    # Initial verified seed data. Task pairs are disjoint across train/dev/test.
    train=[(a,b) for a in range(0,5) for b in range(0,5)]
    targets=[a+b for a,b in train]
    dev=[(a,b) for a in range(10,15) for b in range(0,5)]
    final=[(a,b) for a in range(15,20) for b in range(10,15)]
    pool=[(a,b) for a in range(5,20) for b in range(5,10)]
    assert not(set(train)&set(dev) or set(pool)&set(dev) or set(final)&(set(train)|set(pool)|set(dev)))
    fit(model,train,targets)
    best=evaluate(model,dev)['mae']
    best_state={k:v.clone() for k,v in model.state_dict().items()}
    report=[{'round':0,'train_n':len(train),'development':evaluate(model,dev)}]
    stop_reason='round_budget'
    used=set(train)
    for round_id in range(1,4):
        model.eval()
        round_pool=[pair for pair in pool if 5*round_id<=pair[0]<5*(round_id+1)]
        with torch.no_grad(): proposed=(model(features(round_pool)).squeeze(-1)*40).round().int().tolist()
        accepted=[]; checks=0
        for pair,pred in zip(round_pool,proposed):
            if pair in used: continue
            # Independent exact environment supplies validation, never fake labels.
            for offset in [0]+[value for step in range(1,9) for value in (-step,step)]:
                checks+=1; candidate=pred+offset
                if candidate==sum(pair):
                    accepted.append((pair,candidate)); break
        assert all(value==sum(pair) for pair,value in accepted)
        if not accepted:
            stop_reason='no_verified_novel_data'
            report.append({'round':round_id,'checked':checks,'accepted':0,'stop':stop_reason})
            break
        train.extend(pair for pair,value in accepted); targets.extend(value for pair,value in accepted)
        used.update(pair for pair,value in accepted)
        fit(model,train,targets)
        dev_metrics=evaluate(model,dev)
        report.append({'round':round_id,'checked':checks,'accepted':len(accepted),'train_n':len(train),'development':dev_metrics})
        if dev_metrics['mae']>=best-1e-5:
            stop_reason='no_development_gain'
            report[-1]['stop']=stop_reason; break
        best=dev_metrics['mae']; best_state={k:v.clone() for k,v in model.state_dict().items()}
    model.load_state_dict(best_state)
    final_metrics=evaluate(model,final)  # first and only final-test evaluation
    assert all(torch.isfinite(value).all() for value in model.parameters())
    print(json.dumps({'rounds':report,'stop_reason':stop_reason,'final_test':final_metrics,'limits':'Linear arithmetic surrogate, exact external verifier; no claim of LLM self-improvement or guaranteed round gains.'},indent=2))

if __name__=='__main__': main()
