"""Probability the policy itself gave to a choice class at the states it met in training, by stretch of decisions (CPU)."""
import glob, gzip, json, re, sys
from collections import defaultdict
sys.path.insert(0, 'tools/exp')
from summarize import choice_class
WATCH = {('pilot:stone', 'stairs', ('explore', 'stairs')): 'stone: stairs', ('pilot:logs', 'toward', ('explore', 'toward')): 'logs: toward'}
LIMIT = int(sys.argv[1])
for arm in sys.argv[2:]:
    files = sorted(glob.glob(f'artifacts/exp/{arm}/train-*.jsonl.gz'), key=lambda f: int(re.search(r'train-t0-(\d+)-', f).group(1)))
    acc = defaultdict(lambda: [0., 0., 0]); count = 0; shape = None
    for f in files:
        goal = cands = None
        with gzip.open(f, 'rt') as h:
            for line in h:
                kind = line[10:line.index('"', 10)]
                if kind == 'goal': goal = json.loads(line)['data']
                elif kind == 'candidates': cands = json.loads(line)['data']
                elif kind == 'selection' and cands and cands['candidates']:
                    sel = json.loads(line)['data']; count += 1
                    if count > LIMIT: break
                    probs = sel['probabilities']; shape = shape or type(probs).__name__
                    ids = [c['candidate_id'] for c in cands['candidates']]
                    p = [probs.get(i, 0.) for i in ids] if isinstance(probs, dict) else probs
                    mask = cands.get('mask') or [True] * len(ids)
                    cls = [choice_class(c) for c in cands['candidates']]
                    present = {c for c, m in zip(cls, mask) if m}
                    for (g, target, need), label in WATCH.items():
                        if goal['goal_id'] == g and set(need) <= present and present <= set(need) | {'toward'}:
                            a = acc[(label, min((count - 1) // 512, 2) if LIMIT <= 1536 else (count - 1) // 512)]
                            a[0] += sum(x for x, c, m in zip(p, cls, mask) if m and c == target)
                            a[1] += sum(1 for c, m in zip(cls, mask) if m and c == target) / sum(mask); a[2] += 1
        if count > LIMIT: break
    print(arm, 'decisions', min(count, LIMIT), 'probabilities as', shape)
    for (label, bucket), (p, u, n) in sorted(acc.items()):
        print(f'   {label:14s} decisions {bucket*512:4d}+ n={n:3d} policy {p/n:.3f} uniform {u/n:.3f} ratio {p/u:.2f}')
