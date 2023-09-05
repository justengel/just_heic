import arrow
import os
from PIL import Image, ImageOps
import pillow_heif
from typing import List

from just_heic.utils import (
    info,
    debug,
    set_cm_time,
    get_files,
    make_output_filename,
    get_metadata,
    EXIF_DATETIME,
    EXIF_ORIENTATION,
)


def convert_file(
    filename: str,
    output: str = None,
    fix_rotation: bool = True,
    exif_date_taken: bool = False,
) -> str:
    if os.path.splitext(filename)[-1].lower() != ".heic":
        raise ValueError("Invalid file! Expected an HEIC file extension.")

    output = make_output_filename(filename, output, ext=".jpg")

    # open the image file
    info("Converting", filename)
    heif_file = pillow_heif.read_heif(filename)

    # create the new image
    debug("Reading", filename)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )

    debug("Reading metadata")
    dictionary = heif_file.info
    exif = get_metadata(filename, data=dictionary["exif"])

    # Get created from exif
    created = os.path.getctime(filename)
    if exif_date_taken and EXIF_DATETIME in exif:
        created = arrow.get(exif[EXIF_DATETIME]).float_timestamp
    modified = os.path.getmtime(filename)

    debug("Saving", output)
    if fix_rotation:
        # Fix image orientation
        image = ImageOps.exif_transpose(image)

        # Fix exif data orientation
        exif[EXIF_ORIENTATION] = 1

    image.save(output, "JPEG", exif=exif.tobytes())
    set_cm_time(output, created, modified)
    debug("Saved", output)

    return output


def to_jpg(
    src: str,
    dest: str = None,
    recursive: bool = False,
    fix_rotation: bool = True,
    exif_date_taken: bool = False,
) -> List[str]:
    if not os.path.exists(src):
        raise ValueError("The given source does not exist!")

    # Find files to convert
    files = get_files(src, dest, recursive)

    # Convert files
    output_files = []
    for filename, output in files:
        output_files.append(
            convert_file(filename, output, fix_rotation, exif_date_taken)
        )

    return output_files
