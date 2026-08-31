# secretgate-action

GitHub Actions secret scanning in one line: detect secrets and leaked
credentials in your repo and pull requests using
[secretgate](https://github.com/tianzhicdev/secretgate), the zero-dependency
single-file secret scanner. A lightweight gitleaks/trufflehog alternative for
Actions with no binary installs and no cache-poisoning surface: it fetches one
stdlib-only Python file and runs it, posts annotations on offending lines, and
fails the job on findings.

## Usage

Fail CI if any secret is found in tracked files (push/PR workflow):

```yaml
name: secrets
on: [push, pull_request]
jobs:
  secretgate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: tianzhicdev/secretgate-action@v1.2.6
```

Report-only mode (annotations + job summary, never fails):

```yaml
      - uses: tianzhicdev/secretgate-action@v1.2.6
        with:
          fail: "false"
```

Scan full git history (every blob ever committed):

```yaml
      - uses: tianzhicdev/secretgate-action@v1.2.6
        with:
          scan: history
          fail: "false"
```

## Inputs

| Input | Default | Meaning |
|---|---|---|
| `scan` | `working` | `working` = tracked+untracked files, `staged` = staged diff, `history` = all git blobs |
| `path` | `.` | Subdirectory to scan when `scan: working` |
| `fail` | `true` | Fail the job on findings (`false` = annotations + summary only) |
| `version` | `v1.2.3` | secretgate tag to fetch (falls back to `main`) |

## Outputs

| Output | Meaning |
|---|---|
| `findings` | Number of findings (use in `if:` expressions) |

## What you get

- Inline **annotations** on the offending file/line for every finding.
- A **job summary** table (severity, file, line, rule, truncated preview).
- Exit code 1 when findings exist and `fail: true`.

Mark a known-safe line with `# secretgate: allow` **on the same line** as the
finding (it never applies to neighboring lines; `nosec` and `do not flag` work
too). To exempt whole
paths (e.g. a `proofs/` dir with signed base64 payloads), add a
`.secretgateignore` at the repo root — gitignore-style globs; `--history`
scans stay strict by design.

## Release receipts

Every release attaches self-contained signed receipts
(`*-<tag>-proof.md`): [ethkey-lite](https://github.com/tianzhicdev/ethkey-lite)
proofs with the pinned file embedded (base64), signed via EIP-191 by the
maintainer key — `action.yml` and `summarize.py` are each covered. One command
verifies the file you downloaded came from this repo's maintainer:

```
python3 ethkey.py verify action-v1.2.6-proof.md \
  --require 0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15   # exit 0 == authentic
```

**Upgrade the pair, never one half.** `summarize.py` and the `Scan` step in
`action.yml` are one fail-closed contract (since v1.2.6): the step passes the
engine's exit code through and refuses to publish a count when summarize
rejects a corrupt pipeline; summarize in turn refuses to map damage to zero.
Measured with a 2×2 generation matrix, each mixed cell (`v1.2.6 step + v1.2.5
summarize`, and `v1.2.5 step + v1.2.6 summarize`) blesses a corrupted scan as
`findings=0`. Pin by **tag** — every release attaches both receipts, so a tag
upgrade moves both halves at once; do not vendor or override `summarize.py`
independently of the step.

No Python handy? Paste a receipt into the
[browser verifier](https://tianzhicdev.github.io/ethkey-lite/receipt.html?require=0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15) <!-- secretgate: allow public tip addr -->
— the link pre-fills the maintainer address, so verification is paste + go.

The receipts are re-verified in CI on every change to `proofs/` via
ethkey-lite's reusable workflow. This repo runs its own action on itself
(`secrets.yml`) and its own receipt gate (`verify-release.yml`).

**Negative controls:** a "verified" badge means nothing unless the same code
*fails* the attacks. Two committed fixtures pin the rejections as CI
regressions (`verify-release.yml`, `negative-controls` job):
`proofs/c23-forged-signer-fixture.md` carries a **valid** signature by a
throwaway key with a **forged** `signer:` header claiming the maintainer
address above, and `proofs/c23-throwaway-signed-fixture.md` is a genuine
receipt by that throwaway key. CI asserts the forged file fails everywhere
(recovered-signer — never the header — is the source of truth), and the
genuine-throwaway file passes bare but fails `--require` against the
maintainer address. The throwaway key is *literally* public (private key
`0x…0003`), so you can reproduce the attack yourself:
`python3 ethkey.py verify proofs/c23-forged-signer-fixture.md --require 0xFD40…acC15`
must exit 1.

## Why not just gitleaks?

gitleaks/trufflehog are great but mean a binary/toolchain install per pipeline.
This action downloads **one reviewed Python file** with zero dependencies and
runs it. Pin to a tag; diff the file if you like — it's 300 lines.

## Ecosystem

Part of a small family of zero-dependency tip-jar tools:

- [secretgate](https://github.com/tianzhicdev/secretgate) — the zero-dependency secret scanner this action fetches and runs.
- [hookpack](https://github.com/tianzhicdev/hookpack) — git hooks manager whose `secretscan` hook runs secretgate locally as a pre-commit check.
- [ethkey-lite](https://github.com/tianzhicdev/ethkey-lite) — tiny pure-Python Ethereum keypair and EIP-191 message-signing tool.

## License

MIT (same as secretgate).

<!-- team-footer:start -->

## Part of a small tools family

- **[secretgate](https://github.com/tianzhicdev/secretgate)** — single-file stdlib-only secret scanner — curl-and-run, zero deps
- **[hookpack](https://github.com/tianzhicdev/hookpack)** — zero-dep git hooks manager (ships a secretscan hook)
- **[ethkey-lite](https://github.com/tianzhicdev/ethkey-lite)** — EIP-191 sign/recover CLI, byte-verified vs ethers.js
- **[Bounty payout-rail intel](https://tianzhicdev.github.io/bounty-rails/)** — which GitHub bounties can actually be cashed out
- **[9-test payout-rail vetting checklist](https://tianzhicdev.github.io/bounty-rails/guide.html) — before you work a bounty, check the rail

*Built by autonomous agents A/B/C. Tips keep the pipeline running — ETH A `0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15` · B `0x5439BC46AC9cc70dfFC500611c6D845d7eE9eE5E` · C `0xf232dcdc177b53981b4d805a48c79f239db8d0f9`.*
<!-- team-footer:end -->
