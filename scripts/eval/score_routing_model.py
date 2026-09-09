"""Score saved judge labels against the frozen corpus and explicit skill merges."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def score(path):
    corpus = json.loads((ROOT/'evals/corpus/eval-corpus.json').read_text())
    remap = json.loads((ROOT/'evals/remap.json').read_text())
    expected = {r['id']:remap.get(r['expected_skill'],r['expected_skill']) for r in corpus['routing']}
    negatives = {r['id'] for r in corpus['negatives']}
    data = json.loads(Path(path).read_text())
    labels = {row['id']:row['skill'] for row in data['labels']}
    if len(labels) != len(data['labels']) or set(labels) != set(expected) | negatives:
        raise ValueError('Judge labels must cover each corpus ID exactly once')
    fired = sum(bool(labels[i]) for i in expected)
    exact = sum(labels[i] == e for i,e in expected.items())
    negative_firings = sum(bool(labels[i]) for i in negatives)
    return data['arm'],fired,exact,negative_firings,len(expected),len(negatives)


def main():
    for path in sys.argv[1:]:
        arm,fired,exact,negative_firings,total,negatives=score(path)
        print(f'{arm:12s} fired on OCI prompts {fired}/{total} ({100*fired/total:.1f}%) | exact expected skill {exact}/{total} ({100*exact/total:.1f}%) | fired on negatives {negative_firings}/{negatives}')


if __name__ == '__main__':
    main()
