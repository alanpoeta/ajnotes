#!/usr/bin/env python3
"""Create a new lecture in a course and wire it into main.tex.

Usage:
    python scripts/new-lecture.py [course]
    python scripts/new-lecture.py --from-file path/to/lec_03.tex

`course` is the course folder name (e.g. "notes"). Alternatively pass
--from-file to use the course containing that file (e.g. the lecture you're
editing). With neither, the only course is used when there's exactly one.
"""
import argparse
import sys

from courses import get_course


def main():
    parser = argparse.ArgumentParser(description='Create a new lecture in a course.')
    parser.add_argument('course', nargs='?', default=None, help='Course folder name.')
    parser.add_argument('--from-file', default=None,
                        help='A file in the course (e.g. the lecture you are editing).')
    parser.add_argument('--title', default='',
                        help='Optional lecture title (blank leaves the heading as '
                             'just "N Lecture").')
    args = parser.parse_args()

    course = get_course(args.course, args.from_file)
    if course is None:
        return 1

    lecture = course.lectures.new_lecture(args.title.strip())
    print(f'Created lecture {lecture.number} in {course.name}:')
    print(f'  {lecture.file_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
