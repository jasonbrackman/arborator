import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fictus import FictusDisplay, FictusFileSystem
from fictus.fictusexception import FictusException


class MyTestCase(unittest.TestCase):
    root = "c:"

    def setUp(self) -> None:
        self.fs = FictusFileSystem("c:")

    def test_cd_back_one(self):
        self.fs.mkdir(r"a\b")  # create \\a\b
        self.fs.cd(r"\a\b")  # move to \\a\b

        # Should show c:\a\b
        self.assertEqual(os.sep.join([self.root, "a", "b"]), self.fs.cwd())

        self.fs.cd("..")  # Go higher
        self.assertEqual(os.sep.join([self.root, "a"]), self.fs.cwd())

        self.fs.cd("..")  # again to _root
        self.assertEqual(os.sep.join([self.root]), self.fs.cwd())

        # with self.assertRaises(FictusException):
        # should fail as moving higher than _root doesn't exist
        self.fs.cd("..")
        self.assertEqual(self.fs.cwd(), self.root)

    def test_cd_traversal(self):
        self.fs.mkdir("a/b/c")
        self.fs.mkdir("a/c/b")
        self.fs.mkdir("a/a/a")

        self.fs.cd("a/b/c/../..")
        self.assertEqual(os.sep.join([self.root, "a"]), self.fs.cwd())

        self.fs.cd("/a/a/../b/../c")
        self.assertEqual(os.sep.join([self.root, "a", "c"]), self.fs.cwd())

    def test_cd_root(self):
        self.fs.mkdir("a/b")
        self.fs.cd("a/../a/b")
        self.fs.cd("/")
        self.assertEqual(self.root, self.fs.cwd())

        self.fs.cd("a/b")
        self.fs.cd("\\")
        self.assertEqual(self.root, self.fs.cwd())

        # go to _root from _root
        self.fs.cd("/a")
        self.fs.cd("/a")
        self.assertEqual(os.sep.join([self.root, "a"]), self.fs.cwd())

    def test_cd_from_cwd(self):
        self.fs.mkdir("a/b/c")
        self.fs.mkdir("a/c/b")
        self.fs.mkdir("a/a/a")
        self.fs.cd("/a/b")

        self.assertEqual(os.sep.join([self.root, "a", "b"]), self.fs.cwd())

        self.fs.cd("/a")
        self.assertEqual(os.sep.join([self.root, "a"]), self.fs.cwd())

    def test_cd_fail(self):
        self.fs.cd("/")  # drop to _root

        with self.assertRaises(FictusException):
            self.fs.cd("z/y/x")  # doesn't go anywhere; invalid path
            self.fs.cd("/z/y/x")  # still broken but starts with a jump to _root

    def test_cd_fail_but_remain_at_cwd(self):
        self.fs.cd("/")  # drop to _root
        self.fs.mkdir("a/b/c")
        self.fs.cd("a/b/c")  # move down the chain

        # with self.assertRaises(FictusException):
        self.fs.cd("../../../..")  # go back once too many times

        self.assertEqual(self.fs.cwd(), self.root)
        # still at the last place expected
        # self.assertEqual(self.fs.cwd(), self.root + "/a/b/c")

    def test_mkdir_with_non_string(self):
        with self.assertRaises(FictusException):
            # empty strings not allowed
            self.fs.mkdir("")

    def test_mkdir_with_odd_characters(self):
        # allowed
        items = [" ", "0", "~", "🎂"]
        for item in items:
            self.fs.mkdir(f"/{item}")
            self.fs.cd(f"/{item}")
            self.assertEqual(os.sep.join([self.root, item]), self.fs.cwd())

    def test_mkdir_with_a_dot(self):
        # a period is 'normalized' away ie: fizz/./buzz == fizz/buzz
        self.fs.mkdir("/fizz/./buzz")
        self.fs.cd("/fizz/buzz")  # no '.' directory created
        self.fs.cd("/fizz/./././././././././.")  # still fine.
        self.assertEqual(os.sep.join([self.root, "fizz"]), self.fs.cwd())

    def test_invalid_root(self):
        with self.assertRaises(FictusException):
            FictusFileSystem("c")

    def test_reforestation_writes_under_destination(self):
        self.fs.mkdir("docs")
        self.fs.cd("docs")
        self.fs.mkfile("readme.txt")
        self.fs.cd("/")

        with TemporaryDirectory() as temp:
            destination = Path(temp) / "output"
            FictusDisplay(self.fs).reforestation(destination)

            self.assertTrue((destination / "docs" / "readme.txt").is_file())

    def test_reforestation_preserves_existing_files_by_default(self):
        self.fs.mkfile("readme.txt")

        with TemporaryDirectory() as temp:
            destination = Path(temp)
            existing_file = destination / "readme.txt"
            existing_file.write_text("keep me", encoding="utf-8")

            with self.assertRaises(FictusException):
                FictusDisplay(self.fs).reforestation(destination)

            self.assertEqual("keep me", existing_file.read_text(encoding="utf-8"))

    def test_reforestation_can_overwrite_when_explicitly_requested(self):
        self.fs.mkfile("readme.txt")

        with TemporaryDirectory() as temp:
            existing_file = Path(temp) / "readme.txt"
            existing_file.write_text("replace me", encoding="utf-8")

            FictusDisplay(self.fs).reforestation(Path(temp), overwrite=True)

            self.assertEqual("", existing_file.read_text(encoding="utf-8"))

    def test_reforestation_rejects_unsafe_node_names(self):
        self.fs.mkfile("../outside.txt")

        with TemporaryDirectory() as temp:
            with self.assertRaises(FictusException):
                FictusDisplay(self.fs).reforestation(Path(temp))

if __name__ == "__main__":
    unittest.main()
