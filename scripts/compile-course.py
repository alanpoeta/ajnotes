#!/usr/bin/env python3
"""Include all lectures of a single course in its main.tex and compile it.

Usage:
    python scripts/compile-course.py [course]
    python scripts/compile-course.py --from-file path/to/lec_03.tex

`course` is the course folder name (e.g. "notes"). Alternatively pass
--from-file to use the course containing that file. With neither, the only
course is used when there's exactly one. This is the single-course counterpart
of compile-all-courses.py.
"""
import argparse
import sys

from courses import get_course


def main():
    parser = argparse.ArgumentParser(description='Compile a single course.')
    parser.add_argument('course', nargs='?', default=None, help='Course folder name.')
    parser.add_argument('--from-file', default=None,
                        help='A file in the course (e.g. the lecture you are editing).')
    args = parser.parse_args()

    course = get_course(args.course, args.from_file)
    if course is None:
        return 1

    lectures = course.lectures
    lectures.update_lectures_in_main(lectures.parse_range_string('all'))
    returncode = lectures.compile_main()

    if returncode == 0:
        print(f'Compiled {course.name}: {lectures.root / "main.pdf"}')
    else:
        print(f'latexmk failed for {course.name} (exit {returncode}). '
              f'See {lectures.root / ".aux" / "main.log"}.')
    return returncode


if __name__ == '__main__':
    sys.exit(main())
