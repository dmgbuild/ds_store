"""Targeted tests for internal node split behavior.

These tests specifically exercise the pointer ordering in internal B-tree nodes
during split operations. The key scenarios are:

1. Largest pivot insertion - when a leaf split produces a pivot that is larger
   than all existing entries in the parent internal node
2. Middle pivot insertion - when a pivot fits between existing entries
3. Deep tree operations - when splits cascade through multiple levels

The pointer ordering bug manifests when:
- Inserting the largest entry into an internal node during split
- The fix must ensure: next_node becomes pointer BEFORE entry,
  right_ptr becomes the new rightmost pointer

NOTE: We avoid using initial_entries parameter as it has a separate bug.
Instead, trees are built using regular inserts.
"""

from ds_store import DSStore, DSStoreEntry


class TestInternalNodePointerOrdering:
    """Tests that verify correct pointer ordering after internal node splits."""

    def make_entry(self, prefix, num, padding_len=100):
        """Create an entry with controlled size.

        Larger padding = fewer entries per node = easier to trigger splits.
        With padding_len=100, each entry is ~218 bytes, fitting ~18 per node.
        """
        padding = "x" * padding_len
        name = f"{prefix}{num:04d}{padding}"[: padding_len + 5]
        return DSStoreEntry(name, b"cmmt", "ustr", "v")

    def test_ascending_insertion_deep_tree(self, tmp_path):
        """Insert entries in strict ascending order to build a deep tree.

        This exercises the 'largest entry' code path at every level:
        - Each leaf insertion is larger than existing leaf entries
        - Each pivot promoted to internal nodes is larger than existing pivots
        - When internal nodes split, the pivot is again the largest

        If pointer ordering is wrong, tree traversal will fail to find entries.
        """
        ds_path = tmp_path / ".DS_Store"

        # Build tree with ascending insertions (always 'largest')
        all_filenames = []
        with DSStore.open(str(ds_path), "w+") as ds:
            # Insert enough entries to create a multi-level tree
            for i in range(500):
                entry = self.make_entry("f", i)
                all_filenames.append(entry.filename)
                ds.insert(entry)
            assert ds._levels >= 2, f"Need multi-level tree, got {ds._levels} levels"

        # Verify EVERY entry can be found
        with DSStore.open(str(ds_path), "r") as ds:
            for filename in all_filenames:
                found = list(ds.find(filename))
                assert len(found) == 1, (
                    f"Expected 1 copy of {filename[:30]}..., found {len(found)}"
                )

    def test_descending_then_ascending(self, tmp_path):
        """Insert in descending order, then ascending order.

        Descending: each entry is smallest, inserted at beginning
        Ascending: each entry is largest, inserted at end

        This creates a tree with entries at both extremes.
        """
        ds_path = tmp_path / ".DS_Store"

        all_filenames = []

        with DSStore.open(str(ds_path), "w+") as ds:
            # Insert 'a' entries in descending order (each is new smallest)
            for i in range(100, -1, -1):
                entry = self.make_entry("a", i)
                all_filenames.append(entry.filename)
                ds.insert(entry)

            # Insert 'z' entries in ascending order (each is new largest)
            for i in range(101):
                entry = self.make_entry("z", i)
                all_filenames.append(entry.filename)
                ds.insert(entry)

        # Verify all entries
        with DSStore.open(str(ds_path), "r") as ds:
            for filename in all_filenames:
                found = list(ds.find(filename))
                assert len(found) == 1, (
                    f"Expected 1 copy of {filename[:30]}..., found {len(found)}"
                )

            # Also verify total count
            all_entries = list(ds)
            assert len(all_entries) == len(all_filenames)

    def test_interleaved_largest_and_middle(self, tmp_path):
        """Alternate between inserting largest and middle entries.

        This exercises both code paths in the same tree and verifies
        they don't interfere with each other.
        """
        ds_path = tmp_path / ".DS_Store"

        inserted = []

        with DSStore.open(str(ds_path), "w+") as ds:
            # Start with some 'm' entries
            for i in range(50):
                entry = self.make_entry("m", i * 10)  # m0000, m0010, m0020, ...
                ds.insert(entry)
                inserted.append(entry.filename)

            # Interleave insertions
            for i in range(50):
                # Insert a 'z' entry (largest)
                z_entry = self.make_entry("z", i)
                ds.insert(z_entry)
                inserted.append(z_entry.filename)

                # Insert an 'a' entry (smallest)
                a_entry = self.make_entry("a", i)
                ds.insert(a_entry)
                inserted.append(a_entry.filename)

                # Insert a middle entry (between existing 'm' entries)
                mid_entry = self.make_entry("m", i * 10 + 5)  # m0005, m0015, etc.
                ds.insert(mid_entry)
                inserted.append(mid_entry.filename)

        # Verify all entries exist exactly once
        with DSStore.open(str(ds_path), "r") as ds:
            all_entries = list(ds)
            assert len(all_entries) == len(inserted), (
                f"Expected {len(inserted)} entries, got {len(all_entries)}"
            )

            # Check for duplicates
            filenames = [e.filename for e in all_entries]
            assert len(filenames) == len(set(filenames)), "Duplicates detected"


class TestTreeTraversalIntegrity:
    """Tests that verify tree traversal works correctly after splits."""

    def make_entry(self, prefix, num, padding_len=100):
        padding = "x" * padding_len
        name = f"{prefix}{num:04d}{padding}"[: padding_len + 5]
        return DSStoreEntry(name, b"cmmt", "ustr", "v")

    def test_find_in_different_subtrees(self, tmp_path):
        """Verify find() works for entries in different subtrees.

        If internal node pointers are wrong, entries in certain subtrees
        will be unreachable via find().
        """
        ds_path = tmp_path / ".DS_Store"

        # Create entries across the alphabet to ensure they end up in different subtrees
        prefixes = ["a", "f", "k", "p", "u", "z"]
        all_entries = {}

        with DSStore.open(str(ds_path), "w+") as ds:
            for prefix in prefixes:
                all_entries[prefix] = []
                for i in range(30):
                    entry = self.make_entry(prefix, i)
                    all_entries[prefix].append(entry)
                    ds.insert(entry)

        # Verify each entry can be found
        with DSStore.open(str(ds_path), "r") as ds:
            for prefix in prefixes:
                for entry in all_entries[prefix]:
                    found = list(ds.find(entry.filename))
                    assert len(found) == 1, (
                        f"{entry.filename[:30]}...: expected 1, got {len(found)}"
                    )

    def test_iteration_matches_find(self, tmp_path):
        """Verify that iteration and find() return consistent results.

        If tree structure is corrupted, iteration might return entries
        that find() cannot locate, or vice versa.
        """
        ds_path = tmp_path / ".DS_Store"

        # Create a moderately sized tree
        with DSStore.open(str(ds_path), "w+") as ds:
            for i in range(500):
                ds.insert(self.make_entry("f", i))

        with DSStore.open(str(ds_path), "r") as ds:
            # Get all entries via iteration
            all_entries = list(ds)

            # Verify each can be found
            for entry in all_entries:
                found = list(ds.find(entry.filename))
                assert len(found) >= 1, (
                    f"Entry {entry.filename[:30]}... found in iteration but not find()"
                )
                assert len(found) == 1, (
                    f"Entry {entry.filename[:30]}... has {len(found)} copies"
                )


class TestInternalNodeSplitScenarios:
    """Specific scenarios designed to trigger internal node splits."""

    def make_entry(self, prefix, num, padding_len=100):
        padding = "x" * padding_len
        name = f"{prefix}{num:04d}{padding}"[: padding_len + 5]
        return DSStoreEntry(name, b"cmmt", "ustr", "v")

    def test_force_internal_split_with_largest(self, tmp_path):
        """Force internal node splits where the pivot is the largest entry.

        Strategy:
        1. Build a multi-level tree with regular inserts
        2. Continue inserting in ascending order
        3. Each insertion triggers the 'largest entry' code path
        4. Eventually internal nodes fill and split
        """
        ds_path = tmp_path / ".DS_Store"

        # Build tree with ascending insertions
        all_filenames = []
        with DSStore.open(str(ds_path), "w+") as ds:
            # Insert enough to create internal nodes
            for i in range(400):
                entry = self.make_entry("f", i)
                all_filenames.append(entry.filename)
                ds.insert(entry)

            assert ds._levels >= 2, f"Expected >= 2 levels, got {ds._levels}"

        # Verify tree integrity
        with DSStore.open(str(ds_path), "r") as ds:
            all_entries = list(ds)
            assert len(all_entries) == len(all_filenames), (
                f"Expected {len(all_filenames)} entries, got {len(all_entries)}"
            )

            # Verify no duplicates
            filenames = [e.filename for e in all_entries]
            assert len(filenames) == len(set(filenames)), "Duplicates detected"

    def test_deep_tree_splits(self, tmp_path):
        """Test splits in a deep tree (2+ levels).

        With multiple levels, splits can cascade from leaves through
        internal nodes. This verifies the fix works at all levels.
        """
        ds_path = tmp_path / ".DS_Store"

        # Build a multi-level tree with ascending insertions
        all_filenames = []
        with DSStore.open(str(ds_path), "w+") as ds:
            # Insert enough for multiple levels
            for i in range(600):
                entry = self.make_entry("f", i)
                all_filenames.append(entry.filename)
                ds.insert(entry)

            assert ds._levels >= 2, f"Expected >= 2 levels, got {ds._levels}"

        # Verify all entries are findable
        with DSStore.open(str(ds_path), "r") as ds:
            for filename in all_filenames:
                found = list(ds.find(filename))
                assert len(found) == 1, (
                    f"Expected 1 copy of {filename[:30]}..., found {len(found)}"
                )

    def test_alternating_prefixes_ascending(self, tmp_path):
        """Insert entries with alternating prefixes in ascending order.

        This creates a more complex tree structure where entries are
        distributed across subtrees but each insertion is still 'largest'
        within its local context.
        """
        ds_path = tmp_path / ".DS_Store"

        prefixes = ["a", "m", "z"]
        all_filenames = []

        with DSStore.open(str(ds_path), "w+") as ds:
            for i in range(150):
                for prefix in prefixes:
                    entry = self.make_entry(prefix, i)
                    all_filenames.append(entry.filename)
                    ds.insert(entry)

        with DSStore.open(str(ds_path), "r") as ds:
            # Verify count
            all_entries = list(ds)
            assert len(all_entries) == len(all_filenames)

            # Verify all findable
            for filename in all_filenames:
                found = list(ds.find(filename))
                assert len(found) == 1


class TestEdgeCases:
    """Edge cases for split behavior."""

    def make_entry(self, prefix, num, padding_len=100):
        padding = "x" * padding_len
        name = f"{prefix}{num:04d}{padding}"[: padding_len + 5]
        return DSStoreEntry(name, b"cmmt", "ustr", "v")

    def test_single_entry_difference(self, tmp_path):
        """Test when new entry differs from existing by minimal amount.

        Insert entries like: m0000, m0010, m0020, then m0005, m0015, etc.
        This tests precise ordering at split boundaries.
        """
        ds_path = tmp_path / ".DS_Store"

        inserted = []

        with DSStore.open(str(ds_path), "w+") as ds:
            # Create base entries
            for i in range(50):
                entry = self.make_entry("m", i * 10)
                ds.insert(entry)
                inserted.append(entry.filename)

            # Insert entries between existing ones
            for i in range(50):
                entry = self.make_entry("m", i * 10 + 5)
                ds.insert(entry)
                inserted.append(entry.filename)

        # Verify all entries
        with DSStore.open(str(ds_path), "r") as ds:
            all_entries = list(ds)
            assert len(all_entries) == 100

            # Verify order
            filenames = [e.filename for e in all_entries]
            assert filenames == sorted(filenames), "Entries not in sorted order"

    def test_many_sequential_largest_insertions(self, tmp_path):
        """Insert 1000 entries in strict ascending order.

        Every single insertion is the 'largest' entry.
        This is the worst case for the pointer ordering bug.
        """
        ds_path = tmp_path / ".DS_Store"

        filenames = []
        with DSStore.open(str(ds_path), "w+") as ds:
            for i in range(1000):
                entry = self.make_entry("f", i)
                filenames.append(entry.filename)
                ds.insert(entry)

        # Verify all entries
        with DSStore.open(str(ds_path), "r") as ds:
            all_entries = list(ds)
            assert len(all_entries) == 1000, f"Expected 1000, got {len(all_entries)}"

            # Verify each is findable
            for filename in filenames:
                found = list(ds.find(filename))
                assert len(found) == 1, (
                    f"{filename[:30]}...: expected 1, got {len(found)}"
                )

    def test_reverse_then_forward(self, tmp_path):
        """Insert in reverse order, then continue forward.

        This tests the transition from 'smallest' insertions to 'largest'.
        """
        ds_path = tmp_path / ".DS_Store"

        filenames = []

        with DSStore.open(str(ds_path), "w+") as ds:
            # Reverse order: 199, 198, ..., 0
            for i in range(199, -1, -1):
                entry = self.make_entry("f", i)
                filenames.append(entry.filename)
                ds.insert(entry)

            # Forward order: 200, 201, ..., 399
            for i in range(200, 400):
                entry = self.make_entry("f", i)
                filenames.append(entry.filename)
                ds.insert(entry)

        with DSStore.open(str(ds_path), "r") as ds:
            all_entries = list(ds)
            assert len(all_entries) == 400

            for filename in filenames:
                found = list(ds.find(filename))
                assert len(found) == 1
