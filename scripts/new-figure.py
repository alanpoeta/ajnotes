#!/usr/bin/env python3
"""Create a new Inkscape figure for a course and open it for drawing.

Usage:
    python scripts/new-figure.py "Light cone"
    python scripts/new-figure.py "Light cone" --course special-relativity
    python scripts/new-figure.py "Light cone" --from-file path/to/lec_03.tex

Copies the SVG template into the course's figures/ folder, opens it in Inkscape,
and prints the LaTeX \\incfig snippet (also copied to the clipboard if pyperclip
is installed) for you to paste into your lecture.
"""
import argparse
import sys
from shutil import copy

from courses import project_for
from figures import TEMPLATE, slugify, latex_template, beautify, open_in_inkscape


def main():
    parser = argparse.ArgumentParser(description='Create a new Inkscape figure.')
    parser.add_argument('title', help='Figure title (used for the file name and caption).')
    parser.add_argument('--course', default=None, help='Course folder name.')
    parser.add_argument('--from-file', default=None,
                        help='A file in the course (e.g. the lecture you are editing); '
                             'the figure is placed in that course.')
    args = parser.parse_args()

    # Place the figure in the project (the notes, or a specific exercise) that the
    # open file belongs to; fall back to the course's notes/ when only a name is given.
    project = project_for(args.from_file, args.course)
    if project is None:
        return 1

    figures_dir = project / 'figures'
    figures_dir.mkdir(parents=True, exist_ok=True)

    name = slugify(args.title)
    figure_path = figures_dir / (name + '.svg')

    if figure_path.exists():
        print(f'A figure named {name!r} already exists in {project.name}.')
        return 1

    copy(str(TEMPLATE), str(figure_path))
    open_in_inkscape(figure_path)

    snippet = latex_template(name, beautify(name))
    try:
        import pyperclip
        pyperclip.copy(snippet)
        copied = ' (copied to clipboard)'
    except Exception:
        copied = ''

    print(f'Created figure {name!r} in {project.name}{copied}:')
    print(snippet)
    return 0


if __name__ == '__main__':
    sys.exit(main())
