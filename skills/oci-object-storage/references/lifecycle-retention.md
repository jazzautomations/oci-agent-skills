# Lifecycle, versioning and retention
Source: research/04c Object Storage; research/09b §29.
Lifecycle put replaces the entire rule array. Preserve the old policy, merge locally and review every prefix, action and version target before proposing replacement. Confirm the complex parameter is an array rather than a wrapper object.
Versioned deletions can leave prior versions billing. Lifecycle rules for current objects, previous versions and multipart uploads have different targets; check the installed parameter schema and service documentation rather than copying a guessed ABORT action.
Archive transitions can break readers until an authorized restore completes; do not promise a fixed restore duration.
Retention locks can be irreversible and prevent deletion even when lifecycle rules request it. Record retention duration, legal constraints and lock state before discussing cleanup. Never propose a lock as a reversible experiment.
