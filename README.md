# CodePDF

Creates PDF files from code/markdown files.

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

## Command line help:

```
Usage:
    codepdf [-h | -v] [-D]
    codepdf [FILE...] [-o file] [-D]

Options:
    FILE                : File names to convert, or - for stdin.
                          If no names are given, stdin is used.
    -D,--debug          : Print some debug info while runnigng.
    -o file,--out file  : Output file name. If no name is given,
                          then <input_basename>.pdf is used.
    -h,--help           : Show this help message.
    -v,--version        : Show version.
```
