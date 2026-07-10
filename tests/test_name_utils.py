"""Tests for descriptive name detection."""

from pathlib import Path

from medianamer.name_utils import find_files_needing_rename, is_descriptive_name, needs_rename

EXAMPLE_DATA_CURRENT = Path(__file__).resolve().parent.parent / "exampleData" / "Current"


def test_descriptive_names():
    assert is_descriptive_name("LiftTogetherOrgans")
    assert is_descriptive_name("my_vacation_photo")
    assert is_descriptive_name("Project Alpha")
    assert is_descriptive_name("clip-final-v2")
    assert is_descriptive_name("birthdayParty")
    assert is_descriptive_name("I'mCat")
    assert is_descriptive_name("THEONEPIECEIS")
    assert is_descriptive_name("vacation2024")
    assert is_descriptive_name("MyPhoto123")


def test_undescriptive_names():
    assert not is_descriptive_name("1677436352686185")
    assert not is_descriptive_name("12345")
    assert not is_descriptive_name("IMG_1234")
    assert not is_descriptive_name("DSC0001")
    assert not is_descriptive_name("a1b2c3d4e5f67890")
    assert not is_descriptive_name("550e8400-e29b-41d4-a716-446655440000")
    assert not is_descriptive_name("Screenshot 2024-01-01")
    assert not is_descriptive_name("video_001")
    assert not is_descriptive_name("G88xPUkWAAAYKvk")
    assert not is_descriptive_name("a1b2c3d4e5f6")
    assert not is_descriptive_name("320309338_706097217745185_4821093235619883660_n")
    assert not is_descriptive_name("ajVPg78_460sv")
    assert not is_descriptive_name("ssstwitter.com_1677363396448")
    assert not is_descriptive_name("tumblr_oiiggtypn21sn0wg5o1_400")
    assert not is_descriptive_name("serfdrsagregvergbreft")
    assert not is_descriptive_name("trim.B62AC75E-1030-4A26-A212-B3D79AB18929")
    assert not is_descriptive_name("unknown-3-1")
    assert not is_descriptive_name("untitled_42")
    assert not is_descriptive_name("G88xPUkWAAAYKvk")


def test_example_data_current_folder():
    if not EXAMPLE_DATA_CURRENT.is_dir():
        return

    for path in EXAMPLE_DATA_CURRENT.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".mp4", ".mov", ".jpg", ".jpeg", ".png", ".webm"}:
            continue
        assert needs_rename(path) == (not is_descriptive_name(path.stem)), path.name


def test_needs_rename(tmp_path):
    (tmp_path / "1677436352686185.webm").write_bytes(b"x")
    (tmp_path / "LiftTogetherOrgans.mov").write_bytes(b"x")
    (tmp_path / "notes.txt").write_text("ignore")

    assert needs_rename(tmp_path / "1677436352686185.webm")
    assert not needs_rename(tmp_path / "LiftTogetherOrgans.mov")
    assert not needs_rename(tmp_path / "notes.txt")

    found = find_files_needing_rename(tmp_path)
    assert len(found) == 1
    assert found[0].name == "1677436352686185.webm"


def test_find_files_needing_rename_subfolders(tmp_path):
    sub = tmp_path / "nested"
    sub.mkdir()
    (tmp_path / "12345.jpg").write_bytes(b"x")
    (sub / "67890.png").write_bytes(b"x")
    (tmp_path / "vacation.jpg").write_bytes(b"x")

    assert len(find_files_needing_rename(tmp_path)) == 1
    assert find_files_needing_rename(tmp_path)[0].name == "12345.jpg"

    found = find_files_needing_rename(tmp_path, include_subfolders=True)
    assert len(found) == 2
    assert found[0].name == "12345.jpg"
    assert found[1] == sub / "67890.png"
