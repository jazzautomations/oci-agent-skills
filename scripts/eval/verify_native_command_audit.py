"""Recompute recorded inert-command adjudication using the pinned CLI environment."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('audit', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='oci-syntax-check-') as directory:
        output = Path(directory) / 'audit.json'
        subprocess.run([sys.executable, str(Path(__file__).with_name('audit_native_commands.py')),
                        str(args.report), '--out', str(output)], check=True)
        if json.loads(output.read_text()) != json.loads(args.audit.read_text()):
            raise ValueError('Recorded syntax adjudication differs from recomputation')
    print(json.dumps({'verified': True, 'executed_model_commands': 0}))


if __name__ == '__main__':
    main()
