"""Usage API window and row contracts, independent of cloud authentication."""
from datetime import datetime, timedelta, timezone
import math


def utc(value):
    dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def window(start, end, granularity, *, now=None, delta=False, groups=()):
    start, end = utc(start), utc(end)
    now = now or datetime.now(timezone.utc)
    if granularity not in {'MONTHLY','DAILY','HOURLY'} or len(groups) > 4:
        raise ValueError('Unsupported granularity or more than four grouping dimensions')
    if granularity == 'MONTHLY':
        start = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not start < end or end > now:
        raise ValueError('Empty, reversed or future actual-cost window')
    if granularity == 'HOURLY' and (end-start > timedelta(hours=36) or start < now-timedelta(days=31)):
        raise ValueError('HOURLY requires at most 36 hours starting within 31 days')
    if delta and end > now-timedelta(hours=48):
        raise ValueError('Cost deltas exclude the last 48 hours')
    return start, end


def rows(payload, start, end, *, monthly=False):
    """Reject silently widened windows, preserve currency and credits, drop zero/null."""
    if isinstance(payload,dict):
        payload = payload.get('data', payload)
    if isinstance(payload,dict):
        payload = payload.get('items', [])
    if not isinstance(payload,list):
        raise ValueError('Invalid usage response')
    result = []
    for row in payload:
        lo,hi = row.get('time-usage-started'), row.get('time-usage-ended')
        if not lo or not hi or utc(lo)<start or utc(hi)>end or utc(lo)>=utc(hi):
            raise ValueError('Service echoed a different covered window')
        if monthly and (utc(lo).day != 1 or utc(hi).day != 1):
            raise ValueError('Service echoed partial MONTHLY buckets')
        amount = row.get('computed-amount')
        if amount is None or float(amount)==0:
            continue
        currency=row.get('currency')
        if not math.isfinite(float(amount)) or not currency or not currency.strip() or currency=='NA':
            raise ValueError('Unusable cost or currency')
        result.append(row)
    return sorted(result,key=lambda r: r['time-usage-started'])
