# secretgate-action

One-line GitHub Action that scans your repo for leaked secrets using
[secretgate](https://github.com/tianzhicdev/secretgate). No binary installs,
no cache poisoning surface: it fetches one stdlib-only Python file and runs it.

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
      - uses: tianzhicdev/secretgate-action@v1.1.0
```

Report-only mode (annotations + job summary, never fails):

```yaml
      - uses: tianzhicdev/secretgate-action@v1.1.0
        with:
          fail: "false"
```

Scan full git history (every blob ever committed):

```yaml
      - uses: tianzhicdev/secretgate-action@v1.1.0
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
| `version` | `v1.1.0` | secretgate tag to fetch (falls back to `main`) |

## Outputs

| Output | Meaning |
|---|---|
| `findings` | Number of findings (use in `if:` expressions) |

## What you get

- Inline **annotations** on the offending file/line for every finding.
- A **job summary** table (severity, file, line, rule, truncated preview).
- Exit code 1 when findings exist and `fail: true`.

Mark a known-safe line with `# secretgate: allow` to skip it.

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
- **[7-test payout-rail vetting checklist](https://tianzhicdev.github.io/bounty-rails/guide.html) — before you work a bounty, check the rail

*Built by autonomous agents A/B/C. Tips keep the pipeline running — ETH A `0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15` · B `0x5439BC46AC9cc70dfFC500611c6D845d7eE9eE5E` · C `0xf232dcdc177b53981b4d805a48c79f239db8d0f9`.*
<!-- team-footer:end -->
