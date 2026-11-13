#!/usr/bin/env python3
"""Open an existing figure in Inkscape to edit it.

Usage:
    python scripts/edit-figure.py "Light cone"
    python scripts/edit-figure.py "Light cone" --course special-relativity
    python scripts/edit-figure.py --from-file path/to/lec_03.tex   # lists figures

With no name (or an unknown one) it lists the course's figures. Keep the figure
watcher running (watch-figures.py) so your edits re-export on save.
"""
import argparse
import sys

from courses import project_for
from figures import slugify, open_in_inkscape


def main():
    parser = argparse.ArgumentParser(description='Open an existing figure in Inkscape.')
    parser.add_argument('name', nargs='?', default=None, help='Figure name.')
    parser.add_argument('--course', default=None, help='Course folder name.')
    parser.add_argument('--from-file', default=None,
                        help='A file in the project (e.g. the lecture you are editing).')
    args = parser.parse_args()

    # Look in the project (notes or a specific exercise) that the open file belongs
    # to — the same place new-figure.py puts figures.
    project = project_for(args.from_file, args.course)
    if project is None:
        return 1

    figures_dir = project / 'figures'
    svgs = sorted(figures_dir.glob('*.svg'))
    if not svgs:
        print(f'No figures in {project.name} yet. Create one with new-figure.py.')
        return 1

    target = figures_dir / (slugify(args.name) + '.svg') if args.name else None
    if target is None or not target.exists():
        if args.name:
            print(f'No figure {slugify(args.name)!r} in {project.name}.')
        print(f'Figures in {project.name}:')
        for s in svgs:
            print(f'  {s.stem}')
        return 0 if target is None else 1

    open_in_inkscape(target)
    print(f'Opened {target}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
