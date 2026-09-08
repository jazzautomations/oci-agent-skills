"""Redact identifiers and credential-shaped values from diagnostic text."""
import re


def redact(text):
    text = re.sub(r'-----BEGIN [^-]*PRIVATE KEY-----.*?(?:-----END [^-]*PRIVATE KEY-----|$)', '[redacted private key]', text, flags=re.S)
    text = re.sub(r'ocid1\.([a-z0-9_-]+)\.[A-Za-z0-9_.-]+', r'ocid1.\1...redacted', text)
    text = re.sub(r'(?i)\bBearer\s+\S+', 'Bearer [redacted]', text)
    text = re.sub(r'(?i)(password|authToken|access[-_]uri|security_token|token|api[-_]key)(["\s]*[:=]["\s]*)[^\s,;}]+', r'\1=[redacted]', text)
    text = re.sub(r'/p/[^/\s]+/n/', '/p/[redacted]/n/', text)
    return text
