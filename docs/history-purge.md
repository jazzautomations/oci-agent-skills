# Historical content cleanup before public release

Owner: **repository history owner**. The repository has already been pushed to
private GitHub. The earlier pre-push plan below was not executed; current
patch-body findings remain recorded in V22. Coordinate any history rewrite with
collaborators and preserve a private backup first. This document is a procedure,
not authorization to force-push or change repository visibility.

The scanner checks textual patch bodies, including additions and deletions.
Author/committer metadata and commit-message `Co-Authored-By` / `Claude-Session`
trailers are exempt. The same text inside a tracked file remains patch content.
The scanner reports counts and locations, never matched addresses. Binary content
and arbitrary account/display names remain outside this heuristic check.

## Exact pre-purge evidence

| Commit / side | Path | Blob | Email occurrences in blob |
|---|---|---|---|
| `85815c5`, added | `docs/final-audit-findings.json` | `268721e42eb20f5c37ef231c09caed3a2ccad0fc` | 2 |
| `a320700`, removed | `docs/final-audit-findings.json` | `268721e42eb20f5c37ef231c09caed3a2ccad0fc` | 2 |
| `a320700`, replacement | `docs/final-audit-findings.json` | `2d16d40ca8c14c479ef89f40c8e7808f45a41a0b` | 0 |

There is one offending blob, referenced by two patches. The four patch occurrences
are not four distinct leaks. The replacement in `a320700` is clean; deleting the
address from the current tree did not remove the older reachable blob. These IDs
identify the original history and will change after a purge.

## Owner-operated content purge

Save uncommitted and untracked work (including handoff scratch files) privately
outside the checkout, and make a private offline backup. Keep the backup local:
it contains the original history. Install `git-filter-repo` locally before running
the following from the repository root. The replacement rules are created with
private permissions outside the checkout; no address is printed or pasted into a
tracked file.

```bash
# MUTATING — not run in this repo; [shape-verified] from upstream documentation.
# rollback: restore the private bundle into a separate checkout and restore saved local work.
set -euo pipefail
git bundle create ../oci-agent-skills-before-purge.bundle --all
export HISTORY_PURGE_RULES="$(mktemp)"
trap 'rm -f "$HISTORY_PURGE_RULES"' EXIT
python3 - <<'PY'
import os
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0, 'scripts/ci')
from check_history import HISTORY_PATTERNS
blob = '268721e42eb20f5c37ef231c09caed3a2ccad0fc'
body = subprocess.check_output(['git', 'cat-file', 'blob', blob]).decode('utf-8')
addresses = sorted(set(re.findall(HISTORY_PATTERNS['email'], body)))
if not addresses:
    raise SystemExit('Expected historical email evidence not found; stop and review.')
rules = Path(os.environ['HISTORY_PURGE_RULES'])
rules.chmod(0o600)
rules.write_text(''.join('literal:' + value + '==><redacted-email>\n' for value in addresses))
PY
# Stop if rule generation failed; never proceed with an empty replacement file.
test -s "$HISTORY_PURGE_RULES"
git filter-repo --force --replace-text "$HISTORY_PURGE_RULES" --replace-refs delete-no-add
python3 scripts/ci/check_history.py
python3 scripts/ci/check_no_secrets.py
```

`--force` permits rewriting this existing checkout after the backup; all reachable
refs are in scope because no `--refs` restriction is supplied. `--replace-text`
rewrites file contents, while `--replace-refs delete-no-add` avoids preserving old
history through replacement refs. The content replacement rules do not target commit-message trailers or author
identities. See the [upstream git-filter-repo
manual](https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt)
for replacement syntax, force/backup behavior, and mailmap support.

Require a clean history scan, rerun pytest and strict validators, and regenerate
the release matrix after rewriting. Other red release/evaluation gates still need
their named owners. Do not publish the original backup or reintroduce its refs.
For rollback, clone the private bundle into a separate directory and restore the
saved local files there; that restored history again requires a purge before any
push.

## Optional author identity rewrite

Identity changes are the owner's choice and are not required by the patch-body
leak gate. Before the content purge, create a private mailmap file outside the
checkout. Use the format below, replacing example identities privately:

```text
Chosen Name <new@example.invalid> <old@example.invalid>
```

Set `HISTORY_PURGE_MAILMAP` to that private file. To apply both changes in one
rewrite, replace the `git filter-repo` invocation above with:

```bash
# MUTATING — not run in this repo; [shape-verified] from upstream documentation.
# rollback: restore the private pre-purge bundle and saved local work.
git filter-repo --force --replace-text "$HISTORY_PURGE_RULES" \
  --mailmap "$HISTORY_PURGE_MAILMAP" --replace-refs delete-no-add
```

The mailmap rewrites matching author, committer and tagger identities. It does not
rewrite commit-message trailers; those remain exempt. Remove the private mailmap
and replacement files after validation, and set the desired local Git identity
for future commits separately.
