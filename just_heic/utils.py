import glob
import os
from PIL import Image, ImageOps, ExifTags
import pillow_heif
from typing import List, Tuple

if os.name == "nt":
    from ctypes import windll, wintypes, byref
else:
    windll = wintypes = byref = None


VERBOSE = 0
EXIF_REVERSED = {v: k for k, v in ExifTags.TAGS.items()}
EXIF_ORIENTATION = EXIF_REVERSED["Orientation"]
EXIF_DATETIME = EXIF_REVERSED["DateTime"]


def set_verbosity(verbosity: int):
    global VERBOSE
    VERBOSE = verbosity


def info(*args, **kwargs):
    global VERBOSE
    if VERBOSE > 0:
        print(*args, **kwargs)


def debug(*args, **kwargs):
    global VERBOSE
    if VERBOSE > 1:
        print(*args, **kwargs)


def set_cm_time(filename: str, created: float, modified: float):
    os.utime(filename, (created, modified))

    if os.name == "nt":
        # Love Windows: taken from https://stackoverflow.com/a/56805533/1965288
        # Convert Unix timestamp to Windows FileTime using some magic numbers
        # See documentation: https://support.microsoft.com/en-us/help/167296
        timestamp = int((created * 10000000) + 116444736000000000)
        ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)

        # Call Win32 API to modify the file creation date
        handle = windll.kernel32.CreateFileW(filename, 256, 0, None, 3, 128, None)
        windll.kernel32.SetFileTime(handle, byref(ctime), None, None)
        windll.kernel32.CloseHandle(handle)


def get_files(
    src: str,
    dest: str = None,
    recursive: bool = False,
    ext: str = ".heic",
    out_ext: str = ".jpg",
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
            iter_files = glob.iglob(f"**/*{ext}", root_dir=src, recursive=True)
        else:
            iter_files = glob.iglob(f"*{ext}", root_dir=src, recursive=False)

    # Create a list of (source, destination) files
    files = []
    debug("Files to convert:")
    for f in iter_files:
        out = make_output_filename(f, dest or src, ext=out_ext)
        f = os.path.normpath(os.path.join(src, f))
        files.append((f, out))
        debug("\t", "SRC:", f, "DEST:", out)

    return files


def make_output_filename(filename: str, output: str = None, ext: str = ".jpg") -> str:
    if output is None:
        output = os.path.splitext(filename)[0] + ext
    elif os.path.isdir(output):
        output = os.path.join(output, os.path.splitext(filename)[0] + ext)
    return os.path.normpath(output)


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
