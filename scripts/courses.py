#!/usr/bin/env python3
import re
from pathlib import Path

from lectures import Lectures
from utils import beautify
from config import ROOT


class Course():
    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.stem
        # A course holds its lecture notes in notes/ and, optionally, one
        # standalone mini-project per exercise session in exercises/.
        self.notes_dir = self.path / 'notes'
        self.exercises_dir = self.path / 'exercises'
        self._lectures = None

    @property
    def lectures(self):
        if not self._lectures:
            self._lectures = Lectures(self)
        return self._lectures

    @property
    def title(self):
        """The course title, read from \\title{...} in the notes' main.tex.

        Falls back to a prettified folder name if main.tex has no \\title (this
        is the source of truth now that there is no info.yaml)."""
        main = self.notes_dir / 'main.tex'
        if main.exists():
            match = re.search(r'\\title\{(.+?)\}', main.read_text(encoding='utf-8'))
            if match:
                return match.group(1)
        return beautify(self.name)

    @property
    def short(self):
        """A short identifier for the course; just the folder name."""
        return self.name

    def __eq__(self, other):
        if other is None:
            return False
        return self.path == other.path


class Courses(list):
    def __init__(self):
        list.__init__(self, self.read_files())

    def read_files(self):
        # A course is any folder holding notes/main.tex (the notes master), found
        # at ANY depth under the root — so courses can sit directly under the root
        # or be grouped in, e.g., semester folders. Keying off a real file means
        # detection never drifts. (scripts/, build dirs and hidden dirs are skipped.)
        skip = {'scripts', 'output', '.aux'}
        course_directories = []
        for main in ROOT.glob('**/notes/main.tex'):
            container = main.relative_to(ROOT).parts[:-2]  # dirs above notes/
            if any(part in skip or part.startswith('.') for part in container):
                continue
            course_directories.append(main.parent.parent)
        _courses = [Course(path) for path in sorted(set(course_directories))]
        return sorted(_courses, key=lambda c: c.name)


def course_containing(path):
    """The course that contains `path`: the nearest directory at or above it that
    holds a notes/main.tex, found by walking up. This works no matter which folder
    you open as the workspace — the course folder, a parent root, or notes/ itself
    (or any file inside them)."""
    path = Path(path).resolve()
    for candidate in [path, *path.parents]:
        if (candidate / 'notes' / 'main.tex').exists():
            return Course(candidate)
    return None


# Backwards-compatible name (the `courses` argument is no longer needed).
def course_for_file(path, courses=None):
    return course_containing(path)


def courses_or_enclosing():
    """All courses under the root, or — if there are none — the single course that
    encloses the root. Lets the whole-root tasks (compile all, watch figures) also
    work when you open one course's folder, or its notes/, as the workspace."""
    found = Courses()
    if found:
        return found
    enclosing = course_containing(ROOT)
    return [enclosing] if enclosing else []


def project_root_for_file(path):
    """The nearest ancestor directory of `path` that holds a main.tex.

    This is the "project" the file belongs to: the notes/ folder for a lecture,
    or an exercises/ex_NN/ folder for an exercise solution. Used to place figures
    and to compile the right document. Returns None if no main.tex is found."""
    path = Path(path).resolve()
    for parent in [path, *path.parents]:
        if (parent / 'main.tex').exists():
            return parent
    return None


def project_for(from_file=None, course_name=None):
    """The project a figure command should act on: the project containing the open
    file (notes/ or an exercise), else the resolved course's notes/. None if no
    course resolves. Shared by new-figure.py and edit-figure.py."""
    if from_file:
        project = project_root_for_file(from_file)
        if project is not None:
            return project
    course = get_course(course_name, from_file)
    return course.notes_dir if course is not None else None


def exercise_projects(course):
    """Sorted list of a course's exercise project dirs (those with a main.tex)."""
    if not course.exercises_dir.is_dir():
        return []
    return sorted(d for d in course.exercises_dir.iterdir()
                  if d.is_dir() and (d / 'main.tex').exists())


def get_course(name=None, from_file=None):
    """Pick a single course.

    Priority: an explicit folder `name`, then the course containing `from_file`
    (e.g. the file you're editing), then the only course if there's exactly one.
    Returns None (after printing a helpful message) when the choice is ambiguous
    or a given name doesn't match, so command-line scripts can exit cleanly.
    """
    if name is not None:
        courses = Courses()
        course = next((c for c in courses if c.name == name), None)
        if course is None:
            available = ', '.join(c.name for c in courses) or '(none under the open folder)'
            print(f'No course named {name!r}. Available: {available}')
        return course

    # Resolve from the open file: walking up from the file finds its course
    # regardless of which folder is open (so opening notes/ directly still works).
    if from_file is not None:
        course = course_containing(from_file)
        if course is not None:
            return course

    courses = Courses()

    if len(courses) == 0:
        print('No courses found. Create one with new-course.py first.')
        return None

    if len(courses) == 1:
        return courses[0]

    print('Multiple courses found, please pass one as an argument:')
    for c in courses:
        print(f'  {c.name}')
    return None
