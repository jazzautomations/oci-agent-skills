"""Public OCI price bands. Decimal math; tenancy-wide graduated allowances."""
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.request import build_opener, HTTPRedirectHandler

ENDPOINT = 'https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/'


def number(value):
    try:
        value = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Invalid quantity or price') from exc
    if not value.is_finite() or value < 0:
        raise ValueError('Quantity and price must be finite and nonnegative')
    return value


class PriceBook:
    def __init__(self, payload, currency='USD'):
        self.currency = currency
        self.snapshot = payload['lastUpdated']
        self.retrieved_at = payload.get('_retrieved_at')
        self.products = {p['partNumber']: p for p in payload['items']}

    def bands(self, part):
        product = self.products[part]
        loc = next(x for x in product['currencyCodeLocalizations'] if x['currencyCode'] == self.currency)
        bands = sorted([(number(b.get('rangeMin', 0)), number(b['rangeMax']) if b.get('rangeMax') is not None else Decimal('Infinity'), number(b['value']))
                        for b in loc['prices'] if b['model'] == 'PAY_AS_YOU_GO'])
        if not bands or bands[0][0] != 0 or any(a[1] != b[0] for a,b in zip(bands,bands[1:])) or any(lo >= hi for lo,hi,_ in bands):
            raise ValueError('Missing, overlapping or discontinuous PAY_AS_YOU_GO bands')
        return bands

    def rate(self, part, quantity):
        q = number(quantity)
        for lo, hi, rate in self.bands(part):
            if lo <= q < hi:
                return rate
        raise ValueError('Quantity outside published bands')

    def cost(self, part, quantity):
        q = number(quantity)
        bands = self.bands(part)
        if q > bands[-1][1]:
            raise ValueError('Quantity outside published bands')
        return sum((max(Decimal(0), min(q, hi) - lo) * rate for lo,hi,rate in bands), Decimal(0))

    def avoided(self, part, total_quantity, removed_quantity):
        total, removed = number(total_quantity), number(removed_quantity)
        if removed > total:
            raise ValueError('Removed quantity exceeds tenancy total')
        return self.cost(part, total) - self.cost(part, total - removed)


def load_prices(cache=None, currency='USD', *, offline=False, max_age_hours=24):
    if not re.fullmatch('[A-Z]{3}', currency):
        raise ValueError('Currency must be three uppercase letters')
    ttl = number(max_age_hours)
    if cache and Path(cache).exists():
        if Path(cache).stat().st_size > 4_000_000:
            raise ValueError('Price cache exceeds bound')
        payload = json.loads(Path(cache).read_text())
        if offline:
            return PriceBook(payload, currency)
        try:
            fetched = datetime.fromisoformat(payload['_retrieved_at'].replace('Z', '+00:00'))
            age = (datetime.now(timezone.utc) - fetched).total_seconds()
        except (KeyError, TypeError, ValueError):
            age = -1
        cached_currency = payload.get('_currency')
        if cached_currency == currency and 0 <= age < float(ttl) * 3600:
            return PriceBook(payload, currency)
    if offline:
        raise ValueError('Offline pricing requires an existing cache')
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    with build_opener(NoRedirect).open(ENDPOINT + '?currencyCode=' + currency, timeout=30) as response:
        raw = response.read(4_000_001)
        if len(raw) > 4_000_000:
            raise ValueError('Public price response exceeds bound')
        payload = json.loads(raw)
    payload['_retrieved_at'] = datetime.now(timezone.utc).isoformat()
    payload['_currency'] = currency
    book = PriceBook(payload, currency)
    if cache:
        path = Path(cache)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload))
    return book
