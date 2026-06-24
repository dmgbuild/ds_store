# Some basic test code
import os
import plistlib
import sys

from ds_store import DSStore, __main__


def test_create(tmpdir):
    """Test that we can create a .DS_Store file successfully."""
    store_name = str(tmpdir / ".DS_Store")

    with DSStore.open(store_name, "w+"):
        pass

    assert os.path.exists(store_name)

    os.unlink(store_name)


def test_can_read(tmpdir):
    """Test that we can retrieve data from a .DS_Store file written by macOS."""
    with DSStore.open("tests/Test_DS_Store", "r") as store:
        assert store["bam"]["Iloc"] == (104, 116)
        assert store["bar"]["Iloc"] == (256, 235)
        assert store["baz"]["Iloc"] == (454, 124)


def test_holds_data(tmpdir):
    """Test that we can retrieve a key from a .DS_Store file that we stored
    into it earlier."""
    store_name = str(tmpdir / ".DS_Store")

    with DSStore.open(store_name, "w+") as store:
        store["foobar.dat"]["note"] = ("ustr", "Hello World!")

    assert os.path.exists(store_name)

    with DSStore.open(store_name, "r") as store:
        assert store["foobar.dat"]["note"] == (b"ustr", "Hello World!")

    os.unlink(store_name)


def test_find(tmpdir):
    """Test that we can find records with and without a code."""
    with DSStore.open("tests/Test_DS_Store", "r") as store:
        bamIloc = list(store.find("bam", code="Iloc"))
        assert len(bamIloc) == 1
        bam = list(store.find("bam"))
        assert bamIloc == bam


def test_cli_prints_entries(capsys):
    """The command-line tool should print the entries it reads, not swallow
    them. Guards against the loop being reduced to ``pass``."""
    __main__.main(["tests/Test_DS_Store"])

    out = capsys.readouterr().out
    assert "bam" in out
    assert "Iloc" in out


def test_cli_entry_point_takes_no_args(capsys, monkeypatch):
    """The console_scripts entry point calls ``main()`` with no arguments, so
    ``argv`` must default to ``sys.argv[1:]``. Guards against a TypeError on
    every invocation."""
    monkeypatch.setattr(sys, "argv", ["ds_store", "tests/Test_DS_Store"])

    __main__.main()  # must not raise

    assert "bam" in capsys.readouterr().out


def test_pretty_decodes_binary_plist():
    """Binary-plist blob values (e.g. lsvC) render as their decoded contents,
    not as a raw hex dump or latin-1 bytes."""
    blob = plistlib.dumps({"sortColumn": "dateAdded"}, fmt=plistlib.FMT_BINARY)

    # blob records arrive as bytearray, plain plists as bytes; handle both.
    for value in (blob, bytearray(blob)):
        out = __main__.pretty(value)
        assert "sortColumn" in out
        assert "dateAdded" in out
        assert "bplist00" not in out
