"""Per choice class at multi-class states: MC return (the critic target) and return minus the run's value, by arm."""
import glob, gzip, json, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, 'tools/exp')
from summarize import choice_class
from critic_inputs import returns
def rows(trace):
    out, goal, saved, sel = [], None, None, None
    with gzip.open(trace, 'rt') as h:
        for line in h:
            kind = line[10:line.index('"', 10)]
            if kind == 'goal': goal = json.loads(line)['data']
            elif kind == 'candidates': saved = json.loads(line)['data']
            elif kind == 'selection': sel = json.loads(line)['data']
            elif kind == 'reward' and goal and saved and sel and saved['candidates']:
                out.append({'goal': goal, 'saved': saved, 'selection': sel, 'reward': json.loads(line)['data']}); saved = sel = None
    return out
for arm in sys.argv[1:]:
    acc = defaultdict(lambda: defaultdict(list)); once = True
    for trace in sorted(glob.glob(f'artifacts/exp/{arm}/train-*.jsonl.gz')):
        rs = rows(trace)
        for r, g in zip(rs, returns(rs)):
            if once: print(arm, 'selection keys', list(r['selection']), 'reward keys', list(r['reward'])); once = False
            if g is None: continue
            cands = r['saved']['candidates']; mask = r['saved'].get('mask') or [True]*len(cands)
            classes = sorted({choice_class(c) for c, m in zip(cands, mask) if m})
            if len(classes) < 2: continue
            chosen = next(c for c in cands if c['candidate_id'] == r['selection'].get('candidate_id', r['selection'].get('selected_id')))
            acc[(r['goal']['goal_id'], '+'.join(classes))][choice_class(chosen)].append((g, g - r['selection']['values']['local']))
    for key, by in sorted(acc.items(), key=lambda kv: -sum(map(len, kv[1].values()))):
        n = sum(map(len, by.values()))
        if n < 60: continue
        print(f'{arm} {key[0]} [{key[1]}] n={n}')
        for cls, v in sorted(by.items()):
            g = [a for a, _ in v]; d = [b for _, b in v]
            print(f'   {cls:9s} n={len(v):4d} return {st.mean(g):+.3f} sd {st.pstdev(g):.3f} | return-value {st.mean(d):+.3f} sd {st.pstdev(d):.3f}')
