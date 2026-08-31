#!/usr/bin/env python3
"""Tip-address parity contract for secretgate-action (A c42 rail, c48 port).

Layers are mapped to THIS repo's real shapes (C c38 lesson: a port that
maps layers to the target's shapes verifies the world, not the porter):
this repo has NO Pages site and NO repo-own 'ETH:' tip line, so its
receive-side money surface is FUNDING.yml (GitHub's Sponsor button —
B c37 proved a repo without FUNDING.yml leaves the platform-advertised
tip layer unpinned) plus the team-footer copy in README.

Layers checked (all must hold or exit 1):
  1. .github/FUNDING.yml: exists, carries EXACTLY ONE distinct EVM addr
     and it == TIP_ADDR (missing file = clean RED, B c37 shape).
  2. README team-footer block: the FIRST address (labeled 'A') == TIP.
  3. REJECT sweep: B's and C's fleet addrs must never appear in
     FUNDING.yml or the README outside the team-footer block. Verify-side
     `require=` deep-link values are scrubbed FIRST (C c38 / A c47 delta):
     they legitimately carry sibling addrs; the scrub's scope is proven
     both directions by the flip harness (plain sibling RED, sibling
     inside require= GREEN).

No third-party imports (stdlib only). Run from the repo root.
"""
import os
import re
import sys

TIP_ADDR = "0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15"  # secretgate: allow public tip addr
FLEET_OTHERS = {  # sibling fleet addrs: a tip copy swapped to one = forgery class
    "0x5439bc46ac9cc70dfFC500611c6D845d7eE9eE5E".lower(): "B",
    "0xf232dcdc177b53981b4d805a48c79f239db8d0f9": "C",
}

ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
failures = []


def die(msg):
    failures.append(msg)
    print(f"FAIL: {msg}")


def ok(msg):
    print(f"OK: {msg}")


def addrs(text):
    """Distinct addresses in text, lower-cased, document order."""
    seen, out = set(), []
    for m in ADDR_RE.findall(text):
        k = m.lower()
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def check_receive_side(layer, text):
    """Address set of a receive-side layer must be exactly {TIP}."""
    a = addrs(text)
    if a == [TIP_ADDR.lower()]:
        ok(f"{layer}: exactly one addr, == TIP")
    else:
        die(f"{layer}: address set {a} != [TIP {TIP_ADDR}] "
            f"(sibling/fleet addr in receive-side layer = B c29 forge class)")


def scrub_verify_side(text):
    return re.sub(r"require=0x[0-9a-fA-F]{40}", "require=<verify-side>", text)


def main():
    # 1. FUNDING.yml — the platform layer (B c37: Sponsor button without
    #    this file = an un-owned, un-pinnable money surface).
    funding_path = os.path.join(".github", "FUNDING.yml")
    if not os.path.isfile(funding_path):
        die("FUNDING.yml missing — sponsor surface unpinned (B c37 class)")
        funding = ""
    else:
        funding = open(funding_path, encoding="utf-8").read()
        check_receive_side("FUNDING.yml", funding)

    # 2. README team-footer: first (A-labelled) addr == TIP
    readme = open("README.md", encoding="utf-8").read()
    team = re.search(r"<!-- team-footer:start -->.*?<!-- team-footer:end -->",
                     readme, re.S)
    if not team:
        die("README team-footer block missing")
    else:
        first = addrs(team.group(0))[:1]
        if first == [TIP_ADDR.lower()]:
            ok("README team-footer: first (A-labelled) addr == TIP")
        else:
            die(f"README team-footer first addr {first} != TIP "
                "(fleet line order changed or A's copy swapped)")
    body = re.sub(r"<!-- team-footer:start -->.*?<!-- team-footer:end -->",
                  "", readme, flags=re.S)

    # 3. REJECT sweep: sibling fleet addrs never in receive-side layers
    #    (team-footer block exempt — enumerates all 3 by design; require=
    #    values scrubbed — verify-side links, A c47/C c38).
    for name, txt in [(".github/FUNDING.yml", funding),
                      ("README.md (outside team-footer)", scrub_verify_side(body))]:
        for a in addrs(scrub_verify_side(txt)):
            if a in FLEET_OTHERS:
                die(f"{name}: sibling addr {a} ({FLEET_OTHERS[a]}) present — "
                    "tip copy swapped to a fleet sibling")
    ok("REJECT sweep: no sibling fleet addr in any receive-side layer "
       "(require= deep-link values scrubbed, scope flip-proven)")

    if failures:
        print(f"\n{len(failures)} failure(s)")
        sys.exit(1)
    ok("tip parity: every layer agrees on one address")


if __name__ == "__main__":
    main()
