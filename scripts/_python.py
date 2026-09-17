#!/usr/bin/env python3
"""Cross-platform launcher: run a toolkit script with an interpreter that has the
optional deps (watchdog, pyperclip) available.

The VS Code tasks call this instead of a hardcoded interpreter path, so one
tasks.json works on macOS and Windows. Resolution order:

  1. $LATEX_NOTES_PYTHON            — explicit override, if you set one
  2. the toolkit venv, if present   — ~/.local/share/ajnotes-venv (macOS/Linux)
                                      %LOCALAPPDATA%\\ajnotes-venv (Windows)
  3. the interpreter running this   — plain `python3` / `py`, deps or not

Usage:  python3 _python.py <script.py> [args...]
"""
import os
import subprocess
import sys
from pathlib import Path


def _venv_python():
    if os.name == 'nt':
        base = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'ajnotes-venv'
        return base / 'Scripts' / 'python.exe'
    return Path.home() / '.local' / 'share' / 'ajnotes-venv' / 'bin' / 'python'


def interpreter():
    override = os.environ.get('LATEX_NOTES_PYTHON')
    if override:
        return override
    venv = _venv_python()
    if venv.exists():
        return str(venv)
    return sys.executable


def main():
    if len(sys.argv) < 2:
        print('usage: _python.py <script.py> [args...]', file=sys.stderr)
        return 2
    script = Path(__file__).resolve().parent / sys.argv[1]
    return subprocess.run([interpreter(), str(script), *sys.argv[2:]]).returncode


if __name__ == '__main__':
    sys.exit(main())
