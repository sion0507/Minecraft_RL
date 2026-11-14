#!/bin/bash
# After arm D: (1) fixed-state probe of the T and D heads, (2) 20 more evaluation slots (seeds 15010-15029) for the
# untrained and the T heads, (3) the held-out iron task for the untrained and the T heads. One game server at a time.
cd /home/sion/Documents/projects/RL_projects/Minecraft_learning-exp || exit 1
export PYTHONPATH=$PWD/src PATH=/home/sion/Documents/projects/RL_projects/Minecraft_learning/.venv/bin:$PATH
while kill -0 "$1" 2>/dev/null; do sleep 30; done
sleep 30
T=artifacts/exp/T-train-stone_pick D=artifacts/exp/D-train-stone_pick
stamp() { echo "$(date +%FT%T%:z) $*"; }
stamp "commit $(git rev-parse --short HEAD) dirty: $(git status --porcelain -- src configs bridge | wc -l)"

stamp "probe start"
heads=""
for f in $T/initial $T/update-04 $T/update-08 $T/update-12 $T/update-16 $T/update-20 $T/final $D/update-04 $D/update-08 $D/update-12 $D/final; do
  [ -s $f.safetensors ] && heads="$heads $f.safetensors"
done
python tools/exp/fixed_probe.py --traces "$T/before-*.jsonl.gz" --heads $heads --output artifacts/exp/probe-fixed-before.json 2> artifacts/exp/probe-fixed-before.stderr
stamp "probe end $?"

run() {
  name=$1; shift
  stamp "$name start"
  python -m mc_diamond.exp "$@" --output artifacts/exp/$name 2> artifacts/exp/$name.stderr | tail -2
  stamp "$name end"
  python3 tools/exp/summarize.py artifacts/exp/$name
}
run U-eval-stone_pick-s11-30 --config configs/exp/stone_pick_time.yaml --eval-before 20 --eval-offset 10
run T-eval-stone_pick-s11-30 --config configs/exp/stone_pick_time.yaml --heads $T/final.safetensors --eval-before 20 --eval-offset 10
run U-eval-iron --config configs/exp/iron.yaml --eval-before 10
run T-eval-iron --config configs/exp/iron.yaml --heads $T/final.safetensors --eval-before 10
stamp "queue done"
