Purpose: write an OCI CLI `--query` that returns the right rows — envelope, key case, the 20 live-run patterns, the traps.
Source: research/04a-cli-auth-ergonomics.md (§2.1–2.3, §3 P6/P7), research/10a-sdk-developer-patterns.md (§2.7–2.10); generated 2026-09-08; verified-on CLI 3.91.0

## 1. Where a query starts

`--query` runs on the **whole envelope**: paths start at `data` (`data.items` for
`search resource structured-search`) [verified]. `--output` is `json` or `table` only in
3.91.0 — build TSV with `--query` + `join()`. `--query query://<name>` resolves a named
query from `[OCI_CLI_CANNED_QUERIES]` [verified].

Single-quote the query and use backtick JSON literals (`` `ACTIVE` ``), or double-quote it
and use raw strings (`--query "data[?name=='x'].id"`). Both verified; never let a backtick
reach the shell unquoted.

## 2. Key case — three vocabularies

| Surface | Case | Example |
|---|---|---|
| CLI response JSON (what `--query` sees) | kebab-case | `"lifecycle-state"`, `"display-name"` |
| Search `--query-text`, `--from-json`, `--generate-*-json-input` | camelCase | `lifeCycleState`, `displayName` |
| `--skip-deserialization` output — only leaf that takes it: `oci audit event list` | camelCase again | `eventName` |
| Python SDK model attributes (not JMESPath) | snake_case | `.lifecycle_state`, `e.target_service` |

**A hyphenated key MUST be double-quoted in JMESPath.** `data[0]."lifecycle-state"` works;
unquoted `data[?lifecycle-state=='ACTIVE']` parses as *subtraction* and returns null — no
error, just a wrong answer [verified live]. Discover real keys with `keys(data[0])`.

## 3. The 20 patterns (all executed live)

| # | Pattern | Query |
|---|---|---|
| 1 | count rows | `length(data)` |
| 2 | pluck one field | `data[*].id` |
| 3 | first OCID as a bare string | `data[0].id` + `--raw-output` |
| 4 | rename/project columns | `data[*].{name:"display-name",state:"lifecycle-state",ocid:id}` |
| 5 | filter on a hyphenated key | ``data[?"lifecycle-state"==`ACTIVE`]`` |
| 6 | quote-swapped form | `"data[?name=='my-vcn'].id \| [0]"` |
| 7 | negative filter | ``data[?"lifecycle-state"!=`TERMINATED`]`` |
| 8 | substring match | ``data[?contains(name, `prod`)].name`` |
| 9 | prefix match | ``data[?starts_with(name, `oke-`)].name`` |
| 10 | compound AND | ``data[?"lifecycle-state"==`RUNNING` && contains(shape, `Flex`)]`` |
| 11 | compound OR | ``data[?"lifecycle-state"==`ACTIVE` \|\| "lifecycle-state"==`AVAILABLE`]`` |
| 12 | null check | `data[?description!=null]` |
| 13 | sort ascending | `sort_by(data, &"time-created")[*].name` |
| 14 | sort descending | `reverse(sort_by(data, &"time-created"))[*].name` |
| 15 | top-N after sorting | `reverse(sort_by(data,&"time-created"))[0:5].{n:"display-name",t:"time-created"}` |
| 16 | slice | `data[0:3]` |
| 17 | CSV/TSV line | `join(',', data[*].name)` + `--raw-output` |
| 18 | discover the schema | `keys(data[0])` |
| 19 | count matches inline | ``data[?starts_with(name, `o`)] \| length(@)`` |
| 20 | Search results (`data.items`) | `data.items[*].{n:"display-name",t:"resource-type",c:"compartment-id"}` |

## 4. Traps

| Trap | What happens | Correct move |
|---|---|---|
| Quotes around a captured OCID | `data[0].id` returns `"ocid1..."` with quotes, poisoning the var | Add `--raw-output` — strips quotes only when the query yields a single string [verified] |
| Unquoted hyphenated key | Parsed as subtraction, result `null`, exit 0 | Double-quote the key (§2) |
| `--query` is not pagination | Filtering runs on the page already fetched; `length(data)` on a truncated list is a wrong count | Pass `--all` on any `list` that offers it; the truncation `WARNING` goes to **stderr**, invisible to a stdout-only agent [verified live] |
| `--all` + `--limit` together | `UsageError: If you provide the --all option you cannot provide the --limit option` [verified] | Pick one; `--page-size N` tunes pages, `--page <token>` resumes |
| `--skip-deserialization` (1 of 9145 leaves: `oci audit event list`) | Output flips to camelCase; kebab-key queries return null | Rewrite the paths, or drop the flag |
| Unnamed table columns | `data[*].[a,b]` with `--output table` has no headers | Use `data[].{k:v}` for named headers |
| Porting a `--query` into SDK code | The SDK returns model objects, not the CLI envelope | Use its paginators: `list_call_get_all_results` / `..._generator` / `list_call_get_up_to_limit` (Python); Go has no helper, loop on `resp.OpcNextPage`, Java `listXxxRecordIterator`, TS `listAllXxx` [unverified] |

## 5. Links
- [JMESPath spec](https://jmespath.org/specification.html) · [CLI input/output](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliusing.htm) · [API pagination](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/usingapi.htm) (all 200, 2026-09-08)
