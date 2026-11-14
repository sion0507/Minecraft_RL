#!/bin/bash
# After the critic queue: arm T again with another training seed (11016) on the current code, to see whether the
# shift arm T showed (and arm D3 did not) comes back. Then its heads on the same fixed states and the same 30 slots.
# $1 = PID to wait for (a finished PID starts it now). One game server at a time.
cd /home/sion/Documents/projects/RL_projects/Minecraft_learning-exp || exit 1
export PYTHONPATH=$PWD/src PATH=/home/sion/Documents/projects/RL_projects/Minecraft_learning/.venv/bin:$PATH
while kill -0 "$1" 2>/dev/null; do sleep 30; done
sleep 30
T=artifacts/exp/T-train-stone_pick D=artifacts/exp/D3-train-stone_pick N=artifacts/exp/T2-train-stone_pick
stamp() { echo "$(date +%FT%T%:z) $*"; }
stamp "commit $(git rev-parse --short HEAD) dirty: $(git status --porcelain -- src configs bridge | wc -l)"
run() {
  name=$1; shift
  stamp "$name start"
  python -m mc_diamond.exp "$@" --output artifacts/exp/$name 2> artifacts/exp/$name.stderr | tail -2
  stamp "$name end"
  python3 tools/exp/summarize.py artifacts/exp/$name
}
run T2-train-stone_pick --config configs/exp/stone_pick_time.yaml --train 3072 --eval-after 10 --critic-replay-epochs 4 --seed 11016
stamp "probe start"
python tools/exp/fixed_probe.py --traces "$T/before-*.jsonl.gz" --output artifacts/exp/probe-fixed-before-T2.json \
  --heads $T/initial.safetensors $T/final.safetensors $D/final.safetensors \
  $N/update-08.safetensors $N/update-16.safetensors $N/update-20.safetensors $N/final.safetensors 2> artifacts/exp/probe-fixed-before-T2.stderr
stamp "probe end $?"
run T2-eval-stone_pick-s11-30 --config configs/exp/stone_pick_time.yaml --heads $N/final.safetensors --eval-before 20 --eval-offset 10
stamp "queue done"
