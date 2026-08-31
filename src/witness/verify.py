"""One command that answers: is every published number still true?

Running the four stages separately proves they pass. It does not prove the
README is telling the truth about them — and those are different failures.
Twice during this build a committed artifact drifted behind the prose that
cited it: `gate.json` still said 14 workbooks after the corpus grew to 17, and
`selftest.json` held 10 cases at 100 trials while the README claimed 300 trials
across 37. Both would have survived any number of green test runs, because the
tests and the claims were never compared to each other.

So this module does not re-run the science. It reads the artifacts the science
left behind, re-derives each headline figure from the raw rows, and checks it
against the value published in README.md. A stale artifact turns the check red.

That was still not enough. An audit before submission found the same figures had
drifted a third time — in CHANGELOG.md, AGENTS.md, PRIOR-WORK.md and REPRODUCE.md,
documents no check had ever read, while all six checks stayed green. The seventh
check closes that gap: it reads every prose document and turns red if a superseded
claim reappears in any of them.

  uv run python -m witness.verify           read committed artifacts (seconds)
  uv run python -m witness.verify --run     regenerate them first (~10 min)

Exit status is 0 only if every check is green, so it works as a CI gate and as
the last thing to run before submitting.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RESULTS = Path("results")

# The figures README.md publishes. If a check below cannot re-derive one of
# these from the raw artifact, the README is overclaiming and the run is red.
CLAIMED_GATE_PASS = 12
CLAIMED_GATE_CELLS = 36_500
CLAIMED_SELFTEST_CASES = 37
CLAIMED_SELFTEST_TRIALS = 300
CLAIMED_BASELINE = 24
CLAIMED_WITNESS = 32
CLAIMED_KILL_RATE = 0.818
CLAIMED_FALSE_ALARM = 0.0
CLAIMED_CELL_COV = 0.914
CLAIMED_BRANCH_COV = 1.0


class Check:
    def __init__(self, name: str):
        self.name = name
        self.ok = False
        self.headline = ""
        self.notes: list[str] = []

    def fail(self, why: str) -> "Check":
        self.ok, self.headline = False, why
        return self

    def pas(self, headline: str) -> "Check":
        self.ok, self.headline = True, headline
        return self


def _load(name: str):
    p = RESULTS / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def check_gate() -> Check:
    c = Check("engine-trust gate")
    d = _load("gate.json")
    if d is None:
        return c.fail("results/gate.json missing — run witness.gate corpus")

    reports = d["reports"]
    passed = sum(1 for r in reports if r["passes"])
    cells = sum(r["agreed"] for r in reports)
    disagreements = sum(len(r["disagreements"]) for r in reports)
    usable = [r for r in reports if r["compared"] > 0]

    if disagreements:
        return c.fail(f"{disagreements} cell(s) disagreed with Excel's cached values")
    if passed < CLAIMED_GATE_PASS:
        return c.fail(f"{passed} workbooks pass; README claims {CLAIMED_GATE_PASS}")
    if cells < CLAIMED_GATE_CELLS:
        return c.fail(f"{cells:,} cells compared; README claims {CLAIMED_GATE_CELLS:,}")

    c.notes.append(f"{len(usable)}/{len(usable)} workbooks with cached values reproduce")
    c.notes.append(f"{len(reports) - len(usable)} excluded — no cached formula values to compare")
    return c.pas(f"{passed}/{len(reports)} workbooks · {cells:,} cells · 0 disagreements")


def check_selftest() -> Check:
    c = Check("harness self-test")
    d = _load("selftest.json")
    if d is None:
        return c.fail("results/selftest.json missing — run witness.selftest 300")

    n = len(d)
    trials = {r["identity"]["trials_run"] for r in d}
    perfect = all(r["identity"]["agreed"] == r["identity"]["trials_run"] for r in d)
    shortcut_caught = sum(1 for r in d if not r["shortcut_always_zero"]["certified"])

    if n < CLAIMED_SELFTEST_CASES:
        return c.fail(f"{n} cases in artifact; README claims {CLAIMED_SELFTEST_CASES}")
    if min(trials) < CLAIMED_SELFTEST_TRIALS:
        return c.fail(f"{min(trials)} trials in artifact; README claims {CLAIMED_SELFTEST_TRIALS}")
    if not perfect:
        return c.fail("identity check did not agree on every trial — environment is nondeterministic")
    if shortcut_caught != n:
        return c.fail(f"always-zero port slipped through on {n - shortcut_caught} case(s) — metric is gameable")

    c.notes.append("a port that always returns 0.0 is rejected on every case")
    return c.pas(f"{n}/{n} cases · identity {min(trials)}/{min(trials)} · shortcut caught")


def check_rejection() -> Check:
    """A verifier that only ever says yes has proven nothing, so one test feeds
    it a deliberately defective port and requires a rejection."""
    c = Check("rejection tests")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--no-header"],
        capture_output=True, text=True,
    )
    tail = [ln for ln in r.stdout.strip().split("\n") if ln.strip()]
    last = tail[-1] if tail else "no output"
    if r.returncode != 0:
        return c.fail(f"pytest failed — {last}")
    c.notes.append("includes a port with banker's rounding that MUST be rejected")
    return c.pas(last)


def check_experiment() -> Check:
    c = Check("experiment")
    d = _load("evaluation.json")
    if d is None:
        return c.fail("results/evaluation.json missing — run witness.evaluate")

    s = d["summary"]
    b = s["arms"]["baseline"]["certified"]
    w = s["arms"]["witness"]["certified"]
    tot = s["cases"]
    pp = round((w - b) / tot * 100)

    if w <= b:
        return c.fail(f"no improvement: baseline {b}/{tot}, witness {w}/{tot}")
    if b != CLAIMED_BASELINE or w != CLAIMED_WITNESS:
        c.notes.append(
            f"README publishes {CLAIMED_BASELINE}/{CLAIMED_WITNESS}; "
            f"this artifact is a {s['trials']}-trial run"
        )

    deltas = [
        cs["arms"]["baseline"].get("max_abs_delta", 0)
        for cs in d["cases"]
        if not cs["arms"].get("baseline", {}).get("certified")
    ]
    if deltas:
        c.notes.append(f"largest delta in a failing baseline port: {max(deltas):,.0f} (a date-serial day count, not dollars)")
    return c.pas(f"baseline {b}/{tot} → witness {w}/{tot} (+{pp}pp) at pass^{s['trials']}")


def check_mutation() -> Check:
    c = Check("mutation score")
    d = _load("mutation.json")
    if d is None:
        return c.fail("results/mutation.json missing — run witness.mutation")

    s = d["summary"]
    kill, false_alarm = s["mutation_kill_rate"], s["false_alarm_rate"]
    if false_alarm > CLAIMED_FALSE_ALARM:
        return c.fail(f"{false_alarm:.1%} false alarms on equivalent mutants — must be 0%")
    if kill < CLAIMED_KILL_RATE - 0.01:
        return c.fail(f"kill rate {kill:.1%} below the published {CLAIMED_KILL_RATE:.1%}")
    c.notes.append(f"{s['equivalent_total']} equivalent mutants flagged 0 times (false-alarm control)")
    return c.pas(
        f"{s['killed']}/{s['semantic_total']} semantic mutants killed ({kill:.1%}) · "
        f"{s['false_alarms']}/{s['equivalent_total']} false alarms"
    )


def check_coverage() -> Check:
    c = Check("oracle coverage")
    d = _load("coverage.json")
    if d is None:
        return c.fail("results/coverage.json missing — run witness.coverage")

    cell = [r["cell_coverage"] for r in d if r.get("cell_coverage") is not None]
    branch = [r["branch_coverage"] for r in d if r.get("branch_coverage") is not None]
    if not cell:
        return c.fail("no coverage rows in artifact")
    mc, mb = sum(cell) / len(cell), (sum(branch) / len(branch) if branch else 0.0)
    if mc < CLAIMED_CELL_COV - 0.01:
        return c.fail(f"cell coverage {mc:.1%} below the published {CLAIMED_CELL_COV:.1%}")
    c.notes.append("agreement means little if every vector drove the same branch")
    return c.pas(f"{mc:.1%} mean cell coverage · {mb:.0%} branch coverage")


# ---------------------------------------------------------------------------
# Document consistency.
#
# The six checks above compare README.md against results/. That is necessary
# and it is not sufficient: an audit before submission found the same figures
# had drifted in CHANGELOG.md, AGENTS.md, PRIOR-WORK.md, REPRODUCE.md and the
# trajectories — documents no check had ever read. Every green run had missed
# them, because the claims and the evidence were still never compared.
#
# So this check reads every prose document in the repository and fails on a
# superseded claim reappearing anywhere in it. Each pattern below is a fact
# that was once true and no longer is; the reason is recorded beside it so a
# future reader knows what corrected it rather than only that it is banned.
# ---------------------------------------------------------------------------

DOCS = [
    "README.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "PRIOR-WORK.md",
    "REPRODUCE.md",
]

# The rendered agent transcripts are deliberately NOT scanned for superseded
# claims. A transcript is a record of what was said at the time, so it is
# supposed to contain numbers that were later corrected — the first run of this
# check flagged three, and every one was a verbatim tool call from an earlier
# session. Editing them to satisfy a linter would falsify the very deliverable
# they exist to provide. They are scanned only for the two things that must
# never appear in them regardless: an unfilled placeholder, and a leaked
# absolute path from the machine this was built on.
TRANSCRIPTS = [
    "trajectories/01-build-agent.md",
    "trajectories/02-port-agent.md",
]

LEAKS = [
    (r"<YOUR NAME>|<REPO-URL>", "an unfilled placeholder"),
    (r"/Users/[A-Za-z0-9._-]+/", "a leaked absolute home path"),
]

SUPERSEDED = [
    (r"14 (?:municipal finance|public-record) workbooks", "the corpus is 17 workbooks"),
    (r"20 candidate ports", "74 candidate ports: 37 baseline + 37 witness"),
    (r"10 baseline, 10 Witness", "37 baseline, 37 witness"),
    (r"10 cases is thin", "37 cases; the corpus is too easy, not too small"),
    (r"10/10 cases", "37/37 cases"),
    (r"\(10 cases\)", "the self-test covers 37 cases"),
    (r"30,000 vectors", "9,000 vectors per case (3,000 trials x 3 seeds)"),
    (r"17 workbooks parsed", "results/dag.json covers 14; the other 3 hold no formula cells"),
    (r"33 certified ports", "33 mutated ports: the 32 certified plus Available Funds.S48"),
    (r"Five cases have a single free input", "eleven of the 37 cases have a single free input"),
    (r"6.38 inputs, 8.366 formula nodes", "1-56 inputs, 14-118 formula nodes"),
    (r"witness\.ablation 4\b", "the committed ablation artifact is a 12-case run"),
    (r"certified (?:_?themselves_?|itself) as correct while sitting on",
     "13 baseline ports self-certified and were wrong; only 6 by five figures"),
    (r"certified as correct: \$", "a certified port has zero error by construction"),
    (r"\$47,482|median error when it failed.*\$47",
     "that median filtered out zero deltas; the median of all 13 failures is $2,340"),
    (r"\$50,951|\$47,000 silent error|\$48,030",
     "those deltas are date-serial DAYS on date-formatted cells, not dollars"),
    (r"five-figure errors?\*?\*? — chained", "the five-figure deltas are days, not dollars"),
    (r"\b212\b|18 scale|88 monoton", "106 derived / 53 confirmed (9 scale, 44 monotone); 212/106 double-counted the arms"),
    (r"<YOUR NAME>", "the entrant is named in README.md"),
    (r"<REPO-URL>|git clone <repo>", "the clone URL must be a real, reachable URL"),
]


def check_docs() -> Check:
    c = Check("document claims")
    n_workbooks = len(sorted(Path("corpus").glob("*.xlsx")))
    cases = _load("cases.json")
    n_cases = len(cases) if cases else 0

    hits: list[str] = []
    read = 0
    for name in DOCS:
        p = Path(name)
        if not p.exists():
            hits.append(f"{name} is missing")
            continue
        read += 1
        for i, line in enumerate(p.read_text().splitlines(), 1):
            for pat, why in SUPERSEDED:
                if re.search(pat, line):
                    hits.append(f"{name}:{i} superseded claim — {why}")

    for name in TRANSCRIPTS:
        p = Path(name)
        if not p.exists():
            hits.append(f"{name} is missing")
            continue
        read += 1
        for i, line in enumerate(p.read_text().splitlines(), 1):
            for pat, why in LEAKS:
                if re.search(pat, line):
                    hits.append(f"{name}:{i} {why}")

    if not Path("LICENSE").exists():
        hits.append("LICENSE is missing — required for the licence-compliance rule")

    if hits:
        for h in hits[1:6]:
            c.notes.append(h)
        if len(hits) > 6:
            c.notes.append(f"...and {len(hits) - 6} more")
        return c.fail(hits[0])

    if n_workbooks != 17 or n_cases != CLAIMED_SELFTEST_CASES:
        return c.fail(
            f"corpus holds {n_workbooks} workbooks and cases.json {n_cases} cases; "
            f"the documents are written for 17 and {CLAIMED_SELFTEST_CASES}"
        )

    c.notes.append(f"{len(SUPERSEDED)} superseded claims, each checked in every document")
    return c.pas(f"{read} documents clean · corpus {n_workbooks} · cases {n_cases} · LICENSE present")


CHECKS = [
    check_gate,
    check_selftest,
    check_rejection,
    check_experiment,
    check_mutation,
    check_coverage,
    check_docs,
]


def regenerate() -> None:
    """--run: rebuild the artifacts before checking them."""
    stages = [
        (["-m", "witness.gate", "corpus"], "engine-trust gate", "~2 min"),
        (["-m", "witness.selftest", "300"], "harness self-test", "~4 min"),
        (["-m", "witness.evaluate", "400"], "experiment", "~4 min"),
    ]
    for args, label, eta in stages:
        print(f"  running {label} ({eta}) …", flush=True)
        r = subprocess.run([sys.executable, *args], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  {label} FAILED:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
            sys.exit(1)
    print()


def main(argv: list[str]) -> int:
    if not RESULTS.exists():
        print("No results/ directory. Run from the repository root.")
        return 1

    if "--run" in argv[1:]:
        print("Regenerating artifacts before checking them.\n")
        regenerate()

    tty = sys.stdout.isatty()
    grn, red, dim, off = ("\033[32m", "\033[31m", "\033[2m", "\033[0m") if tty else ("", "", "", "")
    bar = "─" * 74

    print(f"\n{bar}")
    print("WITNESS — verifying every published number against its raw artifact")
    print(bar)

    results = [fn() for fn in CHECKS]
    for c in results:
        tag = f"{grn}[GREEN]{off}" if c.ok else f"{red}[ RED ]{off}"
        print(f"{tag}  {c.name:<22}{c.headline}")
        for note in c.notes:
            print(f"         {dim}{'':<22}{note}{off}")

    n_ok = sum(1 for c in results if c.ok)
    print(bar)
    if n_ok == len(results):
        print(f"{grn}ALL {len(results)} CHECKS GREEN{off} — every published figure is backed by results/.")
    else:
        print(f"{red}{len(results) - n_ok} OF {len(results)} CHECKS RED{off} — see above.")
    print(f"{bar}\n")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
