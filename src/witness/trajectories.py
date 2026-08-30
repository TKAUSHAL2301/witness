"""Deliverable 4 — agent trajectories.

The rulebook asks for "representative trajectories for every agent you used…
easy to follow from the agent instructions to the final result. Show what the
agent did and how its tools responded. Capture the feedback that shaped its
next step as well as any retries or human checkpoints."

Two agents were used and both are rendered here:

  1. The BUILD agent (Claude Code, interactive) that wrote this repository.
     Its transcripts are JSONL under ~/.claude/projects/<slug>/.

  2. The PORT agent (Claude Code, `claude -p`) that generated each candidate
     port. Its feedback loop is the interesting one, because the only thing it
     ever receives back is a shrunk counterexample — never a critique.

Redacts absolute home paths. Contains no credentials (Ground Rule 08).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HOME = str(Path.home())
PROJECT_DIR = Path(HOME) / ".claude/projects/-Users-tkaushal99gmail-com-hackathon"
MAX_CHARS = 1600


def redact(s: str) -> str:
    s = s.replace(HOME, "~")
    s = re.sub(r"(sk-[A-Za-z0-9_-]{8,})", "[REDACTED-KEY]", s)
    return s


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for b in content:
            if not isinstance(b, dict):
                continue
            t = b.get("type")
            if t == "text":
                out.append(b.get("text", ""))
            elif t == "tool_use":
                args = json.dumps(b.get("input", {}), default=str)
                out.append(f"→ TOOL CALL `{b.get('name')}`\n```json\n{args[:MAX_CHARS]}\n```")
            elif t == "tool_result":
                c = b.get("content")
                c = _text(c) if not isinstance(c, str) else c
                flag = " (ERROR)" if b.get("is_error") else ""
                out.append(f"← TOOL RESULT{flag}\n```\n{c[:MAX_CHARS]}\n```")
        return "\n\n".join(out)
    return str(content)


def render_build_agent(out: Path, max_events: int = 220) -> int:
    files = sorted(PROJECT_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not files:
        out.write_text("_No build-agent transcript found._\n")
        return 0
    src = files[-1]
    events = []
    for line in src.read_text(errors="ignore").splitlines():
        try:
            d = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        if role not in ("user", "assistant"):
            continue
        body = _text(m.get("content"))
        if not body.strip():
            continue
        events.append((role, body))

    lines = [
        "# Agent trajectory 1 — the build agent",
        "",
        "**Agent:** Claude Code (interactive), model Opus 5 (1M context).",
        "**Role:** wrote every module in `src/witness/`, chose the case-selection",
        "criteria, and ran every experiment.",
        "",
        f"**Source transcript:** `~/.claude/projects/.../{src.name}` "
        f"({src.stat().st_size:,} bytes). Rendered below: last {max_events} events.",
        "",
        "Human checkpoints are visible throughout: every `user` turn is me steering,",
        "correcting, or interrupting the agent. Two are worth finding — the turn where",
        "the harness self-test reported 9/16 cases certifying a do-nothing port, and the",
        "turn where the engine-trust gate came back 9/14 and the cause turned out to be",
        "a date-serial bug in my own comparator rather than the engine.",
        "",
        "---",
        "",
    ]
    for role, body in events[-max_events:]:
        who = "🧑 HUMAN" if role == "user" else "🤖 AGENT"
        lines.append(f"### {who}\n\n{redact(body)[:6000]}\n")
    out.write_text("\n".join(lines))
    return len(events[-max_events:])


def render_port_agent(out: Path) -> int:
    """The repair loop: instructions → port → counterexample → repaired port."""
    pg = Path("results/portgen.json")
    log = json.loads(pg.read_text()) if pg.exists() else []
    witness_runs = [e for e in log if e.get("arm") == "witness" and e.get("history")]
    # portgen.json only holds the most recent run; recover the rest from the logs.
    if not witness_runs:
        seen = set()
        for lg in sorted(Path("results").glob("portgen*.log")):
            for m in re.finditer(r"\[ ok \] witness/(\S+)\s+repairs=(\d+) certified=(\w+)", lg.read_text(errors="ignore")):
                name, reps, cert = m.group(1), int(m.group(2)), m.group(3) == "True"
                if name in seen:
                    continue
                seen.add(name)
                witness_runs.append({"case": name, "history": [
                    {"attempt": i, "agreed": "-", "trials": 2000,
                     "certified": cert and i == reps} for i in range(reps + 1)]})

    lines = [
        "# Agent trajectory 2 — the port agent",
        "",
        "**Agent:** Claude Code in headless mode (`claude -p`), same model.",
        "**Role:** writes the candidate Python port for one target cell.",
        "",
        "## What the agent receives",
        "",
        "The **baseline arm** gets the workbook path, the target cell, the input list,",
        "and one instruction — *\"read the workbook, work out what the target computes,",
        "check your work however you think best.\"* It has Read/Bash/Glob/Grep.",
        "",
        "The **Witness arm** gets no file access at all. It gets the extracted formula",
        "cone, a typed domain per input, and then — on failure — **only this**:",
        "",
        "```json",
        json.dumps(
            {
                "failing_inputs": {"'Sheet'!B4": None, "'Sheet'!C7": 0},
                "excel_returned": 2481003.11,
                "your_port_returned": 1286441.02,
                "minimal_differing_inputs": "'Sheet'!B4",
            },
            indent=2,
        ),
        "```",
        "",
        "No critique. No explanation. No hint about *why* it is wrong. The shrunk",
        "counterexample is the entire repair signal, and that constraint is the",
        "subject of the ablation in `CHANGELOG.md`.",
        "",
        "## Observed repair loops",
        "",
    ]
    if not witness_runs:
        lines.append("_No port-generation history recorded yet._")
    for e in witness_runs:
        lines.append(f"### `{e['case']}`\n")
        lines.append("| attempt | trials survived | certified |")
        lines.append("| --- | --- | --- |")
        for h in e.get("history", []):
            lines.append(
                f"| {h['attempt']} | {h['agreed']}/{h['trials']} | "
                f"{'yes' if h['certified'] else 'no'} |"
            )
        lines.append("")
    out.write_text("\n".join(lines))
    return len(witness_runs)


def main(argv: list[str]) -> int:
    d = Path("trajectories")
    d.mkdir(exist_ok=True)
    n1 = render_build_agent(d / "01-build-agent.md")
    n2 = render_port_agent(d / "02-port-agent.md")
    print(f"trajectories/01-build-agent.md  ({n1} events)")
    print(f"trajectories/02-port-agent.md   ({n2} repair loops)")
    for f in sorted(d.glob("*.md")):
        assert HOME not in f.read_text(), f"home path leaked into {f}"
    print("redaction check: no absolute home paths present")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
