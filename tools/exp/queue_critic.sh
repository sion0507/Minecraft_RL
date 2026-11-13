#!/bin/bash
# After the D3 queue: which extra critic input helps (tools/exp/critic_inputs.py), one input group at a time, on the
# saved decisions of arm T, of the two iron evaluations and of arm D3. Model only, no game. $1 = PID to wait for.
cd /home/sion/Documents/projects/RL_projects/Minecraft_learning-exp || exit 1
export PYTHONPATH=$PWD/src PATH=/home/sion/Documents/projects/RL_projects/Minecraft_learning/.venv/bin:$PATH
while kill -0 "$1" 2>/dev/null; do sleep 30; done
sleep 30
A=artifacts/exp
stamp() { echo "$(date +%FT%T%:z) $*"; }
stamp "commit $(git rev-parse --short HEAD)"
one() {  # name, trace glob, extra fit settings ...
  name=$1 traces=$2; shift 2
  stamp "$name encode start"
  python tools/exp/critic_inputs.py encode --traces "$traces" --output $A/critic-$name.pt 2> $A/critic-$name.stderr | tail -1
  stamp "$name fit lr 1e-4"
  python tools/exp/critic_inputs.py fit --data $A/critic-$name.pt --output $A/critic-$name.json 2>> $A/critic-$name.stderr
  for lr in "$@"; do
    stamp "$name fit lr $lr"
    python tools/exp/critic_inputs.py fit --data $A/critic-$name.pt --output $A/critic-$name-lr$lr.json --lr $lr 2>> $A/critic-$name.stderr
  done
}
one T "$A/T-train-stone_pick/train-*.jsonl.gz" 1e-3
one iron "$A/[UT]-eval-iron/before-*.jsonl.gz"
one D3 "$A/D3-train-stone_pick/train-*.jsonl.gz"
stamp "queue done"
