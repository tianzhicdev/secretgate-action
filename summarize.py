#!/usr/bin/env python3
"""Read secretgate --json output, emit GH annotations + step summary, print count.

FAIL-CLOSED CONTRACT (v1.2.6, C's c72 defect #3 — bless-by-invisibility family):
stdout carries the finding count ONLY when the scan actually ran. Missing
file, truncated/garbage JSON, non-list JSON (e.g. '{}'), or engine rc >= 2
means THE SCAN DID NOT HAPPEN: we print NO count (empty stdout), annotate
::error to stderr, and exit 3 (or pass the engine rc through). A corrupt
pipeline must never publish findings=0 — silently mapping damage to '0'
blessed an unscanned repo rc=0-clean. The consumer step (action.yml >=
v1.2.6) passes the engine's exit code as arg 3 and treats ANY nonzero here
as step failure, so an honest failure replaces a fake clean.

Shape validation is strict on purpose: engine --json emits ONLY a JSON array
of finding objects ({}, ["x"], and bare strings are damage, not "no
findings").
"""
import json
import sys


def usage() -> int:
    print("usage: summarize.py SG_JSON [STEP_SUMMARY [ENGINE_RC]]",
          file=sys.stderr)
    return 2


def _fail(reason: str, rc: int, summary_path: str) -> int:
    """Corrupt-pipeline leg: ::error annotation + summary line, NO count on
    stdout (the caller's integer test must go red, not read '0')."""
    print(f"::error::secretgate pipeline failure: {reason}", file=sys.stderr)
    try:
        with open(summary_path, "a") as summ:
            summ.write("### secretgate: scan pipeline failed — verdict "
                       "untrusted (never treat this run as clean)\n\n")
    except OSError:
        pass
    return rc


def main() -> int:
    if len(sys.argv) < 2:
        return usage()
    src, summary_path = sys.argv[1], sys.argv[2]
    engine_rc = -1
    if len(sys.argv) >= 4:
        try:
            engine_rc = int(sys.argv[3])
        except ValueError:
            return usage()

    try:
        with open(src) as fh:
            findings = json.load(fh)
    except FileNotFoundError:
        return _fail(f"{src} not found — engine produced no output", 3,
                     summary_path)
    except json.JSONDecodeError as exc:
        return _fail(f"{src} is not valid JSON ({exc}) — "
                     "truncated or damaged scan output", 3, summary_path)
    except OSError as exc:
        return _fail(f"{src} unreadable ({exc})", 3, summary_path)

    # Engine exit-code leg (action >= v1.2.6 passes it; older callers pass
    # nothing and stay byte-compatible). rc==2 is always fatal (path error,
    # CLI misuse); rc>1 any other hard crash; rc==0 WITH findings is an
    # impossible engine verdict pair = damage; rc==1 with findings is the
    # normal found-something leg.
    if engine_rc >= 2:
        return _fail(f"engine exited {engine_rc} — scan did not complete",
                     engine_rc, summary_path)
    if engine_rc == 0 and findings:
        return _fail(f"engine exited 0 yet emitted {len(findings)} "
                     "finding(s) — inconsistent verdict pair", 3,
                     summary_path)
    if engine_rc == 1 and not findings:
        return _fail("engine exited 1 (findings) yet emitted an empty array "
                     "— inconsistent verdict pair", 3, summary_path)

    # Strict shape: array of objects, nothing else blessed.
    if not isinstance(findings, list) or any(
            not isinstance(f, dict) for f in findings):
        return _fail(f"{src} is valid JSON but not an array of finding "
                     f"objects (got {type(findings).__name__}) — not a "
                     "secretgate --json verdict", 3, summary_path)

    for f in findings:
        sev = str(f.get("severity", "high")).upper()
        # Annotations go to stderr: callers capture OUR STDOUT for the finding
        # count (`n=$(python3 summarize.py ...)`), so any '::warning' line
        # printed to stdout lands inside $n and breaks the numeric test.
        print(
            f"::warning file={f.get('path', '?')},line={f.get('line', 1)},"
            f"title=secretgate {f.get('rule', 'secret')}::"
            f"[{sev}] possible secret: {f.get('secret_preview', '')}",
            file=sys.stderr,
        )

    with open(summary_path, "a") as summ:
        summ.write(f"### secretgate: {len(findings)} finding(s)\n\n")
        if findings:
            summ.write("| Severity | File | Line | Rule | Preview |\n")
            summ.write("|---|---|---|---|---|\n")
            for f in findings:
                summ.write(
                    f"| {f.get('severity', '?')} | `{f.get('path', '?')}` | "
                    f"{f.get('line', 1)} | {f.get('rule', '?')} | "
                    f"`{f.get('secret_preview', '')}` |\n"
                )

    print(len(findings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
