import os
from unittest import mock

norm = os.path.normpath


def test_get_files():
    from heic_to_jpg import get_files

    files = get_files("./src")
    assert files == [(norm("src/file.heic"), norm("src/file.jpg"))]

    files = get_files("./src/sub")
    assert files == [(norm("src/sub/file2.heic"), norm("src/sub/file2.jpg"))]

    files = get_files("./src/sub/sub2")
    assert files == [
        (norm("src/sub/sub2/file3.heic"), norm("src/sub/sub2/file3.jpg")),
        (norm("src/sub/sub2/file4.HEIC"), norm("src/sub/sub2/file4.jpg")),
    ]

    files = get_files("./src", recursive=True)
    assert files == [
        (norm("src/file.heic"), norm("src/file.jpg")),
        (norm("src/sub/file2.heic"), norm("src/sub/file2.jpg")),
        (norm("src/sub/sub2/file3.heic"), norm("src/sub/sub2/file3.jpg")),
        (norm("src/sub/sub2/file4.HEIC"), norm("src/sub/sub2/file4.jpg")),
    ]

    # Test convert with destination directory
    files = get_files("./src", "./dest")
    assert files == [(norm("src/file.heic"), norm("dest/file.jpg"))]

    files = get_files("./src/sub", "./dest")
    assert files == [(norm("src/sub/file2.heic"), norm("dest/file2.jpg"))]
    files = get_files("./src/sub", "./dest/sub")
    assert files == [(norm("src/sub/file2.heic"), norm("dest/sub/file2.jpg"))]

    files = get_files("./src/sub/sub2", "./dest")
    assert files == [
        (norm("src/sub/sub2/file3.heic"), norm("dest/file3.jpg")),
        (norm("src/sub/sub2/file4.HEIC"), norm("dest/file4.jpg")),
    ]
    files = get_files("./src/sub/sub2", "./dest/sub/sub2")
    assert files == [
        (norm("src/sub/sub2/file3.heic"), norm("dest/sub/sub2/file3.jpg")),
        (norm("src/sub/sub2/file4.HEIC"), norm("dest/sub/sub2/file4.jpg")),
    ]

    files = get_files("./src", "./dest", recursive=True)
    assert files == [
        (norm("src/file.heic"), norm("dest/file.jpg")),
        (norm("src/sub/file2.heic"), norm("dest/sub/file2.jpg")),
        (norm("src/sub/sub2/file3.heic"), norm("dest/sub/sub2/file3.jpg")),
        (norm("src/sub/sub2/file4.HEIC"), norm("dest/sub/sub2/file4.jpg")),
    ]


def test_output_files():
    from heic_to_jpg import main, make_output_filename

    def mock_convert_output(filename: str, output: str = None) -> str:
        if os.path.splitext(filename)[-1].lower() != ".heic":
            raise ValueError("Invalid file! Expected an HEIC file extension.")

        output = make_output_filename(filename, output)

        return output

    # Test convert with no destination
    with mock.patch("heic_to_jpg.convert_file", mock_convert_output):
        files = main("./src")
        assert set(files) == {norm("src/file.jpg")}

        files = main("./src/sub")
        assert set(files) == {norm("src/sub/file2.jpg")}

        files = main("./src/sub/sub2")
        assert set(files) == {norm("src/sub/sub2/file3.jpg"), norm("src/sub/sub2/file4.jpg")}

        files = main("./src", recursive=True)
        assert set(files) == {
            norm("src/file.jpg"),
            norm("src/sub/file2.jpg"),
            norm("src/sub/sub2/file3.jpg"),
            norm("src/sub/sub2/file4.jpg"),
        }

    # Test convert with destination directory
    with mock.patch("heic_to_jpg.convert_file", mock_convert_output):
        files = main("./src", "./dest")
        assert set(files) == {norm("dest/file.jpg")}

        files = main("./src/sub", "./dest")
        assert set(files) == {norm("dest/file2.jpg")}

        files = main("./src/sub/sub2", "./dest")
        assert set(files) == {
            norm("dest/file3.jpg"),
            norm("dest/file4.jpg"),
        }

        files = main("./src", "./dest", recursive=True)
        assert set(files) == {
            norm("dest/file.jpg"),
            norm("dest/sub/file2.jpg"),
            norm("dest/sub/sub2/file3.jpg"),
            norm("dest/sub/sub2/file4.jpg"),
        }


def test_convert_file():
    from heic_to_jpg import main, convert_file, get_metadata, get_files

    filename = convert_file("src/file.heic", "dest/file.jpg")
    assert filename == norm("dest/file.jpg")

    src_meta = get_metadata("src/file.heic")
    dest_meta = get_metadata(filename)
    assert dict(src_meta) == dict(dest_meta)
    assert os.path.getmtime("src/file.heic") == os.path.getmtime("dest/file.jpg")
    assert os.path.getctime("src/file.heic") == os.path.getctime("dest/file.jpg")

    files = main("src", "dest", recursive=True)
    assert set(files) == {
        norm("dest/file.jpg"),
        norm("dest/sub/file2.jpg"),
        norm("dest/sub/sub2/file3.jpg"),
        norm("dest/sub/sub2/file4.jpg"),
    }

    for src, dest in get_files("src", "dest", recursive=True):
        src_meta = get_metadata(src)
        dest_meta = get_metadata(dest)
        assert dict(src_meta) == dict(dest_meta)
        assert os.path.getmtime(src) == os.path.getmtime(dest)
        assert os.path.getctime(src) == os.path.getctime(dest)
