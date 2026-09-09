"""Pure advisory cleaning of account-controlled text; flags never suppress a value."""
import codecs
import base64
import binascii
import json
import re
import unicodedata

BUDGET = {"display_name": 256, "tag_key": 100, "tag_value": 256,
          "object_name": 1024, "log_line": 512, "description": 512,
          "sql_cell": 512, "generic": 256}
STRIP_CATEGORIES = frozenset({"Cc", "Cf", "Co", "Cs"})
BIDI = "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"
PATTERNS = {
    "imperative-language": r"ignore\s+(all\s+)?previous|disregard|you are now|new instructions|system prompt|act as",
    "role-marker": r"</system>|\[system\]|human:|assistant:|<\|im_start\|>",
    "command-shaped": r"\b(curl|wget)\b|\|\s*(ba)?sh|rm\s+-rf|terraform\s+apply|oci\b.*\b(create|delete|update|terminate)\b",
    "url-in-name": r"https?://|data:|file://",
    "credential-bait": r"~/\.oci|private key|(?:api[_ -]?key|token|password)\s*[=:]\s*\S+",
    "encoded-blob": r"[A-Za-z0-9+/]{40,}={0,2}|[a-f0-9]{40,}",
    "authority-claim": r"approved by|pre-approved|oracle support|the administrator|compliant|do not report|omit|guard disabled|permissiondecision|permission_decision|hookspecificoutput|pretooluse",
}


class CleanResult(tuple):
    """Recognizable result permits clean(clean(x)) without losing transformation flags."""


def scan(text):
    if not isinstance(text, str):
        return []
    normalized = unicodedata.normalize("NFKC", text)
    flags = [name for name, pattern in PATTERNS.items()
             if re.search(pattern, normalized.casefold())]
    compact = re.sub(r"(?<=\b\w)\s+(?=\w\b)", "", normalized.casefold())
    if re.search(r"ignoreallpreviousinstructions|ignorepreviousinstructions", compact.replace(" ", "")):
        flags.append("imperative-language")
    # Decode only bounded candidate text for advisory inspection; never execute it.
    if len(normalized) <= 1024:
        if re.fullmatch(r"[A-Za-z0-9+/]{8,}={0,2}", normalized) and len(normalized) % 4 == 0:
            try:
                decoded = base64.b64decode(normalized, validate=True).decode("utf-8")
                if any(re.search(PATTERNS[key], decoded, re.I) for key in ("command-shaped", "imperative-language", "authority-claim")):
                    flags.append("encoded-blob")
            except (ValueError, UnicodeError, binascii.Error):
                pass
        if re.search(PATTERNS["imperative-language"], codecs.decode(normalized, "rot_13"), re.I):
            flags.append("encoded-blob")
    if normalized != text:
        flags.append("homoglyph")
    return list(dict.fromkeys(flags))


def clean(value, budget="generic"):
    if isinstance(value, CleanResult):
        return value
    if not isinstance(value, str):
        return CleanResult((value, []))
    flags = []
    if any(c in BIDI for c in value):
        flags.append("bidi-stripped")
    if any(unicodedata.category(c) in STRIP_CATEGORIES for c in value):
        flags.append("control-separated")
    if any(c in value for c in "\r\n"):
        flags.append("newlines-collapsed")
    text = re.sub(r"[\r\n]+[ \t]*", " ", value)
    text = "".join(" " if c in BIDI or unicodedata.category(c) in STRIP_CATEGORIES else c for c in text)
    limit = BUDGET.get(budget, BUDGET["generic"]) if isinstance(budget, str) else BUDGET["generic"]
    # Scan before truncation too: a suspicious suffix must remain observable as a flag.
    advisory = scan(text)
    if len(text) > limit:
        flags.extend(["truncated", {"original_length": len(text)}])
        text = text[:limit]
    flags.extend(advisory)
    return CleanResult((text, flags))


def field(name, value, kind="generic"):
    text, flags = clean(value, name if name in BUDGET else kind)
    return {"value": text, "flags": flags}


def envelope(items, *, source, kind, complete):
    flags = []

    def visit(value, name="generic"):
        if isinstance(value, dict):
            return {key: visit(item, key) for key, item in value.items()}
        if isinstance(value, list):
            return [visit(item, name) for item in value]
        text, found = clean(value, name)
        for flag in found:
            if flag not in flags:
                flags.append(flag)
        return text

    cleaned = visit(items)
    return {"source": source, "trust": "account-controlled", "kind": kind,
            "complete": bool(complete), "items": cleaned, "flags": flags}


def emit(obj):
    return json.dumps(obj, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
