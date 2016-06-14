#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" codepdf.py
    Convert code/text files to pdf.
    -Christopher Welborn 06-13-2016
"""
import inspect
import os
import sys
from contextlib import suppress

try:
    from colr import (
        auto_disable as colr_auto_disable,
        Colr as C
    )
    from docopt import docopt
    from markdown import markdown
    from markdown.extensions.codehilite import CodeHiliteExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
    from markdown.extensions.sane_lists import SaneListExtension
    from pdfkit import from_string as pdf_from_string
    from pygments import highlight, lexers, formatters, styles
    from pygments.util import ClassNotFound
except ImportError as eximpcolr:
    print(
        '\n'.join((
            'Failed to import {pname}, you may need to install it:',
            '    pip install {exc.name}',
            'Original error:',
            '    {exc.msg}'
        )).format(
            pname=exc.name.title(),
            exc=exc
        ),
        file=sys.stderr
    )
    sys.exit(1)

# Disable colors when piping output.
colr_auto_disable()

NAME = 'CodePDF'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

# Global debug flag, set with --debug.
DEBUG = False
# File name to trigger reading from stdin.
STDIN_NAME = '-'
# Default pygments style.
DEFAULT_STYLE = 'default'
# Default pygments lexer, when it can't be detected.
DEFAULT_LEXER = 'text'

USAGESTR = """{versionstr}
    Usage:
        {script} -h | -S | -v
        {script} [FILE...] [-f] [-H] [-l] [-o file] [-s style] [-t title] [-D]

    Options:
        FILE                    : File names to convert, or {stdin} for stdin.
                                  If no names are given, stdin is used.
        -D,--debug              : Print some debug info while runnigng.
        -f,--forcemd            : Highlight markdown syntax, instead of
                                  converting to HTML.
        -h,--help               : Show this help message.
        -H,--html               : Output in HTML instead of PDF.
        -l,--linenumbers        : Use line numbers.
        -o file,--out file      : Output file name.
                                  Default: <input_basename>.pdf
        -s name,--style name    : Pygments style name to use for code files.
                                  Default: {default_style}
        -S,--styles             : Print all known pygments styles.
        -t title,--title title  : Title for the PDF.
                                  Default: <input_filename>
        -v,--version            : Show version.
""".format(
    default_style=DEFAULT_STYLE,
    script=SCRIPT,
    stdin=STDIN_NAME,
    versionstr=VERSIONSTR
)


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd. """
    global DEBUG
    DEBUG = argd['--debug']
    if argd['--styles']:
        return print_styles()

    filenames = argd['FILE'] or [STDIN_NAME]
    outname = get_output_name(
        filenames,
        output_name=argd['--out'],
        html_mode=argd['--html']
    )
    success = convert_files(
        argd['FILE'] or [STDIN_NAME],
        argd['--out'] or get_output_name(filenames),
        stylename=argd['--style'],
        linenos=argd['--linenumbers'],
        title=argd['--title'],
        force_highlight=argd['--forcemd'],
        html_mode=argd['--html']
    )
    return 0 if success else 1


def convert_files(
        filenames, outputname,
        stylename=None, linenos=False,
        title=None, force_highlight=False, html_mode=False):
    """ Convert all files into a single PDF. """
    stylename = stylename or DEFAULT_STYLE
    debug(
        '\n'.join((
            'Converting files:\n    {}'.format(
                '\n    '.join(os.path.split(s)[-1] for s in filenames)
            ),
            'Output file: {outfile}',
            '     Forced: {forced}',
            '    LineNos: {linenos}',
            '      Style: {style}',
            '      Title: {title}',
        )).format(
            outfile=outputname,
            forced=force_highlight,
            linenos=linenos,
            style=stylename,
            title=title,
        )
    )
    htmlcontent = []
    for filename in filenames:
        titletext = title or os.path.split(filename)[-1]
        formatter = get_formatter(
            stylename=stylename,
            linenos=linenos,
            title=titletext
        )
        htmlcontent.append(
            convert_to_html(
                filename,
                formatter,
                stylename=stylename,
                linenos=linenos,
                force_highlight=force_highlight
            )
        )

    if html_mode:
        debug('Writing HTML to file...')
        with open(outputname, 'w') as f:
            f.write('<hr>'.join(htmlcontent))
        return True

    debug('Converting to PDF...')
    return pdf_from_string(
        '<hr>'.join(htmlcontent),
        outputname,
        options={'title': titletext}
    )


def convert_highlighted(filename, formatter):
    """ Highlight a file with pygments, and return the resulting HTML. """
    displayname, content = get_file_content(filename)
    lexer = get_file_lexer(filename, content)
    debug('Highlighting: {}'.format(displayname))
    return highlight(content, lexer, formatter)


def convert_markdown(filename, stylename=None, linenos=False):
    """ Convert a markdown file to HTML, and return the result. """
    displayname, content = get_file_content(filename)
    stylename = stylename.lower() if stylename else DEFAULT_STYLE
    debug('Converting MD: {}'.format(displayname))
    hilighter = CodeHiliteExtension(
        pygments_style=stylename,
        linenums=linenos,
        noclasses=True,
    )
    return '\n'.join((
        '<div style="font-family: sans-serif;">',
        markdown(
            content,
            output_format='html5',
            extensions=[
                hilighter,
                FencedCodeExtension(),
                SaneListExtension(),
            ]
        ),
        '</div>'
    ))


def convert_to_html(
        filename, formatter,
        stylename=None, linenos=False, force_highlight=False):
    """ Convert a file to html. The conversion method depends on the
        file extension.
    """
    if (not force_highlight) and filename.endswith(('.md', '.markdown')):
        return convert_markdown(
            filename,
            stylename=stylename,
            linenos=linenos
        )
    return convert_highlighted(filename, formatter)


def debug(*args, **kwargs):
    """ Print a message only if DEBUG is truthy. """
    if not (DEBUG and args):
        return None

    # Include parent class name when given.
    parent = kwargs.get('parent', None)
    with suppress(KeyError):
        kwargs.pop('parent')

    # Go back more than once when given.
    backlevel = kwargs.get('back', 1)
    with suppress(KeyError):
        kwargs.pop('back')

    frame = inspect.currentframe()
    # Go back a number of frames (usually 1).
    while backlevel > 0:
        frame = frame.f_back
        backlevel -= 1
    fname = os.path.split(frame.f_code.co_filename)[-1]
    lineno = frame.f_lineno
    if parent:
        func = '{}.{}'.format(parent.__class__.__name__, frame.f_code.co_name)
    else:
        func = frame.f_code.co_name

    lineinfo = '{}:{} {}: '.format(
        C(fname, 'yellow'),
        C(str(lineno).ljust(4), 'blue'),
        C().join(C(func, 'magenta'), '()').ljust(20)
    )
    # Patch args to stay compatible with print().
    pargs = list(C(a, 'green').str() for a in args)
    pargs[0] = ''.join((lineinfo, pargs[0]))
    print(*pargs, **kwargs)


def get_file_content(filename):
    """ Returns a tuple of (display_name, content), handling stdin if
        STDIN_NAME is used.
    """
    if filename in (STDIN_NAME,):
        return 'stdin', read_stdin()

    with open(filename, 'r') as f:
        content = f.read()
    return os.path.split(filename)[-1], content


def get_file_lexer(filename, content):
    """ Try to get a lexer by file extension, guess by content if that fails.
    """
    try:
        lexer = lexers.get_lexer_for_filename(filename)
    except ClassNotFound:
        try:
            # Guess by content.
            lexer = lexers.guess_lexer(content)
        except ClassNotFound:
            # Fall back to default lexer.
            lexer = lexers.get_lexer_by_name(DEFAULT_LEXER)
    return lexer


def get_formatter(stylename=None, linenos=False, title=None):
    """ Get an HTMLFormatter from pygments. """
    stylename = stylename.lower() if stylename else DEFAULT_STYLE
    try:
        formatter = formatters.HtmlFormatter(
            linenos=linenos,
            style=stylename,
            full=True,
            title=title
        )
    except ClassNotFound:
        raise InvalidArg(
            '\n'.join((
                'Unknown style name: {style}',
                'Expecting:',
                '    {styles}'
            )).format(
                style=stylename,
                styles='\n    '.join(sorted(styles.STYLE_MAP))
            )
        )
    return formatter


def get_output_name(filenames, output_name=None, html_mode=False):
    """ Determine output file name to use when the user hasn't given one. """
    if output_name:
        # Short-circuit auto-name-detection.
        return output_name

    inputname = filenames[0]
    if inputname == '-':
        inputname = 'stdin'
    parentdir, basename = os.path.split(inputname)
    if not parentdir:
        parentdir = os.getcwd()
    return '{name}{ext}'.format(
        name=os.path.join(parentdir, os.path.splitext(basename)[0]),
        ext='.html' if html_mode else '.pdf'
    )


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default. """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def print_styles():
    """ Print all known pygments styles and return a success status code. """
    print('\n'.join((
        '\nStyle names:',
        '    {}'.format(
            '\n    '.join(sorted(styles.STYLE_MAP))
        )
    )))
    return 0


def read_stdin():
    """ Read from stdin, print a message if it's a terminal. """
    if syd.stdin.isatty() and sys.stdout.isatty():
        print('\nReading from stdin until end of file (Ctrl + D)...\n')
    return sys.stdin.read()


class InvalidArg(ValueError):
    """ Raised when the user has used an invalid argument. """
    def __init__(self, msg=None):
        self.msg = msg or ''

    def __str__(self):
        if self.msg:
            return 'Invalid argument, {}'.format(self.msg)
        return 'Invalid argument!'


if __name__ == '__main__':
    try:
        mainret = main(docopt(USAGESTR, version=VERSIONSTR))
    except InvalidArg as ex:
        print_err(ex)
        mainret = 1
    except (EOFError, KeyboardInterrupt):
        print_err('\nUser cancelled.\n', file=sys.stderr)
        mainret = 2
    except BrokenPipeError:
        print_err(
            '\nBroken pipe, input/output was interrupted.\n',
            file=sys.stderr)
        mainret = 3
    except EnvironmentError as ex:
        print_err(
            '\n{x.strerr}: {x.filename}'.format(x=ex)
        )
        mainret = 1
    sys.exit(mainret)
