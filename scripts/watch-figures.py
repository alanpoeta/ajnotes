#!/usr/bin/env python3
"""Auto-export Inkscape figures to PDF + pdf_tex when their .svg is saved.

Usage:
    python scripts/watch-figures.py          # watch every project's figures/ folder
    python scripts/watch-figures.py --once   # export all existing figures once and exit

Keep this running in a terminal during a lecture: each time you save a figure in
Inkscape (Ctrl+S), it is re-exported so your next LaTeX build picks it up. (The
document is rebuilt when you save a .tex — LaTeX Workshop's onFileChange — or when
you compile manually.) This is the cross-platform (watchdog) replacement for
Castel's Linux inotify / macOS fswatch watcher. Stop it with Ctrl+C.

On start, it also warms up Inkscape in the background (a throwaway headless
export), so the first "New figure" / "Edit figure" of the session opens faster —
most of the cold-start cost after a reboot is disk/cache, not the GUI itself.
"""
import argparse
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

from courses import courses_or_enclosing, exercise_projects
from figures import TEMPLATE, export_figure


def figure_dirs():
    dirs = []
    for course in courses_or_enclosing():
        # Every project has its own figures/: the notes plus each exercise.
        for project in [course.notes_dir, *exercise_projects(course)]:
            d = project / 'figures'
            if d.is_dir():
                dirs.append(d)
    return dirs


def _safe_export(svg_path):
    """export_figure(), but a crashed/misbehaving Inkscape invocation (e.g. it was
    closed mid-launch, or got caught by antivirus scanning a just-started exe) is
    reported instead of raised. Uncaught, that exception would kill the export
    loop below, or — worse — watchdog's dispatch thread in watch(), silently
    disabling the watcher for the rest of the session with no crash message."""
    try:
        return export_figure(svg_path)
    except Exception as e:
        print(f'  Export failed for {svg_path.name}: {e}')
        return False


def export_all():
    count = 0
    for d in figure_dirs():
        for svg in d.glob('*.svg'):
            print(f'Exporting {svg.relative_to(svg.parents[2])} ...')
            if _safe_export(svg):
                count += 1
    print(f'Exported {count} figure(s).')


def warm_up_inkscape():
    """Best-effort background warm-up: run one throwaway headless export so
    Inkscape's binary, shared libraries, and font cache get pulled into memory /
    refreshed on disk before you actually need Inkscape. Runs in a background
    thread (never delays the watcher starting); failures are silently ignored —
    this is an optimization, not something the watcher depends on."""
    def _run():
        try:
            with tempfile.TemporaryDirectory() as tmp:
                svg = Path(tmp) / 'warmup.svg'
                shutil.copy(TEMPLATE, svg)
                export_figure(svg)
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()


def watch():
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    warm_up_inkscape()

    class Handler(FileSystemEventHandler):
        def _handle(self, path):
            path = Path(path)
            if path.suffix.lower() == '.svg':
                print(f'Recompiling {path.name} ...')
                _safe_export(path)

        def on_modified(self, event):
            if not event.is_directory:
                self._handle(event.src_path)

        def on_created(self, event):
            if not event.is_directory:
                self._handle(event.src_path)

    dirs = figure_dirs()
    if not dirs:
        print('No figures/ folders found yet. Create a figure first '
              '(new-figure.py), then re-run.')
        return

    observer = Observer()
    handler = Handler()
    for d in dirs:
        observer.schedule(handler, str(d), recursive=False)
        print(f'Watching {d}')
    observer.start()
    print('Watching for figure saves. Press Ctrl+C to stop.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    parser = argparse.ArgumentParser(description='Auto-export Inkscape figures.')
    parser.add_argument('--once', action='store_true',
                        help='Export all existing figures once and exit (no watching).')
    args = parser.parse_args()

    if args.once:
        export_all()
    else:
        watch()
    return 0


if __name__ == '__main__':
    sys.exit(main())
