#!/bin/bash
# After the post-D queue: arm D3 = arm D (no time cost) at arm T's 3,072 decisions, to separate "time cost" from
# "more decisions". Then its heads on the same fixed states and the same 20 extra slots as T. One game server at a time.
cd /home/sion/Documents/projects/RL_projects/Minecraft_learning-exp || exit 1
export PYTHONPATH=$PWD/src PATH=/home/sion/Documents/projects/RL_projects/Minecraft_learning/.venv/bin:$PATH
while kill -0 "$1" 2>/dev/null; do sleep 30; done
sleep 30
T=artifacts/exp/T-train-stone_pick D=artifacts/exp/D3-train-stone_pick
stamp() { echo "$(date +%FT%T%:z) $*"; }
stamp "commit $(git rev-parse --short HEAD) dirty: $(git status --porcelain -- src configs bridge | wc -l)"
run() {
  name=$1; shift
  stamp "$name start"
  python -m mc_diamond.exp "$@" --output artifacts/exp/$name 2> artifacts/exp/$name.stderr | tail -2
  stamp "$name end"
  python3 tools/exp/summarize.py artifacts/exp/$name
}
run D3-train-stone_pick --config configs/exp/stone_pick.yaml --train 3072 --eval-after 10 --critic-replay-epochs 4
stamp "probe start"
python tools/exp/fixed_probe.py --traces "$T/before-*.jsonl.gz" --output artifacts/exp/probe-fixed-before-D3.json \
  --heads $T/initial.safetensors $T/update-16.safetensors $T/final.safetensors \
  $D/update-08.safetensors $D/update-16.safetensors $D/update-20.safetensors $D/final.safetensors 2> artifacts/exp/probe-fixed-before-D3.stderr
stamp "probe end $?"
run D3-eval-stone_pick-s11-30 --config configs/exp/stone_pick_time.yaml --heads $D/final.safetensors --eval-before 20 --eval-offset 10
stamp "queue done"
