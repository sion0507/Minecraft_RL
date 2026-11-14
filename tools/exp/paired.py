import json, random, statistics as st, math
from math import comb
A='artifacts/exp/'
def eps(d, phase):
    return {r['seed']: r for r in json.load(open(A+d+'/summary.json'))['episodes'] if r['phase']==phase and r['valid']}
arms = {'U': {**eps('T-train-stone_pick','before'), **eps('U-eval-stone_pick-s11-30','before')},
        'T': {**eps('T-train-stone_pick','after'), **eps('T-eval-stone_pick-s11-30','before')},
        'D3': {**eps('D3-train-stone_pick','after'), **eps('D3-eval-stone_pick-s11-30','before')},
        'T2': {**eps('T2-train-stone_pick','after'), **eps('T2-eval-stone_pick-s11-30','before')}}
tk = lambda r: r['active_ticks'] if r['success'] else 3600
seeds = sorted(arms['U']); print(len(seeds), [len(a) for a in arms.values()], seeds[0], seeds[-1])
def phases(r):
    out, prev = {}, 0
    for s in r['subgoals']:
        if s['completed']: out[s['goal']] = s['end_tick']-prev; prev = s['end_tick']
    return out
for n,a in arms.items():
    t=[tk(a[s]) for s in seeds]
    ph={g: st.mean(phases(a[s]).get(g,0) for s in seeds if a[s]['success']) for g in ['pilot:logs','pilot:pick','pilot:stone','pilot:stone_pick']}
    print(n, 'succ', sum(a[s]['success'] for s in seeds), 'mean %.0f median %.0f'%(st.mean(t), st.median(t)), 'first10 %.0f new20 %.0f'%(st.mean(t[:10]), st.mean(t[10:])), {g[6:]: round(v) for g,v in ph.items()}, 'dec/ep %.1f'%st.mean(a[s]['decisions'] for s in seeds))
def pair(x, y, sel=seeds):
    d=[tk(arms[x][s])-tk(arms[y][s]) for s in sel]; n=len(d)
    random.seed(0); bs=sorted(st.mean(random.choices(d,k=n)) for _ in range(10000))
    neg=sum(v<0 for v in d); pos=sum(v>0 for v in d); m=neg+pos
    p=min(1, 2*sum(comb(m,k) for k in range(0,min(neg,pos)+1))/2**m)
    print(f'{x}-{y} n={n} mean {st.mean(d):.0f} ({100*st.mean(d)/st.mean(tk(arms[y][s]) for s in sel):.1f}%) se {st.stdev(d)/math.sqrt(n):.0f} boot95 [{bs[250]:.0f},{bs[9750]:.0f}] faster {neg} slower {pos} tie {n-m} sign p={p:.3f}')
pair('D3','U'); pair('T','U'); pair('T2','U'); pair('T2','D3'); pair('T2','T'); pair('T2','U',seeds[:10]); pair('T2','U',seeds[10:]); pair('T','D3'); pair('D3','U',seeds[10:]); pair('D3','U',seeds[:10]); pair('T','D3',seeds[:10]); pair('T','D3',seeds[10:])
for n,a in arms.items(): print(n, [ (s, a[s]['reason'], a[s]['active_ticks']) for s in seeds if not a[s]['success']])
print('slot U T D3 T2'); 
for s in seeds: print(s, tk(arms['U'][s]), tk(arms['T'][s]), tk(arms['D3'][s]), tk(arms['T2'][s]))
