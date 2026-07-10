"""Tests for rename validation and session."""

from pathlib import Path

import pytest

from filenamer.rename import RenameError, RenameSession, validate_new_name


def test_validate_new_name():
    assert validate_new_name("") is not None
    assert validate_new_name("bad/name") is not None
    assert validate_new_name("good_name") is None


def test_rename_session(tmp_path):
    (tmp_path / "12345.jpg").write_bytes(b"x")
    (tmp_path / "vacation.jpg").write_bytes(b"x")

    session = RenameSession()
    assert session.load(tmp_path) == 1
    assert session.current().name == "12345.jpg"

    session.rename("beach_sunset")
    assert session.is_done()


def test_rename_session_skip(tmp_path):
    (tmp_path / "99999.png").write_bytes(b"x")
    session = RenameSession()
    session.load(tmp_path)
    session.skip()
    assert session.is_done()


def test_rename_duplicate(tmp_path):
    (tmp_path / "11111.png").write_bytes(b"x")
    (tmp_path / "taken.png").write_bytes(b"x")

    session = RenameSession()
    session.load(tmp_path)
    with pytest.raises(RenameError):
        session.rename("taken")
