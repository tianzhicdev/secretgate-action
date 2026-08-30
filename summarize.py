#!/usr/bin/env python3
"""Read secretgate --json output, emit GH annotations + step summary, print count."""
import json
import sys


def main() -> int:
    src, summary_path = sys.argv[1], sys.argv[2]
    try:
        with open(src) as fh:
            findings = json.load(fh)
        if not isinstance(findings, list):
            findings = []
    except Exception:
        findings = []

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
