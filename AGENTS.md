# AI tool disclosure

Coding-agent use is required by this hackathon, and so is disclosing it. This
is the complete list.

## Agents used

| Agent                                               | Where                                       | What it did                                                                                                                  |
| --------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Claude Code** (interactive), Opus 5 (1M context)  | my terminal                                 | Wrote every module in `src/witness/`, chose the case-selection criteria, ran every experiment, and wrote this documentation. |
| **Claude Code** (headless, `claude -p`), same model | subprocess, driven by `src/witness/port.py` | Generated all 74 candidate ports — 37 baseline, 37 Witness — and the ablation ports (12 reported cases × 3 repair-signal arms).                                      |
| **Claude Code** (subagent fan-out), same model            | documentation audit only                    | Re-read every prose document against the raw artifacts in `results/` and reported claim drift. Wrote no code and touched no result. Its findings are the stage-16 changelog row. |

All three are the same product and the same model. For the two experiment arms that is deliberate: **the
baseline and the Witness arm must differ only in the scaffolding around the
agent, not in the agent itself.** If the arms used different models, the
comparison would measure the model, not the method.

## What each arm gets

|                                 | Baseline arm                                  | Witness arm                               |
| ------------------------------- | --------------------------------------------- | ----------------------------------------- |
| Tools                           | `Read, Write, Edit, Bash, Glob, Grep`         | none                                      |
| Turns per call                  | 30                                            | 6                                         |
| Calls per case                  | 1                                             | up to 4 (1 draft + up to 3 repairs)       |
| Sees the workbook file          | yes                                           | **no**                                    |
| Sees the extracted formula cone | no                                            | yes                                       |
| Sees a typed input domain       | no                                            | yes                                       |
| Feedback on failure             | whatever it checks itself                     | a shrunk counterexample, and nothing else |
| Sandbox                         | isolated temp dir with a copy of the workbook | no filesystem access at all               |

This asymmetry is intentional and is disclosed in `CHANGELOG.md` under the
fairness note. The baseline is _more_ privileged in tool access and turn budget;
the Witness arm is more privileged in context quality and gets a verification
loop. That is precisely the comparison being made — better scaffolding versus
more freedom.

## Trajectories

Rendered under `trajectories/`:

- `01-build-agent.md` — the interactive session that built the repository, with
  human checkpoints visible at every `user` turn.
- `02-port-agent.md` — what the port agent receives, and the observed repair
  loops with per-attempt trial counts.

Raw transcripts live in Claude Code's own JSONL store. Absolute home paths are
redacted and the renderer asserts no leakage before writing.

## What the agents did _not_ do

- They did not choose the evaluation metric, the tolerance, the seeds, or the
  pass criterion. I did.
- The audit fan-out did not change a single number. It could only flag a
  document that disagreed with an artifact; every correction it prompted moved
  the *prose* toward `results/`, never the reverse. Its checks are now frozen
  into `witness.verify` as the document-claims check, so a judge can rerun them
  in ten seconds rather than take this paragraph on trust.
- They did not label any ground truth. **Nothing in this project has
  agent-authored ground truth** — the oracle is the workbook.
- They did not write the corpus. It is 17 public-record workbooks published by
  the Commonwealth of Massachusetts.

## Human checkpoints

Three decisions in this project were mine, made against what the agent had
produced, and each is visible in the trajectory:

1. **The engine-trust gate came back 9/14** and I did not accept it. Inspecting
   the failures showed a date-serial bug in my own comparator, not the engine.
   → 12/12 usable at the time, and 12/12 usable of 17 today.
2. **The harness self-test showed 9 of 16 cases certifying a do-nothing port.**
   I stopped and added a sensitivity screen rather than publishing the number.
   → cases 16 → 10 at the time. The screen still holds at today's 37 cases:
      shortcut caught 37/37 (`results/selftest.json`).
3. **The baseline arm scored artificially badly** because my harness captured
   the agent's prose summary instead of its code. I found it while reviewing the
   baseline before believing its score, and regenerated all 10 baselines.
   → all 10 imported cleanly at the time; 37/37 do at today's corpus size.

Each of those would have produced a _better-looking_ result if left alone. That
is the point of checking.
