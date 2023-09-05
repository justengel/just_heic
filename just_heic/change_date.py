import arrow
import os
from typing import List

from just_heic.utils import (
    info,
    debug,
    set_cm_time,
    get_files,
    get_metadata,
    EXIF_DATETIME,
)


def change_created_date(
    src: str, recursive: bool = False, ext: str = ".jpg"
) -> List[str]:
    if not os.path.exists(src):
        raise ValueError("The given source does not exist!")

    # Find files to convert
    files = []
    for filename, _ in get_files(src, dest=".", recursive=recursive, ext=ext):
        exif = get_metadata(filename)
        try:
            date_taken = arrow.get(exif[EXIF_DATETIME], "YYYY:MM:DD HH:mm:ss")
        except (arrow.parser.ParserError, Exception):
            try:
                date_taken = arrow.get(exif[EXIF_DATETIME])
            except (TypeError, Exception):
                debug(f"Cannot parse EXIF DateTaken for {filename}")
                continue
        modified = os.path.getmtime(filename)

        info(f"Saving {filename} created time as {date_taken}")
        set_cm_time(filename, date_taken.float_timestamp, modified)
        files.append(filename)

    return files
