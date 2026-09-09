#!/usr/bin/env python3
"""Compatibility entrypoint for V19/V20; use --negatives for the hard negative gate."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/eval/run.py'), run_name='__main__')
