"""Shared helpers for the Inkscape figure workflow.

Adapted from Gilles Castel's inkscape-figures (https://castel.dev/post/lecture-notes-2/),
trimmed to the cross-platform core: create a figure from a template, and export
an .svg to .pdf + .pdf_tex (a vector figure whose labels are typeset by LaTeX).

The Linux/Vim-only parts of the original (inotify/fswatch, daemonize, rofi) are
not used here — see watch-figures.py for a watchdog-based, cross-platform watcher.
"""
import re
import subprocess
import sys
from pathlib import Path

from config import INKSCAPE

TEMPLATE = Path(__file__).resolve().parent / 'figure-template.svg'


def beautify(name):
    """'my-figure' -> 'My Figure' for captions/labels."""
    return name.replace('_', ' ').replace('-', ' ').title()


def slugify(title):
    """'My Figure' -> 'my-figure' for file names."""
    return title.strip().replace(' ', '-').lower()


def latex_template(name, title):
    """The LaTeX snippet that includes a figure (uses \\incfig from preamble)."""
    return '\n'.join((
        r"\begin{figure}[ht]",
        r"    \centering",
        rf"    \incfig{{{name}}}",
        rf"    \caption{{{title}}}",
        rf"    \label{{fig:{name}}}",
        r"\end{figure}",
    ))


def open_in_inkscape(path):
    """Open a figure for editing in Inkscape.

    On macOS go through `open -a` (Launch Services): it hands the file to an
    already-running Inkscape instead of starting a brand-new process per figure,
    and focuses the app. Other platforms spawn the binary directly, as before.
    """
    path = str(path)
    if sys.platform == 'darwin':
        app = INKSCAPE
        # /Applications/Inkscape.app/Contents/MacOS/inkscape -> the .app bundle
        marker = '.app/Contents/MacOS/'
        if marker in app:
            app = app[:app.index(marker) + len('.app')]
        try:
            subprocess.Popen(['open', '-a', app, path])
            return
        except FileNotFoundError:
            pass  # fall through to the direct launch below
    try:
        subprocess.Popen([INKSCAPE, path])
    except FileNotFoundError:
        print(f'Could not run Inkscape ({INKSCAPE!r}). Install Inkscape and put '
              f'it on your PATH, or set INKSCAPE in config.py.')


def _inkscape_version():
    try:
        out = subprocess.check_output([INKSCAPE, '--version'], universal_newlines=True)
    except FileNotFoundError:
        raise SystemExit(
            f'Could not run Inkscape ({INKSCAPE!r}). Install Inkscape and put it '
            f'on your PATH, or set INKSCAPE in config.py.')
    version = re.findall(r'[0-9.]+', out)[0]
    parts = [int(p) for p in version.split('.')]
    return parts + [0] * (3 - len(parts))


def export_figure(svg_path):
    """Export an .svg to .pdf + .pdf_tex next to it. Returns True on success."""
    svg_path = Path(svg_path)
    pdf_path = svg_path.with_suffix('.pdf')

    if _inkscape_version() < [1, 0, 0]:
        command = [
            INKSCAPE,
            '--export-area-page',
            '--export-dpi', '300',
            '--export-pdf', str(pdf_path),
            '--export-latex', str(svg_path),
        ]
    else:
        command = [
            INKSCAPE, str(svg_path),
            '--export-area-page',
            '--export-dpi', '300',
            '--export-type=pdf',
            '--export-latex',
            '--export-filename', str(pdf_path),
        ]

    return subprocess.run(command).returncode == 0
