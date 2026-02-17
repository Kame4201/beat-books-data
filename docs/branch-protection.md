# Branch Protection Rules — `main`

Configured via GitHub API on 2026-02-16.

## Rules

| Rule | Setting |
|------|---------|
| Require pull request reviews | 1 approving review required |
| Required status checks | `lint`, `test` must pass |
| Require branches to be up to date | Yes (`strict: true`) |
| Enforce for admins | No |
| Allow force pushes | No |
| Allow deletions | No |

## Status Checks

The following GitHub Actions jobs must pass before merging to `main`:

- **`lint`** — ruff + black (defined in `.github/workflows/lint.yml`)
- **`test`** — pytest with 70% coverage threshold (defined in `.github/workflows/test.yml`)

## How to Modify

Update via GitHub API:

```bash
gh api repos/Kame4201/beat-books-data/branches/main/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["lint", "test"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": null
}
EOF
```

Or go to: GitHub > Settings > Branches > Branch protection rules > `main`
