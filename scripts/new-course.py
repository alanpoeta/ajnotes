#!/usr/bin/env python3
"""Create a new course: a folder with an initialised notes/main.tex.

Usage:
    python scripts/new-course.py "Special Relativity"
    python scripts/new-course.py "Special Relativity" --folder relativity --language german

The folder name defaults to a slug of the title (e.g. "special-relativity").
The title is written into notes/main.tex's \\title{} (the course's title source).
The document language defaults to English.
"""
import argparse
import sys

from config import ROOT
from courses import Course
from utils import unbeautify


def main():
    parser = argparse.ArgumentParser(description='Create a new course.')
    parser.add_argument('title', help='Course title (shown on the PDF title page).')
    parser.add_argument('--folder', default=None,
                        help='Folder name (default: a slug derived from the title).')
    parser.add_argument('--language', default='english', choices=['english', 'german'],
                        help='Document language (default: english).')
    args = parser.parse_args()

    folder_name = args.folder or unbeautify(args.title)
    course_path = ROOT / folder_name

    if course_path.exists():
        print(f'A folder named {folder_name!r} already exists at {course_path}.')
        return 1

    # init_main creates course_path/notes/ (and lectures/, figures/) and the
    # main.tex that also makes this folder recognisable as a course.
    course = Course(course_path)
    course.lectures.init_main(args.title, args.language)

    print(f'Created course {folder_name!r} ({args.language}) at {course_path}')
    print('Add lectures with:  python scripts/new-lecture.py ' + folder_name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
