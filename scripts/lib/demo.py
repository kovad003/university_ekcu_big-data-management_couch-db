"""Step-by-step runner shared by the experiment scripts.

Pauses before each step when attached to a terminal (--auto turns that off).
Every run overwrites evidence/<slug>/ with transcript.md, results.json and record.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from .couch import REPO_ROOT, Couch, Resp, redact

_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
if os.name == "nt":  # an empty system() call switches the windows console to ansi mode
    os.system("")


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


BOLD, DIM, CYAN, GREEN, RED, YELLOW, MAGENTA = "1", "2", "36", "32", "31", "33", "35"


def _trim(obj: Any, max_items: int = 5, max_str: int = 90) -> Any:
    """Screen only. The transcript keeps the full body."""
    if isinstance(obj, list):
        out = [_trim(v, max_items, max_str) for v in obj[:max_items]]
        if len(obj) > max_items:
            out.append(f"... {len(obj) - max_items} more")
        return out
    if isinstance(obj, dict):
        return {k: _trim(v, max_items, max_str) for k, v in obj.items()}
    if isinstance(obj, str) and len(obj) > max_str:
        return obj[:max_str] + "..."
    return obj


def make_parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--auto", action="store_true",
                   help="run without pausing between steps")
    p.add_argument("--step", action="store_true",
                   help="pause before every step (default when run in a terminal)")
    return p


class Demo:
    def __init__(self, slug: str, title: str, args: argparse.Namespace,
                 configuration: list[str]):
        self.slug = slug
        self.title = title
        self.pause = args.step or (not args.auto and sys.stdin.isatty())
        self.dir = REPO_ROOT / "evidence" / slug
        self.dir.mkdir(parents=True, exist_ok=True)
        self.started = dt.datetime.now().astimezone()
        self.configuration = configuration
        self.checks: list[dict] = []
        self.actions: list[str] = []
        self._md: list[str] = [
            f"# {title}",
            "",
            f"Run started: {self.started.isoformat(timespec='seconds')}",
            "",
            "Configuration:",
            *[f"- {c}" for c in configuration],
            "",
        ]
        self._step_no = 0
        print(_c(BOLD, f"\n=== {title} ==="))
        for c in configuration:
            print(_c(DIM, f"  {c}"))

    def part(self, heading: str) -> None:
        print(_c(BOLD + ";" + MAGENTA, f"\n## {heading}"))
        self._md += [f"## {heading}", ""]

    def step(self, title: str, why: Optional[str] = None) -> None:
        self._step_no += 1
        print(_c(BOLD + ";" + CYAN, f"\n[{self._step_no}] {title}"))
        if why:
            print(_c(DIM, f"    {why}"))
        self._md += [f"### Step {self._step_no}: {title}", ""]
        if why:
            self._md += [f"_{why}_", ""]
        self.actions.append(title)
        if self.pause:
            try:
                input(_c(DIM, "    [Enter] to run "))
            except EOFError:
                self.pause = False

    def info(self, text: str) -> None:
        print(_c(YELLOW, f"    {text}"))
        self._md += [f"> {text}", ""]

    def call(self, couch: Couch, method: str, path: str, body: Any = None,
             params: Optional[dict] = None, screen: str = "trim") -> Resp:
        """screen: 'trim', 'full' or 'status' (status line only)."""
        shown_path = path
        if params:
            shown_path += "?" + "&".join(
                f"{k}={json.dumps(v) if isinstance(v, bool) else v}" for k, v in params.items())
        print(_c(BOLD, f"  {couch.label} > {method} {shown_path}"))
        if body is not None and screen != "status":
            print(_indent(json.dumps(_trim(redact(body)), indent=2, ensure_ascii=False)))
        resp = couch.request(method, path, body, params)
        colour = GREEN if resp.ok else RED
        print(_c(colour, f"  {couch.label} < HTTP {resp.status} {resp.reason}"))
        if screen != "status" and resp.body is not None:
            shown = resp.body if screen == "full" else _trim(resp.body)
            print(_indent(json.dumps(redact(shown), indent=2, ensure_ascii=False)))
        self._md += [
            f"**Instance {couch.label}** (`{couch.url}`)",
            "",
            "```http",
            f"{method} {shown_path}",
            *( [json.dumps(redact(body), indent=2, ensure_ascii=False)] if body is not None else [] ),
            "```",
            "",
            f"Response: **HTTP {resp.status} {resp.reason}**",
            "",
            "```json",
            json.dumps(redact(resp.body), indent=2, ensure_ascii=False),
            "```",
            "",
        ]
        return resp

    def check(self, description: str, passed: bool, expected: str, observed: str) -> bool:
        mark = _c(GREEN, "PASS") if passed else _c(RED, "FAIL")
        print(f"    {mark} {description}")
        print(_c(DIM, f"         expected: {expected}"))
        print(_c(DIM, f"         observed: {observed}"))
        self.checks.append({
            "step": self._step_no, "check": description, "expected": expected,
            "observed": observed, "result": "PASS" if passed else "FAIL",
        })
        self._md += [f"- **{'PASS' if passed else 'FAIL'}**: {description}  ",
                     f"  expected: {expected}  ", f"  observed: {observed}", ""]
        return passed

    def save_json(self, name: str, data: Any) -> Path:
        path = self.dir / name
        path.write_text(json.dumps(redact(data), indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        return path

    def finish(self, interpretation: list[str]) -> None:
        failed = [c for c in self.checks if c["result"] == "FAIL"]
        (self.dir / "transcript.md").write_text("\n".join(self._md) + "\n", encoding="utf-8")
        self.save_json("results.json", {
            "experiment": self.title,
            "started": self.started.isoformat(timespec="seconds"),
            "finished": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "passed": len(self.checks) - len(failed),
            "failed": len(failed),
            "checks": self.checks,
        })
        rec = [
            f"# Experiment record: {self.title}",
            "",
            f"Generated by the script on {self.started.isoformat(timespec='seconds')}. "
            "The full request and response log is in `transcript.md`.",
            "",
            "## Configuration", "", *[f"- {c}" for c in self.configuration], "",
            "## Action", "", *[f"{i}. {a}" for i, a in enumerate(self.actions, 1)], "",
            "## Expected vs observed", "",
            "| Step | Check | Expected | Observed | Result |",
            "| --- | --- | --- | --- | --- |",
            *[f"| {c['step']} | {c['check']} | {_cell(c['expected'])} | "
              f"{_cell(c['observed'])} | {c['result']} |" for c in self.checks],
            "",
            "## Interpretation", "", *[f"- {line}" for line in interpretation], "",
        ]
        (self.dir / "record.md").write_text("\n".join(rec), encoding="utf-8")
        summary = f"{len(self.checks) - len(failed)}/{len(self.checks)} checks passed"
        print(_c(BOLD + ";" + (GREEN if not failed else RED), f"\n=== {summary} ==="))
        print(_c(DIM, f"Evidence written to {self.dir.relative_to(REPO_ROOT)}/"))
        if failed:
            sys.exit(1)


def _indent(text: str, pad: str = "      ") -> str:
    return "\n".join(pad + line for line in text.splitlines())


def _cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")
