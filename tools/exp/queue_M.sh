#!/bin/bash
# Arm M: from the arm T heads, train on the stone-pickaxe chain and the iron task in turn (both with the time cost),
# then evaluate both on slots 1-10. Asks whether the recipe that learned stone also learns the next link of the
# diamond chain without losing the first. $1 = PID to wait for (a finished PID starts it now). One game server at a time.
cd /home/sion/Documents/projects/RL_projects/Minecraft_learning-exp || exit 1
export PYTHONPATH=$PWD/src PATH=/home/sion/Documents/projects/RL_projects/Minecraft_learning/.venv/bin:$PATH
while kill -0 "$1" 2>/dev/null; do sleep 30; done
stamp() { echo "$(date +%FT%T%:z) $*"; }
stamp "commit $(git rev-parse --short HEAD) dirty: $(git status --porcelain -- src configs bridge | wc -l)"
name=M-train-mixed
stamp "$name start"
python -m mc_diamond.exp --config configs/exp/stone_pick_time.yaml --config configs/exp/iron_time.yaml \
  --heads artifacts/exp/T-train-stone_pick/final.safetensors --train 4096 --eval-after 10 --critic-replay-epochs 4 \
  --output artifacts/exp/$name 2> artifacts/exp/$name.stderr | tail -2
stamp "$name end"
python3 tools/exp/summarize.py artifacts/exp/$name
stamp "queue done"
