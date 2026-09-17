# LaTeX lecture notes toolkit

A shared toolkit for writing university lecture notes (and exercise solutions) in
LaTeX, based on [Gilles Castel's setup](https://castel.dev/post/lecture-notes-3).
Installed **once per machine**, then used from any folder. Works on
**macOS, Linux and Windows** with VS Code; the scripts detect the platform, so the
same toolkit folder serves all three.

## How it works

- **This toolkit folder** holds the `scripts/`, the shared `ajnotes` LaTeX package
  (`texmf/`), and a copy of the global VS Code tasks. It is installed once and lives
  in the same place for all your courses.
- **Your notes live anywhere.** Any folder you open in VS Code is treated as a
  *root*; the scripts act on it (the tasks pass it as `LATEX_NOTES_ROOT`). A folder
  is a **course** if it contains `notes/main.tex`, at any depth under the root — so
  you can group courses in e.g. `semester-1/`.
- **Open whatever folder is convenient.** A parent folder holding several courses, a
  single course's folder, or even its `notes/` folder directly all work — per-file
  tasks find the right course by walking *up* from the file you're editing.
- **Documents load the preamble by name:** `\usepackage[english]{ajnotes}` — no path,
  works at any depth, because the TeX installation finds the package globally.

## Requirements

| | Required | Notes |
|---|---|---|
| **Python** | 3.8+ | The tasks call `python3` on macOS/Linux, the `py` launcher on Windows. |
| **TeX** | a distribution providing `latexmk` on your `PATH` | MacTeX (macOS), TeX Live (Linux), MiKTeX + Perl (Windows). |
| **VS Code** | any recent version | Only for the tasks — the scripts also run standalone from a terminal. |
| **Inkscape** | optional | Needed only for the figure tasks. |
| `watchdog` | optional | Required by **Watch figures**. |
| `pyperclip` | optional | Copies the `\incfig` snippet to your clipboard. |

Everything except Python and TeX is optional: without Inkscape you simply don't use
the three figure tasks. Inkscape is auto-detected per platform — inside `Inkscape.app`
on macOS, on `PATH` or via Flatpak on Linux, under `Program Files` on Windows —
and an `INKSCAPE` environment variable overrides the search.

## Installation

### 1. Get the toolkit

**macOS / Linux:**
```sh
git clone https://github.com/alanpoeta/ajnotes.git ~/Projects/ajnotes
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/alanpoeta/ajnotes.git $HOME\Projects\ajnotes
```

Any stable location works; the rest of these steps refer to it as `<toolkit>`. The
VS Code tasks use `${userHome}`, so if you keep the same path *relative to your home
folder* on each machine, the same `tasks.json` works everywhere unedited.

### 2. Install the prerequisites

**macOS** (via [Homebrew](https://brew.sh)):
```sh
brew install python
brew install --cask mactex-no-gui    # ~6 GB; needs your admin password
brew install --cask inkscape         # optional, for figures
```

**Linux** — Debian/Ubuntu:
```sh
sudo apt install python3 python3-venv texlive-full latexmk inkscape
```
Fedora: `sudo dnf install python3 texlive-scheme-full latexmk inkscape` ·
Arch: `sudo pacman -S python texlive-meta inkscape`

`texlive-full` is large (~5 GB). A smaller `texlive-latex-extra` + `texlive-science`
+ `texlive-fonts-extra` usually covers the preamble, but the full scheme avoids
chasing missing `.sty` files.

Make sure you end up with `latexmk` — the scripts won't run without it. It comes with
the full scheme on Debian/Ubuntu and inside `texlive-binextra` (a dependency of
`texlive-meta`) on Arch, but is packaged separately on Fedora, hence the explicit
entry above. Check with `latexmk --version`.

If you install Inkscape via Flatpak
(`flatpak install flathub org.inkscape.Inkscape`), it's detected automatically.

**Windows:** installing MiKTeX alone is *not* enough to run `latexmk` — it is a Perl
script, and MiKTeX ships no Perl interpreter, so you also need Strawberry Perl and
the on-demand `latexmk` package. This walkthrough covers the whole setup:
<https://www.youtube.com/watch?v=4lyHIQl4VM8>

Then install Python 3 (let it add itself to your `PATH`) and, for figures,
[Inkscape](https://inkscape.org/).

### 3. Create the virtualenv (optional — only for figures)

Only needed for **Watch figures** (`watchdog`) and clipboard copying (`pyperclip`).

**macOS / Linux:**
```sh
python3 -m venv ~/.local/share/ajnotes-venv
~/.local/share/ajnotes-venv/bin/python -m pip install watchdog pyperclip
```

**Windows (PowerShell):**
```powershell
py -m venv $env:LOCALAPPDATA\ajnotes-venv
& "$env:LOCALAPPDATA\ajnotes-venv\Scripts\python.exe" -m pip install watchdog pyperclip
```

The venv lives *outside* the toolkit folder because it's machine-specific — that's
also why it isn't in this repo. [`scripts/_python.py`](scripts/_python.py) finds it
automatically (override with `LATEX_NOTES_PYTHON`); if it's missing, every script
still runs on plain `python3` and only **Watch figures** is unavailable.

A venv is used rather than a bare `pip install` because Homebrew's Python and most
current distro Pythons are marked PEP 668 "externally managed" and refuse to install
into the system site-packages.

### 4. Register the `ajnotes` package

This is what makes `\usepackage{ajnotes}` resolve from any folder. Symlinking (rather
than copying) means edits to the preamble in this repo take effect immediately.

**macOS:**
```sh
mkdir -p ~/Library/texmf/tex/latex
ln -sfn "<toolkit>/texmf/tex/latex/ajnotes" ~/Library/texmf/tex/latex/ajnotes
```

**Linux:**
```sh
mkdir -p ~/texmf/tex/latex
ln -sfn "<toolkit>/texmf/tex/latex/ajnotes" ~/texmf/tex/latex/ajnotes
```

Neither needs a refresh command — `TEXMFHOME` is scanned directly. (Confirm your
tree's location with `kpsewhich -var-value TEXMFHOME` if the path above differs.)

**Windows (MiKTeX)** registers a root instead of symlinking:
```powershell
initexmf --register-root="<toolkit>\texmf"
miktex fndb refresh
```

Verify on any platform:
```sh
kpsewhich ajnotes.sty      # should print a path to the package
```

If that prints nothing on macOS, MacTeX may not be on your `PATH` yet — open a new
terminal, or run `eval "$(/usr/libexec/path_helper)"`.

### 5. Set your name and region

Per-person settings live in a private `env.tex` — git-ignored, so nothing personal
reaches the repository:

```tex
\renewcommand{\authorname}{Your Name}        % title page + running header
\renewcommand{\ajgermanvariant}{ngerman}     % babel dialect; default nswissgerman
\renewcommand{\ajenglishvariant}{british}    % babel dialect; default american
\renewcommand{\ajgermanlocale}{DE}           % siunitx locale; unset by default
\renewcommand{\ajenglishlocale}{UK}          % siunitx locale; unset by default
```

Set only the lines you care about. Save it as
`<toolkit>/texmf/tex/latex/ajnotes/env.tex` (Windows:
`<toolkit>\texmf\tex\latex\ajnotes\env.tex`) to apply to every document on the
machine, or next to a `main.tex` to override for just that document — the nearer
file wins.

The babel variants take any dialect babel knows and control hyphenation and
quotation marks (`«x»` Swiss vs `„x“` German, `“x”` US vs `‘x’` UK).

The siunitx locales are **opt-in** and take one of `BR DE FR IT PL SI UK US ZA`.
Left unset, numbers use the house style — decimal point, comma thousands separator,
`·` exponent — in either language. Set one and siunitx's regional preset wins for
that language only, so `\ajgermanlocale = DE` gives `1234,5` in German documents
while English ones keep the house style.

With no `env.tex` at all, documents build with a neutral placeholder name and the
defaults above.

### 6. Install the VS Code tasks

Copy [`vscode-user-tasks.json`](vscode-user-tasks.json) into your VS Code user folder
as `tasks.json`:

| Platform | Destination |
|---|---|
| macOS | `~/Library/Application Support/Code/User/tasks.json` |
| Linux | `~/.config/Code/User/tasks.json` |
| Windows | `%APPDATA%\Code\User\tasks.json` |

If you cloned somewhere other than `~/Projects/ajnotes`, update the
`${userHome}/...` script paths inside it to match. (The Linux path above is for the
official Microsoft build; VSCodium and OSS builds use `Code - OSS`/`VSCodium`.)

### 7. *(Optional)* Bind a shortcut

In the same folder's `keybindings.json`, to open the task list:

```json
{ "key": "ctrl+alt+r", "command": "workbench.action.tasks.runTask" }
```

Use `cmd+alt+r` on macOS. Reload VS Code so it picks up the tasks and keybindings.

### Verifying the install

Run **New course**, then **Compile course**. A `notes/main.pdf` appearing next to
`main.tex` means Python, TeX and the package registration are all working.

## Layout

```
ajnotes/                                installed once (this folder)
├── scripts/                            the tooling
├── texmf/tex/latex/ajnotes/ajnotes.sty the shared preamble (edit here)
└── vscode-user-tasks.json              copy to your VS Code User dir as tasks.json

<any folder you open>/                  a root — one or more courses (may nest)
└── special-relativity/                 a course = a folder with notes/main.tex
    ├── notes/                          lecture notes → one PDF
    │   ├── main.tex   lectures/   figures/   (build: main.pdf + .aux/)
    └── exercises/                      appears on first "New exercise"
        └── ex_01/  main.tex · sheet.pdf · figures/  (build: main.pdf + .aux/)
```

- A folder is a **course** if it has `notes/main.tex`; its title is read from that
  file's `\title{}`.
- **Exercises** are standalone: each `exercises/ex_NN/` compiles to its own PDF and
  is never merged into the notes.
- Don't remove the `% start lectures` / `% end lectures` markers in `notes/main.tex`
  — the scripts rewrite everything between them.
- To **renumber** a lecture, rename its `lec_NN.tex` **and** edit the number in its
  `\lecture{N}{…}{…}` line (that argument is what's printed). To start at 2, name the
  first file `lec_02.tex` with `\lecture{2}{…}{…}`.

## Everyday use (VS Code tasks)

Press <kbd>Cmd+Alt+R</kbd> (macOS) / <kbd>Ctrl+Alt+R</kbd> (Windows), or
**Terminal → Run Task…**, to get the task list, then
pick one. Course/project tasks act on the **file you have open**; prompting tasks pop
a text box at the top — type and press <kbd>Enter</kbd>.

| Task | What it does |
|------|--------------|
| New course | create a course folder with `notes/main.tex` (prompts title + language) |
| New lecture | add the next `lec_NN.tex` and include it (prompts an optional title) |
| Compile course | include all lectures, build the notes `main.pdf` |
| Compile all courses | build every course's notes |
| New exercise | scaffold an `exercises/ex_NN` solution mini-project (prompts title) |
| Compile exercise | build the exercise (or notes) the open file belongs to |
| New figure | create + open an Inkscape figure, copy its `\incfig` snippet |
| Edit figure | reopen an existing figure in Inkscape |
| Watch figures | auto-export figures to PDF on save (run once per session) |

You can also open any `.tex` and build with LaTeX Workshop directly — `ajnotes` is on
the TeX path, so it resolves without any per-project configuration.

## Editing the preamble

Edit [`texmf/tex/latex/ajnotes/ajnotes.sty`](texmf/tex/latex/ajnotes/ajnotes.sty).
Content changes apply to every document immediately. You only need to refresh the
TeX filename database if you *add or rename* files under `texmf/` — `miktex fndb
refresh` on Windows; on macOS the symlinked `TEXMFHOME` needs no refresh.

## Output layout

Builds put `main.pdf` next to `main.tex` and the auxiliary files in `.aux/`,
matching `latex-workshop.latex.auxDir = "%OUTDIR%/.aux"` so the tasks and
LaTeX Workshop agree. This is identical on every platform: `-aux-directory` is a
MiKTeX-only engine flag, but on MacTeX/TeX Live `latexmk` emulates it — building
into `.aux/` and then moving the PDF up.

## Bibliography (optional)

The biblatex setup ships in the package but binds no file. To cite in a document, add
`\addbibresource{refs.bib}` to its `main.tex` (after `\usepackage[...]{ajnotes}`) —
any name/path you like — then use `\cite{…}` and `\printbibliography`. Documents
without a bibliography need no `.bib` file and build cleanly.

## Language (English ⇄ German)

Set per course by the option on the package in `notes/main.tex`:

```tex
\usepackage[english]{ajnotes}   % default
\usepackage[german]{ajnotes}
```

Everything localizes at **compile time**, so flipping the option and recompiling is
enough — no source edits. It switches babel and every printed label (Theorem→Satz,
Exercise→Aufgabe, Lecture→Vorlesung, …), the lecture dates in the margin (stored as
ISO `YYYY-MM-DD`, rendered with a localized weekday + month, e.g. `Thu 11. Jun 2026`
↔ `Do 11. Jun 2026`), and an exercise's default title (Problem Set N ↔ Übungsserie
N). The environment/command names you type don't change. (Numbers keep a decimal
point in both languages unless you opt into a `siunitx` locale.)

The regional variant of each language — Swiss vs. standard German, US vs. UK
English — is a per-person setting, not per course; see
[step 5](#5-set-your-name-and-region).

## Exercises

Exercise sessions live in `<course>/exercises/`, one self-contained mini-project per
session — each compiles to its **own** PDF.

1. With any file of the course open, run **New exercise** (title e.g. "Sheet 1") →
   creates `exercises/ex_NN/main.tex`.
2. Drop the given problem set into that folder as `sheet.pdf`; to print it ahead of
   your solutions, un-comment the `\includepdf[pages=-]{sheet.pdf}` line
   (`pdfpages` is already loaded).
3. Write solutions with one command per level, passing the number/letter — they format
   and indent like a real sheet (`1.` / `(a)` / `i.`) and the code says exactly which
   (sub)exercise each block is. Then run **Compile exercise**.

   ```tex
   \exercise{1}
       \subexercise{a}
           First part's answer…
       \subexercise{b}
           Second part's answer…
           \subsubexercise{i}
               A sub-point…
   \exercise{2}
       …
   ```

   (These set `\leftskip`, so keep the exercises last in the document; if you add
   anything after them, precede it with `\par\leftskip=0pt`.)

Figures work as in the notes: with an exercise open, **New figure** places it in that
exercise's `figures/`.

## Figures (Inkscape)

Vector SVGs whose text is typeset by LaTeX, included with `\incfig{name}`.

- **New figure** (<kbd>Ctrl+Alt+F</kbd> if bound) → name it → draw in Inkscape → save
  → paste the copied `\incfig` snippet into your document. Keep **Watch figures**
  running so saves auto-export to PDF; the figure then appears in the PDF on your next
  build (saving a `.tex` rebuilds via LaTeX Workshop, or compile manually).
- **Edit figure** reopens an existing figure's `.svg`; save and it re-exports.
- **Styling:** use Inkscape's **Fill & Stroke** dialog (<kbd>Ctrl+Shift+F</kbd>);
  copy a styled object and apply its look with **Paste Style**
  (<kbd>Ctrl+Shift+V</kbd>). Each new figure includes ready-made objects (arrows,
  axes) parked just below the page — copy them onto your page.
- **Math labels:** type LaTeX straight into an Inkscape text object — `$\gamma$`,
  `$\frac{1}{2}$` — and it is typeset by LaTeX at build time, in the document's
  font. Figure math is set in `\displaystyle`, so fractions, sums and integrals
  get their full-size form (use `$\textstyle...$` for the cramped one). Display
  delimiters (`$$...$$`, `\[...\]`) do *not* work — Inkscape wraps each label in
  a box where display math is invalid. To preview the result while drawing, the
  [textext](https://textext.github.io/textext/) extension renders LaTeX inside
  Inkscape.

## Configuration — [`scripts/config.py`](scripts/config.py)

- `PACKAGE` — the LaTeX package name (`ajnotes`); keep it in sync with the `.sty`
  filename and how it's registered with your TeX installation.
- `DEFAULT_LANGUAGE` — fallback language when a `main.tex` has no recognisable option.
- `INKSCAPE` — auto-detected per platform; set the `INKSCAPE` environment variable to
  override.
- `DATE_FORMAT` — how lecture dates are stored (ISO `YYYY-MM-DD`); the `.sty`
  localizes them at compile time.
- `ROOT` — auto-detected from `LATEX_NOTES_ROOT` (set by the tasks) or the current
  directory; never set by hand.

## License and credit

MIT — see [LICENSE](LICENSE). Built on [Gilles Castel's university
setup](https://github.com/gillescastel/university-setup) (MIT, © 2019 Gilles
Castel); the course/lecture handling and the figure workflow derive from it.
