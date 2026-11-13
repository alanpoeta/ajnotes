#!/usr/bin/env python3
from courses import courses_or_enclosing

for course in courses_or_enclosing():
    lectures = course.lectures

    r = lectures.parse_range_string('all')
    lectures.update_lectures_in_main(r)
    lectures.compile_main()
