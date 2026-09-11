# Authorized history cleanup — September 11, 2026

The owner explicitly authorized replacing published history. Both published
branches were updated atomically with exact old-revision leases: concurrent remote
changes would have refused publication. Repository visibility remained private.

| Branch | Previous published tip | Clean published tip |
|---|---|---|
| main | b22f39873014d19a97c2066459b81024e3e979ca | f0e920fd0ed1d42d77dff53d64beea7c330d60bb |
| v2-foundation | 0c52607b69f9305474c7b7ee1b15fe5180ebd136 | 625336afeb05044487d7e1c50079d98acdaedf08 |

The already-reviewed replacement changes one historical blob containing email
values. Historical branch-tip trees were compared byte-for-byte before adding the
new validation commit. That commit publishes the previously local OCI integration,
RAG and benchmark work. Its source tree was also checked unchanged across the
parent-history replacement. No OCI resources or credentials were changed.

Before publication, a private complete Git bundle preserved all local refs,
including the new validation snapshot; a separate archive preserved tracked and
untracked workspace files. `CODEX-STATUS.md` remains untracked and unpublished.
The backups are outside the repository and were verified before the update.

Both the local all-ref scan and an independent fresh mirror downloaded from
GitHub report zero findings; see the [publication evidence](evidence/published-history-cleanup-2026-09-11.json).
Scope: reachable textual patch bodies, not GitHub's
unreachable-object caches, old CI artifacts, private backups or other people's
clones. Commit author/committer identities and message trailers remain outside
the existing scanner's documented scope. No remote cache-erasure claim is made.

## Existing clones

Commit IDs changed. Preserve any local work before synchronizing; a fresh clone
is the simplest clean starting point. Reapply needed local changes onto the clean
history instead of merging the old history back. Local OCI configuration is
independent of this Git operation and is unaffected.

The validation workflow now requests complete history and runs the history
scanner, so future pushes cannot silently reintroduce the removed patch content.
This closes the history finding only; other release criteria remain separately
reported in the [validation matrix](validation-matrix.md).
