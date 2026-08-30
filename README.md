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

## License

MIT (same as secretgate).
