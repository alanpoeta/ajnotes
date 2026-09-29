import os
import subprocess
from pathlib import Path


# Fallback document language when a course's main.tex has no recognisable option.
DEFAULT_LANGUAGE = 'english'


# Command used to run Inkscape (for the figure scripts). Auto-detected per OS so
# the same toolkit works on macOS and Windows; the first path that exists wins,
# falling back to a bare 'inkscape' (i.e. whatever is on your PATH).
# Override with the INKSCAPE environment variable if yours lives elsewhere.
_INKSCAPE_CANDIDATES = [
    # macOS (Homebrew cask puts the real binary inside the .app bundle)
    '/Applications/Inkscape.app/Contents/MacOS/inkscape',
    str(Path.home() / 'Applications/Inkscape.app/Contents/MacOS/inkscape'),
    '/opt/homebrew/bin/inkscape',
    '/usr/local/bin/inkscape',
    # Linux (a distro package lands on PATH; Flatpak needs the wrapper below)
    '/usr/bin/inkscape',
    '/var/lib/flatpak/exports/bin/org.inkscape.Inkscape',
    str(Path.home() / '.local/share/flatpak/exports/bin/org.inkscape.Inkscape'),
    # Windows
    r'C:\Program Files\Inkscape\bin\inkscape.exe',
    r'C:\Program Files (x86)\Inkscape\bin\inkscape.exe',
]


def _find_inkscape():
    override = os.environ.get('INKSCAPE')
    if override:
        return override
    for candidate in _INKSCAPE_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return 'inkscape'


INKSCAPE = _find_inkscape()

# The root is the folder that holds your course folders. The toolkit (these
# scripts and the shared LaTeX package) lives elsewhere, so the root is taken
# from the LATEX_NOTES_ROOT environment variable — the VS Code tasks set it to
# the folder you have open — and otherwise falls back to the current directory.
ROOT = Path(os.environ.get('LATEX_NOTES_ROOT') or Path.cwd()).resolve()

# Name of the shared LaTeX package, registered with your TeX installation so it is
# found by name.
# Documents load it with \usepackage[<language>]{ajnotes} — no path needed.
PACKAGE = 'ajnotes'

# Lecture dates are stored language-neutrally as ISO YYYY-MM-DD; the \lecture macro
# in ajnotes.sty localizes the weekday and month name at compile time. This format
# is used both to write new lectures and to parse them back (for the week display).
DATE_FORMAT = '%Y-%m-%d'


def compile_latex(project_dir):
    """Build project_dir/main.tex with latexmk: the PDF lands in project_dir and the
    auxiliary files in project_dir/.aux/ (mirroring the LaTeX Workshop settings
    latex.outDir=%DIR% + latex.auxDir=%OUTDIR%/.aux, so both build paths agree).

    Shared by the notes and exercise compile scripts. Returns latexmk's exit code.
    """
    result = subprocess.run(
        ['latexmk', '-pdf', '-f', '-interaction=nonstopmode', '-auxdir=.aux',
         'main.tex'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(project_dir),
    )
    return result.returncode
