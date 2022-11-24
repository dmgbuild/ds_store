# Some basic test code
import os

from ds_store import DSStore


def test_create(tmpdir):
    """Test that we can create a .DS_Store file successfully."""
    store_name = str(tmpdir / ".DS_Store")

    with DSStore.open(store_name, "w+"):
        pass

    assert os.path.exists(store_name)

    os.unlink(store_name)


def test_can_read(tmpdir):
    """Test that we can retrieve data from a .DS_Store file written by OS X."""
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
