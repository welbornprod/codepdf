#!/bin/bash

# Update example.pdf and example.html using fresh files.
# -Christopher Welborn 06-14-2016
appname="CodePDF Example Updater"
appversion="0.0.1"
apppath="$(readlink -f "${BASH_SOURCE[0]}")"
appscript="${apppath##*/}"
appdir="${apppath%/*}"


function echo_err {
    # Echo to stderr.
    echo -e "$@" 1>&2
}

function fail {
    # Print a message to stderr and exit with an error status code.
    echo_err "$@"
    exit 1
}

function fail_usage {
    # Print a usage failure message, and exit with an error status code.
    print_usage "$@"
    exit 1
}

function print_usage {
    # Show usage reason if first arg is available.
    [[ -n "$1" ]] && echo_err "\n$1\n"

    echo "$appname v. $appversion

    Usage:
        $appscript -h | -v
        $appscript [-D]

    Options:
        -D,--debug    : Use debug mode for codepdf when updating examples.
        -h,--help     : Show this message.
        -v,--version  : Show $appname version and exit.
    "
}

declare -a nonflags
codepdf_args=("--title" "CodePDF Example Output")
for arg; do
    case "$arg" in
        "-D"|"--debug" )
            [[ ! "${codepdf_args[*]}" =~ --debug ]] && codepdf_args+=("--debug")
            ;;
        "-h"|"--help" )
            print_usage ""
            exit 0
            ;;
        "-v"|"--version" )
            echo -e "$appname v. $appversion\n"
            exit 0
            ;;
        -*)
            fail_usage "Unknown flag argument: $arg"
            ;;
        *)
            nonflags=("${nonflags[@]}" "$arg")
    esac
done

include_files=(
    "$appdir/README.md"
    "$appdir/requirements.txt"
    "$appdir/codepdf.py"
)
exts=(".pdf" ".html")
for fileext in "${exts[@]}"; do
    ./codepdf.py "${codepdf_args[@]}" "${include_files[@]}" -o "example${fileext}"
done
