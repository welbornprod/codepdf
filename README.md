# CodePDF

Creates PDF/HTML files from code/markdown files.

## Dependencies:

These are system package dependencies.

- **Python 3+** (`python3`):
    This program uses python 3 features, and is not compatible with Python 2.
- **WKHtmlToPDF** (`wkhtmltopdf`):
    Converts HTML to PDF, and is required by `pdfkit`.

### Python package dependencies:

These packages can be installed with `pip`.

- **Docopt** (`docopt`):
    Used for command-line argument parsing.
- **Markdown** (`markdown`):
    Used for converting markdown files.
- **PdfKit** (`pdfkit`):
    Used for converting html to pdf.
- **Pygments** (`pygments`):
    Used for converting code files.

## Installation:

I recommend symlinking this script somewhere in your `$PATH`:
```bash
git clone https://github.com/welbornprod/codepdf.git
cd codepdf
ln -s "$PWD/codepdf.py" ~/.local/bin/codepdf
```

## Command line help:

```
Usage:
    codepdf -h | -S | -v
    codepdf [FILE...] [-f] [-H] [-l] [-o file] [-s style] [-t title] [-D]

Options:
    FILE                    : File names to convert, or - for stdin.
                              If no names are given, stdin is used.
    -D,--debug              : Print some debug info while running.
    -f,--forcemd            : Highlight markdown syntax, instead of
                              converting to HTML.
    -h,--help               : Show this help message.
    -H,--html               : Output in HTML instead of PDF.
                              Using .htm or .html as the output file
                              extension will automatically set this flag.
    -l,--linenumbers        : Use line numbers.
    -o file,--out file      : Output file name.
                              Default: <input_basename>.pdf
    -s name,--style name    : Pygments style name to use for code files.
                              Default: default
    -S,--styles             : Print all known pygments styles.
    -t title,--title title  : Title for the PDF.
                              Default: <input_filename>
    -v,--version            : Show version.
```

## Examples:

[example.html](example.html)
is an HTML file that was created by running:

```
codepdf README.md requirements.txt codepdf.py -o example.html
```

This is the same HTML that is used to create the PDF file.

[example.pdf](example.pdf)
is a PDF file that was created by running:

```
codepdf README.md requirements.txt codepdf.py -o example.pdf
```
