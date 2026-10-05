#!/usr/bin/env python3

from datetime import datetime
import re
import subprocess


from config import DATE_FORMAT, DEFAULT_LANGUAGE, PACKAGE, compile_latex


def number2filename(n):
    return 'lec_{0:02d}.tex'.format(n)


def filename2number(s):
    return int(str(s).replace('.tex', '').replace('lec_', ''))


class Lecture():
    def __init__(self, file_path, course):
        with file_path.open() as f:
            for line in f:
                lecture_match = re.search(r'lecture\{(.*?)\}\{(.*?)\}\{(.*)\}', line)
                if lecture_match:
                    break

        date_str = lecture_match.group(2)
        # Dates are stored as ISO (locale-independent). Fall back to today if the
        # stored date doesn't parse — the parsed date only feeds the week display.
        try:
            date = datetime.strptime(date_str, DATE_FORMAT)
        except ValueError:
            date = datetime.today()
        title = lecture_match.group(3)

        self.file_path = file_path
        self.date = date
        self.number = filename2number(file_path.stem)
        self.title = title
        self.course = course

    def edit(self):
        subprocess.Popen([
            "x-terminal-emulator",
            "-e", "zsh", "-i", "-c",
            f"\\vim --servername kulak --remote-silent {str(self.file_path)}"
        ])

    def __str__(self):
        return f'<Lecture {self.course.short} {self.number} "{self.title}">'


class Lectures(list):
    def __init__(self, course):
        self.course = course
        self.root = course.notes_dir
        self.main_file = self.root / 'main.tex'
        self.lectures_dir = self.root / 'lectures'
        list.__init__(self, self.read_files())

    def language(self):
        """The document language of this course, read from main.tex's package
        option (\\usepackage[<language>]{ajnotes}). Defaults to English."""
        if self.main_file.exists():
            match = re.search(r'\\usepackage\[(\w+)\]\{' + PACKAGE + r'\}',
                              self.main_file.read_text())
            if match:
                return match.group(1)
        return DEFAULT_LANGUAGE

    def read_files(self):
        files = self.lectures_dir.glob('lec_*.tex')
        return sorted((Lecture(f, self.course) for f in files), key=lambda lecture: lecture.number)

    def init_main(self, title, language='english'):
        """Create the notes folders and a fresh main.tex.

        Returns True if main.tex was created, or False if it already existed (so
        this is safe to call repeatedly without clobbering existing files).
        `title` fills the PDF's \\title{}; `language` is the preamble option,
        'english' (default) or 'german'.
        """
        self.root.mkdir(parents=True, exist_ok=True)
        self.lectures_dir.mkdir(exist_ok=True)
        (self.root / 'figures').mkdir(exist_ok=True)

        if self.main_file.exists():
            return False

        lines = [
            r'\documentclass[a4paper]{article}',
            fr'\usepackage[{language}]{{{PACKAGE}}}',
            fr'\title{{{title}}}',
            r'\begin{document}',
            r'    \maketitle',
            r'    \tableofcontents',
            r'    \clearpage',
            r'    % start lectures',
            r'    % end lectures',
            r'\end{document}',
        ]
        self.main_file.write_text('\n'.join(lines))
        return True

    def parse_lecture_spec(self, string):
        if len(self) == 0:
            return 0

        if string.isdigit():
            return int(string)
        elif string == 'last':
            return self[-1].number
        elif string == 'prev':
            return self[-1].number - 1

    def parse_range_string(self, arg):
        all_numbers = [lecture.number for lecture in self]
        if 'all' in arg:
            return all_numbers

        if '-' in arg:
            start, end = [self.parse_lecture_spec(bit) for bit in arg.split('-')]
            return list(set(all_numbers) & set(range(start, end + 1)))

        return [self.parse_lecture_spec(arg)]

    @staticmethod
    def get_header_footer(filepath):
        part = 0
        header = ''
        footer = ''
        with filepath.open() as f:
            for line in f:
                # order of if-statements is important here!
                if 'end lectures' in line:
                    part = 2

                if part == 0:
                    header += line
                if part == 2:
                    footer += line

                if 'start lectures' in line:
                    part = 1
        return (header, footer)

    def update_lectures_in_main(self, r):
        header, footer = self.get_header_footer(self.main_file)
        body = ''.join(
            ' ' * 4 + r'\input{lectures/' + number2filename(number) + '}\n' for number in r)
        self.main_file.write_text(header + body + footer)

    def new_lecture(self, title=''):
        if len(self) != 0:
            new_lecture_number = self[-1].number + 1
        else:
            new_lecture_number = 1

        new_lecture_path = self.lectures_dir / number2filename(new_lecture_number)

        # ISO date; the \lecture macro localizes the weekday/month at compile time.
        date = datetime.today().strftime(DATE_FORMAT)

        self.lectures_dir.mkdir(exist_ok=True)
        new_lecture_path.touch()
        new_lecture_path.write_text(
            f'% !TEX root = ../{self.main_file.name}\n'
            f'\\lecture{{{new_lecture_number}}}{{{date}}}{{{title}}}\n'
        )

        if new_lecture_number == 1:
            self.update_lectures_in_main([1])
        else:
            self.update_lectures_in_main([new_lecture_number - 1, new_lecture_number])

        self.read_files()

        lecture = Lecture(new_lecture_path, self.course)

        return lecture

    def compile_main(self):
        return compile_latex(self.root)
