import argparse
import glob
import os
from PIL import Image, ImageOps, ExifTags
import pillow_heif
from typing import List, Tuple

if os.name == "nt":
    from ctypes import windll, wintypes, byref
else:
    windll = wintypes = byref = None


def set_cm_time(filename: str, created: float, modified: float):
    os.utime(filename, (created, modified))

    if os.name == "nt":
        # Love Windows
        # Convert Unix timestamp to Windows FileTime using some magic numbers
        # See documentation: https://support.microsoft.com/en-us/help/167296
        timestamp = int((created * 10000000) + 116444736000000000)
        ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)

        # Call Win32 API to modify the file creation date
        handle = windll.kernel32.CreateFileW(filename, 256, 0, None, 3, 128, None)
        windll.kernel32.SetFileTime(handle, byref(ctime), None, None)
        windll.kernel32.CloseHandle(handle)


VERBOSE = 0


def info(*args, **kwargs):
    global VERBOSE
    if VERBOSE > 0:
        print(*args, **kwargs)


def debug(*args, **kwargs):
    global VERBOSE
    if VERBOSE > 1:
        print(*args, **kwargs)


def get_files(
    src: str, dest: str = None, recursive: bool = False
) -> List[Tuple[str, str]]:
    global VERBOSE

    # Check destination
    if dest is not None:
        if os.path.isdir(src) and os.path.isfile(dest):
            dest = os.path.dirname(dest)
        elif not os.path.exists(dest):
            os.makedirs(dest)

    # Collect source files
    if os.path.isfile(src):
        iter_files = glob.iglob(os.path.basename(src), root_dir=os.path.dirname(src))
        src = os.path.dirname(src)
    else:
        if recursive:
            iter_files = glob.iglob("**/*.heic", root_dir=src, recursive=True)
        else:
            iter_files = glob.iglob("*.heic", root_dir=src, recursive=False)

    # Create a list of (source, destination) files
    files = []
    debug("Files to convert:")
    for f in iter_files:
        out = make_output_filename(f, dest or src)
        f = os.path.normpath(os.path.join(src, f))
        files.append((f, out))
        debug("\t", "SRC:", f, "DEST:", out)

    return files


def make_output_filename(filename: str, output: str = None) -> str:
    if output is None:
        output = os.path.splitext(filename)[0] + ".jpg"
    elif os.path.isdir(output):
        output = os.path.join(output, os.path.splitext(filename)[0] + ".jpg")
    return os.path.normpath(output)


EXIF_REVERSED = {v: k for k, v in ExifTags.TAGS.items()}
ORIENTATION = EXIF_REVERSED['Orientation']


def get_metadata(filename: str, data: bytes = None) -> Image.Exif:
    debug("Reading metadata", filename)
    if isinstance(data, bytes):
        exif_dict = Image.Exif()
        exif_dict.load(data)
    elif os.path.splitext(filename)[-1].lower() == ".heic":
        img = pillow_heif.read_heif(filename)
        dictionary = img.info
        exif_dict = Image.Exif()
        exif_dict.load(dictionary["exif"])
    else:
        img = Image.open(filename)
        exif_dict = img.getexif()
    return exif_dict


def convert_file(filename: str, output: str = None, fix_rotation: bool = True) -> str:
    global VERBOSE

    if os.path.splitext(filename)[-1].lower() != ".heic":
        raise ValueError("Invalid file! Expected an HEIC file extension.")

    output = make_output_filename(filename, output)

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
    exif_dict = dictionary["exif"]
    created = os.path.getctime(filename)
    modified = os.path.getmtime(filename)

    debug("Saving", output)
    if fix_rotation:
        # Fix image orientation
        image = ImageOps.exif_transpose(image)

        # Fix exif data orientation
        exif = get_metadata(filename, data=exif_dict)
        exif[ORIENTATION] = 1
        exif_dict = exif.tobytes()

    image.save(output, "JPEG", exif=exif_dict)
    set_cm_time(output, created, modified)
    debug("Saved", output)

    return output


def main(src: str, dest: str = None, recursive: bool = False, fix_rotation: bool = True) -> List[str]:
    if not os.path.exists(src):
        raise ValueError("The given source does not exist!")

    # Find files to convert
    files = get_files(src, dest, recursive)

    # Convert files
    output_files = []
    for filename, output in files:
        output_files.append(convert_file(filename, output, fix_rotation))

    return output_files


def cli():
    global VERBOSE

    P = argparse.ArgumentParser("Convert heic files to jpg files.")
    P.add_argument(
        "src", default=".", type=str, help="Source file or directory."
    )
    P.add_argument(
        "dest", type=str, nargs="?", default=None, help="Destination file or directory."
    )
    P.add_argument(
        "-r", "--recursive", action="store_true", help="Recurse through subdirectories."
    )
    P.add_argument("-n", "--no-rotation", action="store_true", help="If set do not fix the exif rotation.")
    P.add_argument(
        "-v", "--verbose", action="count", default=0, help="Print debug messages."
    )
    ARGS = P.parse_args()

    SRC = ARGS.src
    DEST = ARGS.dest
    RECURSE = ARGS.recursive
    NO_ROTATION = ARGS.no_rotation
    VERBOSE = ARGS.verbose  # Set global

    main(SRC, DEST, RECURSE, fix_rotation=not NO_ROTATION)


if __name__ == "__main__":
    cli()