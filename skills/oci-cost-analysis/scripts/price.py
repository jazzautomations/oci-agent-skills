#!/usr/bin/env python3
"""Print published bands or a marginal rate and graduated monthly cost."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from lib.pricing import load_prices


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('part_number')
    p.add_argument('currency', nargs='?', default='USD')
    p.add_argument('--quantity', type=str)
    p.add_argument('--cache', type=Path)
    p.add_argument('--offline', action='store_true', help='Use explicit snapshot for reproducibility; no freshness claim')
    args = p.parse_args()
    try:
        book = load_prices(args.cache, args.currency, offline=args.offline)
        product = book.products[args.part_number]
        result = dict(part_number=args.part_number, currency=book.currency, snapshot=book.snapshot, retrieved_at=book.retrieved_at, offline_snapshot=args.offline,
                      basis='list price, pre-discount; PAY_AS_YOU_GO', unit=product['metricName'],
                      bands=[dict(min=str(lo), max=str(hi), rate=str(rate)) for lo,hi,rate in book.bands(args.part_number)])
        if args.quantity is not None:
            result.update(quantity=args.quantity, marginal_rate=str(book.rate(args.part_number,args.quantity)),
                          graduated_cost=str(book.cost(args.part_number,args.quantity)))
        print(json.dumps(result, indent=2))
    except Exception:
        p.exit(1, 'Price lookup unavailable: check currency, SKU, quantity and snapshot.\n')


if __name__ == '__main__':
    main()
