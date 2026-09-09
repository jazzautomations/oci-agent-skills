"""Observable offline proxies; no model calls, shell execution, or tenancy access."""
import math
import re
import unicodedata
from collections import Counter

STOP = set('a an the and or for of to in on with is it my me do how what which when use not i o a os as de da do dos das e em um uma que como para por meu minha no na com ou isso oci oracle cloud infrastructure'.split())


def tokens(text):
    text = ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c))
    return [w.rstrip('s') for w in re.findall(r'[a-z0-9]+', text) if len(w) > 1 and w not in STOP]


def in_scope(prompt):
    p = prompt.casefold()
    if re.search(r'open container|oci image|oci-c\b|on-prem|on prem|visual designer|jdk license|sem relaç[aã]o com nuvem', p):
        return False
    return bool(re.search(r'\boci\b|oracle cloud|\boke\b|autonomous|exadata|\bapex\b|23ai|26ai|\bfusion\b|netsuite|\btenancy\b|\bcompartment\b|\bocpu|\bvcn\b|\ba1\.flex\b|\bords\b|\bocvs\b', p))


def select(prompt, candidates):
    """BM25-like description matching. Expected labels and case IDs are never inputs."""
    if not candidates or not in_scope(prompt):
        return None
    documents = [tokens(c['name'] + ' ' + c['description'].split('Not for:')[0]) for c in candidates]
    frequency = Counter(word for doc in documents for word in set(doc))
    query = Counter(tokens(prompt))
    scores = []
    for candidate, doc in zip(candidates, documents):
        counts = Counter(doc)
        score = sum(min(query[word], 2) * math.log(1 + len(documents) / (1 + frequency[word])) * counts[word] / (counts[word] + 0.5 + len(doc) / 80) for word in query if word in counts)
        scores.append((score, candidate['name']))
    score, name = max(scores, key=lambda row: (row[0], row[1]))
    return name if score >= 1.5 else None


def routing(rows, candidates, remap):
    output = []
    for row in rows:
        selected = select(row['prompt'], candidates)
        expected = remap.get(row['expected_skill'], row['expected_skill'])
        output.append({'id': row['id'], 'selected': selected, 'expected': expected, 'correct': selected == expected})
    return output


def negative(rows, candidates):
    return [{'id': row['id'], 'selected': select(row['prompt'], candidates)} for row in rows]


def safety(fixtures, clean):
    output = []
    for fixture in fixtures:
        result = clean(fixture['text'])
        value, flags = result
        output.append({'id': fixture['id'], 'flagged': bool(flags), 'returned': bool(value),
                       'idempotent': clean(result) == result,
                       'pass': bool(flags) and bool(value) and clean(result) == result})
    return output
