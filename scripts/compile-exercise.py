#!/usr/bin/env python3
"""Compile the standalone document (e.g. an exercise) the given file belongs to.

Usage:
    python scripts/compile-exercise.py --from-file path/to/exercises/ex_01/main.tex

Finds the nearest main.tex at or above the file and builds it with latexmk into
its folder (aux files under .aux/). (For the full lecture notes, use
compile-course.py.)
"""
import argparse
import sys

from config import compile_latex
from courses import project_root_for_file


def main():
    parser = argparse.ArgumentParser(description='Compile an exercise mini-project.')
    parser.add_argument('--from-file', required=True,
                        help='A file in the exercise project to compile.')
    args = parser.parse_args()

    project = project_root_for_file(args.from_file)
    if project is None:
        print(f'No main.tex found at or above {args.from_file!r}.')
        return 1

    returncode = compile_latex(project)
    if returncode == 0:
        print(f'Compiled {project.name}: {project / "main.pdf"}')
    else:
        print(f'latexmk failed for {project.name} (exit {returncode}). '
              f'See {project / ".aux" / "main.log"}.')
    return returncode


if __name__ == '__main__':
    sys.exit(main())
