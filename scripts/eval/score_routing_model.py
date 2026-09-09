import json,sys
c=json.load(open('evals/corpus/eval-corpus.json'))
exp={r['id']:r['expected_skill'] for r in c['routing']}; neg={n['id'] for n in c['negatives']}
def score(path):
    d=json.load(open(path)); lab={l['id']:l['skill'] for l in d['labels']}
    fired=sum(1 for i in exp if lab.get(i)); exact=sum(1 for i,e in exp.items() if lab.get(i)==e)
    negfire=sum(1 for i in neg if lab.get(i))
    return d['arm'], fired, exact, negfire, len(exp), len(neg)
for p in sys.argv[1:]:
    arm,f,e,n,R,N=score(p)
    print(f"{arm:12s} fired on OCI prompts {f}/{R} ({100*f/R:.0f}%) | exact expected skill {e}/{R} ({100*e/R:.0f}%) | fired on negatives {n}/{N}")
