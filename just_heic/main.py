import argparse
from just_heic import heic_to_jpg, change_date, utils


def cli():
    global VERBOSE

    p = argparse.ArgumentParser("Convert heic files to jpg files.")

    subcmds = p.add_subparsers(title="sub-commands", required=True, dest="subcmd")

    # To jpg
    to_jpg = subcmds.add_parser("to_jpg", help="Convert heic files to jpg files.")
    to_jpg.add_argument("src", default=".", type=str, help="Source file or directory.")
    to_jpg.add_argument(
        "dest", type=str, nargs="?", default=None, help="Destination file or directory."
    )
    to_jpg.add_argument(
        "-r", "--recursive", action="store_true", help="Recurse through subdirectories."
    )
    to_jpg.add_argument(
        "-n",
        "--no-rotation",
        action="store_true",
        help="If set do not fix the exif orientation.",
    )

    to_jpg.add_argument(
        "-t",
        "--exif_date_taken",
        action="store_true",
        help="Change the created time to the date taken.",
    )
    to_jpg.add_argument(
        "-v", "--verbose", action="count", default=0, help="Print debug messages."
    )

    # To date taken
    to_dt = subcmds.add_parser(
        "to_date_taken",
        help="Change the given files created times to the exif date taken.",
    )
    to_dt.add_argument("src", default=".", type=str, help="Source file or directory.")
    to_dt.add_argument(
        "-r", "--recursive", action="store_true", help="Recurse through subdirectories."
    )
    to_dt.add_argument(
        "-e",
        "--ext",
        type=str,
        default=".jpg",
        help="Only modify files with this extension",
    )
    to_dt.add_argument(
        "-v", "--verbose", action="count", default=0, help="Print debug messages."
    )

    ARGS = p.parse_args()
    utils.set_verbosity(ARGS.verbose)  # Set global print statements

    if ARGS.subcmd == "to_jpg":
        src = ARGS.src
        dest = ARGS.dest
        recurse = ARGS.recursive
        no_rotation = ARGS.no_rotation
        exif_date_taken = ARGS.exif_date_taken
        heic_to_jpg.to_jpg(
            src,
            dest,
            recurse,
            fix_rotation=not no_rotation,
            exif_date_taken=exif_date_taken,
        )
    else:
        src = ARGS.src
        recurse = ARGS.recursive
        ext = ARGS.ext
        change_date.change_created_date(src, recursive=recurse, ext=ext)


if __name__ == "__main__":
    cli()
