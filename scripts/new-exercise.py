#!/usr/bin/env python3
"""Create a new exercise session as a standalone mini-project.

Usage:
    python scripts/new-exercise.py [course]
    python scripts/new-exercise.py --from-file path/to/lec_03.tex
    python scripts/new-exercise.py --from-file <file> --title "Sheet 1"

Each session lives in <course>/exercises/ex_NN/ with its own main.tex (compiled
to its own PDF beside it), plus a figures/ folder. Drop the given problem set
into the folder as sheet.pdf and, if you want it embedded in your solutions,
un-comment the \\includepdf line in main.tex.
"""
import argparse
import re
import sys

from config import PACKAGE
from courses import get_course, exercise_projects


EXERCISE_TEMPLATE = r'''% !TEX root = ./main.tex
\documentclass[a4paper]{{article}}
\usepackage[{language}]{{{package}}}
\title{{{title}}}
\begin{{document}}
    \maketitle
    % Attach the given problem sheet: drop it in this folder as sheet.pdf and
    % un-comment the next line.
    % \includepdf[pages=-]{{sheet.pdf}}
    \exercise{{1}}
    \subexercise{{a}}

\end{{document}}
'''


def next_number(course):
    numbers = []
    for d in exercise_projects(course):
        match = re.match(r'ex_(\d+)$', d.name)
        if match:
            numbers.append(int(match.group(1)))
    return (max(numbers) + 1) if numbers else 1


def main():
    parser = argparse.ArgumentParser(description='Create a new exercise session.')
    parser.add_argument('course', nargs='?', default=None, help='Course folder name.')
    parser.add_argument('--from-file', default=None,
                        help='A file in the course (e.g. the lecture you are editing).')
    parser.add_argument('--title', default='',
                        help='Exercise title (default: a language-aware '
                             '"Problem Set N" / "Übungsserie N").')
    args = parser.parse_args()

    course = get_course(args.course, args.from_file)
    if course is None:
        return 1

    n = next_number(course)
    project = course.exercises_dir / f'ex_{n:02d}'
    if project.exists():
        print(f'{project} already exists.')
        return 1

    (project / 'figures').mkdir(parents=True)

    language = course.lectures.language()
    # Default title uses the \lblproblemset label so it localizes at compile time
    # (Problem Set / Übungsserie); an explicit --title is used verbatim.
    label = args.title.strip() or fr'\lblproblemset\ {n}'
    title = f'{course.title} — {label}'
    (project / 'main.tex').write_text(
        EXERCISE_TEMPLATE.format(
            language=language,
            package=PACKAGE,
            title=title,
        ),
        encoding='utf-8',
    )

    print(f'Created exercise {n} in {course.name}:')
    print(f'  {project / "main.tex"}')
    print('Drop the problem set in as sheet.pdf; write solutions with '
          '\\exercise{n} / \\subexercise{a} / \\subsubexercise{i}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
