#!/usr/bin/env python3
"""Pins the corrupt-pipeline contract of summarize.py + the action Scan step
(C's c72 defect report — bless-by-invisibility family member #3, claimed by
A as c80).

Defect: with findings>0 handled, the pipeline still mapped DAMAGE to a clean
verdict: engine killed mid-write (truncated sg.json), garbage, '{}', or a
missing sg.json all made summarize.py print '0' rc=0, and the step published
findings=0 exit 0 — an unscanned repo blesses as clean. This harness drives
the Scan step run block extracted VERBATIM from the LOCAL action.yml (must
byte-match the working tree; the published-tag leg is findings-output-matrix
in the engine repo) against a FAKE ENGINE that emits the damage shapes, and
asserts no corrupt leg can ever publish a findings line:

  P1 truncated JSON + rc 0      -> step exits 3, GITHUB_OUTPUT has NO
                                   findings= line (old: findings=0 rc=0)
  P2 rc 0 but findings present  -> exits 3 (inconsistent verdict pair)
  P3 engine rc 2, no output     -> exits 2 = the engine's OWN rc, no line
                                   (old: '|| true' + missing file -> '0')
  P4 '{}' valid-JSON non-list   -> exits 3, no line
  P5 garbage text + rc 0        -> exits 3, no line
  P6 MISSING sg.json, rc 0      -> exits 3, no line
  P7 empty [] + rc 0 (control)  -> findings=0 exit 0  (non-vacuity: the
                                   matrix can go green)
  P8 1-finding array + rc 1     -> findings=1 exit 0 with fail=false

Fixture tokens are assembled at RUNTIME (c25 self-scan rule: zero static
real-format tokens in this repo). action.yml and summarize.py are read from
the SAME working tree — the pair this repo signs/releases as a unit; the
published-tag leg of the pair is findings-output-matrix.py in the engine
repo.

Exit 0 all pass, 1 any failure (names it), 2 extraction/assert failure.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

FAKE_ENGINES = {
    # name: (stdout bytes, exit code)
    "truncated": ('[{"path": "a", ', 0),
    "rc0_with_findings": (None, 0),   # placeholder; built after token known
    "rc2_no_output": ("", 2),
    "empty_obj": ("{}\n", 0),
    "garbage": ("not json at all\n", 0),
    "missing": ("MISSING_FILE", 0),   # write nothing to sg.json at all
    "clean": ("[]\n", 0),
    "one_finding": (None, 1),
}


def extract_scan_step(action_yml):
    assert "id: scan" in action_yml, "action.yml no longer has an id: scan step"
    assert 'echo "findings=$n" >> "$GITHUB_OUTPUT"' in action_yml, \
        "action.yml no longer publishes findings via GITHUB_OUTPUT"
    # v1.2.6 shape asserts: the fix must still be there when this runs.
    assert "rc=$?" in action_yml and '"$rc"' in action_yml, \
        "Scan step lost the engine-rc pass-through (v1.2.6 contract)"
    m = re.search(
        r"id: scan\n(?:.*\n)*?      run: \|\n((?:        .*\n)+)", action_yml)
    assert m, "could not extract Scan step run block from action.yml"
    body = m.group(1)
    assert "findings=" in body and "GITHUB_OUTPUT" in body, \
        "extracted block lost the findings contract"
    return body


def main():
    engine = sys.argv[1] if len(sys.argv) > 1 else None
    with open(os.path.join(REPO, "action.yml")) as f:
        action_yml = f.read()
    with open(os.path.join(REPO, "summarize.py")) as f:
        summarize = f.read()
    body = extract_scan_step(action_yml)

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        action_path = os.path.join(tmp, "action")
        os.makedirs(action_path)
        with open(os.path.join(action_path, "summarize.py"), "w") as f:
            f.write(summarize)

        scan_dir = os.path.join(tmp, "scan")
        os.makedirs(scan_dir)
        with open(os.path.join(scan_dir, "app.py"), "w") as f:
            f.write("print('hello world')\n")
        token = "AKIA" + "1234567890ABCDEF"
        finding_json = (
            '[{"path": "conf.py", "line": 1, "severity": "HIGH", '
            '"rule": "aws-access-key", "secret_preview": "%s"}]\n' % token)

        def drive(case):
            out = os.path.join(tmp, "ghout_" + case)
            json_out = out + ".json"
            summary = out + ".summary"
            open(summary, "w").close()
            fake = os.path.join(tmp, "fake_engine_" + case + ".py")
            stdout, rc = FAKE_ENGINES[case]
            if stdout is None:
                stdout = finding_json
            if stdout == "MISSING_FILE":
                with open(fake, "w") as f:
                    f.write("import sys\nsys.exit(%d)\n" % rc)
            else:
                # fake engine prints its payload WITHOUT the real-engine
                # newline handling: engine writes --json to stdout, redirect
                # does the file write in the step body.
                with open(fake, "w") as f:
                    f.write("import sys\nsys.stdout.write(%r)\nsys.exit(%d)\n"
                            % (stdout, rc))
            env = dict(os.environ)
            env.update({
                "SG": fake, "SG_SCAN": "working", "SG_FAIL": "false",
                "SG_PATH": scan_dir, "SG_JSON_OUT": json_out,
                "GITHUB_STEP_SUMMARY": summary, "GITHUB_OUTPUT": out,
                "GITHUB_ACTION_PATH": action_path,
            })
            r = subprocess.run(["bash", "-c", body], env=env,
                               capture_output=True, text=True, cwd=tmp,
                               timeout=120)
            published = None
            if os.path.exists(out):
                lines = [l for l in open(out).read().splitlines()
                         if l.startswith("findings=")]
                assert len(lines) <= 1, "multiple findings lines: %r" % lines
                published = lines[0].split("=", 1)[1] if lines else None
            return r, published

        # Corruption legs: exit !=0 AND no published findings line.
        expect = {
            "truncated": (3, None),
            "rc0_with_findings": (3, None),
            "rc2_no_output": (2, None),
            "empty_obj": (3, None),
            "garbage": (3, None),
            "missing": (3, None),
        }
        for case, (w_rc, w_pub) in expect.items():
            r, pub = drive(case)
            ok = r.returncode == w_rc and pub == w_pub
            results.append((f"P:{case} exits {w_rc}, no findings line", ok,
                            r, pub))

        # Non-vacuity control: real clean scan still blesses.
        r, pub = drive("clean")
        results.append(("P:clean publishes findings=0 exit 0",
                        r.returncode == 0 and pub == "0", r, pub))
        # Happy findings leg: fail=false report-only publishes 1, exit 0.
        r, pub = drive("one_finding")
        results.append(("P:one_finding publishes findings=1 exit 0",
                        r.returncode == 0 and pub == "1", r, pub))

    ok = 0
    for name, passed, r, pub in results:
        print(("PASS " if passed else "FAIL ") + name +
              ("" if passed else f" (got rc={r.returncode} pub={pub!r} "
                                 f"stderr={r.stderr[:120]!r})"))
        ok += passed
    print("%d/%d" % (ok, len(results)))
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
