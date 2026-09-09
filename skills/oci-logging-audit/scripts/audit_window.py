#!/usr/bin/env python3
'''Chunk one bounded Audit range into per-call windows and count event types. Reads only.'''
import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from lib.oci_ro import run
from lib.sanitize import emit

RETENTION = timedelta(days=365)
MAX_CHUNKS = 200
EVENT_TYPE = re.compile(r'^[A-Za-z0-9._-]{1,120}$')


def stamp(value):
    moment = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if moment.tzinfo is None:
        raise ValueError('Timestamps must be timezone-aware')
    return moment.astimezone(timezone.utc)


def slices(start, end, hours):
    if not timedelta(0) < end - start:
        raise ValueError('End must be after start')
    if datetime.now(timezone.utc) - start > RETENTION:
        raise ValueError('Audit keeps 365 days; older ranges need a Connector Hub archive')
    step = timedelta(hours=hours)
    count = -(-(end - start) // step)
    if count > MAX_CHUNKS:
        raise ValueError('Range needs %d calls; narrow it or raise CHUNK_HOURS' % count)
    edges = []
    while start < end:
        edges.append((start, min(start + step, end)))
        start += step
    return edges


def tally(rows, counts):
    if not isinstance(rows, list):
        raise ValueError('Unexpected response')
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('k'), str):
            raise ValueError('Unexpected event')
        key = row['k'] if EVENT_TYPE.match(row['k']) else 'unparsed-event-type'
        counts[key] = counts.get(key, 0) + 1
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog="Required env: PROFILE REGION COMPARTMENT_ID START_TIME END_TIME; optional CHUNK_HOURS (1–24, default 6). JSON output is unconditional.")
    parser.add_argument("--json", action="store_true", help="Emit JSON (default)")
    parser.parse_args()
    required = ('PROFILE', 'REGION', 'COMPARTMENT_ID', 'START_TIME', 'END_TIME')
    if not all(os.environ.get(key) for key in required):
        parser.error('Set ' + ', '.join(required) + '; optional CHUNK_HOURS (default 6)')
    try:
        hours = int(os.environ.get('CHUNK_HOURS', '6'))
        if not 1 <= hours <= 24:
            raise ValueError('CHUNK_HOURS must be 1-24')
        windows = slices(stamp(os.environ['START_TIME']), stamp(os.environ['END_TIME']), hours)
    except (ValueError, TypeError) as exc:
        print(emit({'ok': False, 'kind': 'invalid_window', 'detail': str(exc)}))
        return 1
    counts, total = {}, 0
    for begin, finish in windows:
        result = run(['audit', 'event', 'list',
                      '--compartment-id', os.environ['COMPARTMENT_ID'],
                      '--start-time', begin.strftime('%Y-%m-%dT%H:%M:%SZ'),
                      '--end-time', finish.strftime('%Y-%m-%dT%H:%M:%SZ'),
                      '--query', 'data[].{t:"event-time",k:"event-type"}', '--no-retry'],
                     profile=os.environ['PROFILE'], region=os.environ['REGION'], sanitize=False)
        try:
            if not result['ok']:
                raise ValueError('Read failed')
            total += tally(result['data'] or [], counts)
        except (ValueError, KeyError, TypeError):
            print(emit({'ok': False, 'kind': 'failed_or_malformed_read',
                        'chunks_done': windows.index((begin, finish))}))
            return 2
    print(emit({'ok': True, 'chunks': len(windows), 'chunk_hours': hours, 'events': total,
                'event_types': counts, 'page_bounded': True, 'created': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
