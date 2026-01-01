"""Tests for B-tree split behavior in DSStore.insert().

These tests verify correct behavior when inserting entries that trigger
a B-tree node split. Currently, there is a bug where inserting an entry
that is alphabetically larger than all existing entries causes an IndexError.

These tests FAIL with the current implementation and will PASS once fixed.
"""

from ds_store import DSStore, DSStoreEntry


# Constants from the DS_Store implementation
PAGE_SIZE = 4096
HEADER_SIZE = 8  # next_node (4 bytes) + count (4 bytes)
AVAILABLE = PAGE_SIZE - HEADER_SIZE  # 4088 bytes


def entry_size(filename, value='x'):
    """Calculate the byte size of an entry."""
    entry = DSStoreEntry(filename, b'cmmt', 'ustr', value)
    return entry.byte_length()


class TestSplitWithLargestEntry:
    """Tests for inserting the alphabetically largest entry during a split."""

    def test_insert_largest_entry_succeeds(self, tmp_path):
        """Inserting the alphabetically largest entry should succeed.

        Setup:
        - Fill a leaf node with entries that use most of the available space
        - Insert an entry that is alphabetically LARGER than all existing entries
        - The split should handle this correctly and insert the entry
        """
        ds_path = tmp_path / ".DS_Store"

        # Each entry 'fNNN'/'c' is 26 bytes
        # 157 entries = 4082 bytes, leaving 6 bytes remaining
        # Any new entry (min 24 bytes) will trigger a split
        entries = [
            DSStoreEntry(f'f{i:03d}', b'cmmt', 'ustr', 'c')
            for i in range(157)
        ]

        # The 158th entry is alphabetically LARGEST (f999 > f156)
        largest_entry = DSStoreEntry('f999', b'cmmt', 'ustr', 'c')

        with DSStore.open(str(ds_path), "w+") as ds:
            for e in entries:
                ds.insert(e)
            ds.insert(largest_entry)  # Should succeed, not raise

        # Verify all entries exist
        with DSStore.open(str(ds_path), "r") as ds:
            assert len(list(ds.find('f999'))) == 1
            assert len(list(ds)) == 158

    def test_insert_largest_with_different_fill_level(self, tmp_path):
        """Split should work regardless of how full the page is."""
        ds_path = tmp_path / ".DS_Store"

        # Use larger entries to reach the threshold faster
        larger_entry_size = entry_size('file0000', 'comment_data')
        max_entries = AVAILABLE // larger_entry_size

        entries = [
            DSStoreEntry(f'file{i:04d}', b'cmmt', 'ustr', 'comment_data')
            for i in range(max_entries)
        ]

        # Insert the largest entry
        largest_entry = DSStoreEntry('file9999', b'cmmt', 'ustr', 'comment_data')

        with DSStore.open(str(ds_path), "w+") as ds:
            for e in entries:
                ds.insert(e)
            ds.insert(largest_entry)  # Should succeed

        # Verify the largest entry exists
        with DSStore.open(str(ds_path), "r") as ds:
            assert len(list(ds.find('file9999'))) == 1

    def test_insert_middle_entry_succeeds(self, tmp_path):
        """Inserting a middle entry should succeed."""
        ds_path = tmp_path / ".DS_Store"

        entries = [
            DSStoreEntry(f'f{i:03d}', b'cmmt', 'ustr', 'c')
            for i in range(157)
        ]

        # Insert an entry in the MIDDLE alphabetically (f050 < f050a < f051)
        middle_entry = DSStoreEntry('f050a', b'cmmt', 'ustr', 'c')

        with DSStore.open(str(ds_path), "w+") as ds:
            for e in entries:
                ds.insert(e)
            ds.insert(middle_entry)

        # Verify exactly one entry exists (not duplicates)
        with DSStore.open(str(ds_path), "r") as ds:
            assert len(list(ds.find('f050a'))) == 1

    def test_insert_smallest_entry_succeeds(self, tmp_path):
        """Inserting the smallest entry should succeed."""
        ds_path = tmp_path / ".DS_Store"

        entries = [
            DSStoreEntry(f'f{i:03d}', b'cmmt', 'ustr', 'c')
            for i in range(157)
        ]

        # Insert the smallest entry alphabetically (a000 < f000)
        smallest_entry = DSStoreEntry('a000', b'cmmt', 'ustr', 'c')

        with DSStore.open(str(ds_path), "w+") as ds:
            for e in entries:
                ds.insert(e)
            ds.insert(smallest_entry)

        # Verify exactly one entry exists
        with DSStore.open(str(ds_path), "r") as ds:
            assert len(list(ds.find('a000'))) == 1


class TestSequentialInsertion:
    """Test sequential insertion that naturally triggers splits."""

    def test_sequential_insertion_succeeds(self, tmp_path):
        """Sequential insertion of alphabetically ordered entries should work.

        When inserting entries in alphabetical order (file_000, file_001, ...),
        each new entry is larger than all existing entries. Once the node
        fills up, the split should handle this correctly.
        """
        ds_path = tmp_path / ".DS_Store"

        with DSStore.open(str(ds_path), "w+") as ds:
            for i in range(150):
                entry = DSStoreEntry(
                    f"file_{i:03d}", b"cmmt", "ustr", f"Comment {i}"
                )
                ds.insert(entry)

        # Verify all entries exist
        with DSStore.open(str(ds_path), "r") as ds:
            all_entries = list(ds)
            assert len(all_entries) == 150


class TestInternalNodeSplit:
    """Tests for the bug in _insert_inner() when splitting internal nodes."""

    def test_internal_node_split_with_largest_pivot(self, tmp_path):
        """Internal node split should handle largest pivot correctly.

        This test triggers the same bug but in _insert_inner() instead of
        _insert_leaf(). The bug occurs when:
        1. A leaf split produces a pivot
        2. That pivot must be inserted into a nearly-full internal node
        3. The internal node splits, but the pivot is largest in that node

        Stack trace when bug triggers:
        _insert_leaf() -> _insert_inner() -> _split() -> IndexError
        """
        ds_path = tmp_path / ".DS_Store"

        # Use large entries to reduce entries per node
        base = "x" * 100  # 218 bytes per entry, ~18 per node

        def make_entry(prefix, num):
            name = f"{prefix}{num:04d}" + base[5:]
            return DSStoreEntry(name, b'cmmt', 'ustr', 'x')

        # Build initial tree with 'm' prefix entries using initial_entries
        # (bypasses split bug during tree construction)
        entries_per_node = 18
        initial_count = entries_per_node * entries_per_node  # ~324 entries

        initial_entries = sorted([
            make_entry('m', i) for i in range(initial_count)
        ])

        # Create multi-level tree
        with DSStore.open(str(ds_path), "w+", initial_entries=initial_entries) as ds:
            assert ds._levels >= 2  # Must have internal nodes

        with DSStore.open(str(ds_path), "r+") as ds:
            # Insert 'a' entries in descending order (avoids leaf bug)
            # This grows the tree and fills internal nodes
            for i in range(entries_per_node * 5, -1, -1):
                ds.insert(make_entry('a', i))

            # Insert 'z' entries in descending order
            # Eventually triggers internal node split with largest pivot
            for i in range(entries_per_node * 5, -1, -1):
                ds.insert(make_entry('z', i))

        # Verify all entries exist
        with DSStore.open(str(ds_path), "r") as ds:
            all_entries = list(ds)
            expected = initial_count + (entries_per_node * 5 + 1) * 2
            assert len(all_entries) == expected


class TestSplitConsistency:
    """Tests verifying split behavior is consistent."""

    def test_minimal_largest_entry_case(self, tmp_path):
        """Minimal test case for largest entry insertion."""
        ds_path = tmp_path / ".DS_Store"

        # Use very long filenames to fill the page with fewer entries
        base_name = "a" * 100  # 100 character filename
        single_entry_size = entry_size(base_name, 'x')
        max_entries = AVAILABLE // single_entry_size

        entries = [
            DSStoreEntry(f'{chr(ord("a") + i)}' + base_name[1:], b'cmmt', 'ustr', 'x')
            for i in range(max_entries)
        ]

        # The largest entry uses 'z' prefix
        largest_entry = DSStoreEntry('z' + base_name[1:], b'cmmt', 'ustr', 'x')

        with DSStore.open(str(ds_path), "w+") as ds:
            for e in entries:
                ds.insert(e)
            ds.insert(largest_entry)  # Should succeed

        # Verify the entry was inserted
        with DSStore.open(str(ds_path), "r") as ds:
            found = list(ds.find('z' + base_name[1:]))
            assert len(found) == 1

    def test_100_sequential_insertions(self, tmp_path):
        """Verify sequential insertions work consistently across 100 files."""
        for run in range(100):
            ds_path = tmp_path / f".DS_Store_{run}"

            entries = [
                DSStoreEntry(f'f{i:03d}', b'cmmt', 'ustr', 'c')
                for i in range(157)
            ]
            largest_entry = DSStoreEntry('f999', b'cmmt', 'ustr', 'c')

            with DSStore.open(str(ds_path), "w+") as ds:
                for e in entries:
                    ds.insert(e)
                ds.insert(largest_entry)

            # Verify
            with DSStore.open(str(ds_path), "r") as ds:
                assert len(list(ds.find('f999'))) == 1
