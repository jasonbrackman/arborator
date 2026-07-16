"""Contains the class and its methods directly related to the FictusFileSystem."""

import os
from pathlib import Path
from typing import Optional

from .fictusexception import FictusException
from .fictusnode import File, Folder, Node

DEFAULT_ROOT_NAME = os.sep


class FictusFileSystem:
    """
    A FictusFileSystem (FFS) simulates the creation and traversal of a file system.
    The FFS allows for the creation and removal of files and folders,
    """

    def __init__(self, name=DEFAULT_ROOT_NAME) -> None:
        self._validate_root(name)
        self._root: Folder = Folder(name, None)
        self._current: Folder = self._root

    @staticmethod
    def _validate_root(name) -> None:
        if name == os.sep or name.endswith(":"):
            return

        raise FictusException(
            f'A root folder must be "{os.sep}" or end with a colon, like "d:"'
        )

    @classmethod
    def init_from_path(cls, path: Path) -> "FictusFileSystem":
        """
        Create an FFS from a file or directory on disk.

        The provided directory becomes the logical root of the returned FFS: its
        contents are represented directly below ``/`` rather than preserving the
        source's absolute path. If ``path`` is a file, that file is placed at the
        virtual root.

        Raises:
            FictusException: If ``path`` does not exist.
        """
        source = Path(path).expanduser().resolve()
        if not source.exists():
            raise FictusException(f"Path does not exist: {source}")

        ffs = cls()

        if source.is_file():
            ffs.mkfile(source.name)
            return ffs

        for root, directories, files in os.walk(source):
            relative_root = Path(root).relative_to(source)
            if relative_root.parts:
                ffs.mkdir(relative_root.as_posix())

            for directory in directories:
                ffs.mkdir((relative_root / directory).as_posix())

            for file_name in files:
                ffs._to_root()
                if relative_root.parts:
                    ffs.cd(relative_root.as_posix())
                ffs.mkfile(file_name)

        ffs._to_root()

        return ffs

    def root(self) -> Folder:
        """Return the root of the FFS."""
        return self._root

    def current(self) -> Folder:
        """Return the FFS's current Folder being traversed."""
        return self._current

    @staticmethod
    def _normalize(path: str) -> str:
        return os.path.normpath(path.replace("\\", os.sep))

    @staticmethod
    def _validate(path: str) -> None:
        # will raise if path is empty
        if not path:
            raise FictusException("A path must contain a non-empty string.")

    def mkdir(self, path: str) -> None:
        """Takes a string of a normalized relative to cwd and adds the directories
        one at a time."""

        self._validate(path)

        # hold onto the current directory
        current = self._current

        normalized_path = self._normalize(path)
        if normalized_path.startswith(os.sep):
            self._to_root()
            normalized_path = self._normalize(self._root.value + normalized_path)

        folders = {d.value: d for d in self._current.children}

        for idx, part in enumerate(normalized_path.split(os.sep)):
            if not part:
                continue

            if idx == 0 and part.lower() == self._root.value.lower():
                self._to_root()
                continue

            if part not in folders:
                folders[part] = Folder(part, self._current)
                self._current.children.append(folders[part])

            self.cd(folders[part].value)
            folders = {d.value: d for d in self._current.children}

        # return to starting directory
        self._current = current

    def mkfile(self, *files: str) -> None:
        """Takes one or more filenames and adds them to the cwd."""
        visited: set[str] = {
            f.value for f in self._current.children if isinstance(f, File)
        }
        for file in files:
            self._validate(file)

            if file not in visited:
                visited.add(file)
                self._current.children.append(File(file, self._current))

    def add_directory_and_file(self, path: str) -> None:
        self._validate(path)

        parts = self._normalize(path).split(os.sep)
        folder = os.sep.join(parts[:-1])
        file = parts[-1]

        self._to_root()  # jump to root
        self.mkdir(folder)  # create dir
        self.cd(folder)  # jump to the directory
        self.mkfile(file)  # create file

    def rename(self, old: str, new: str) -> None:
        """Renames a File or Folder based on its name."""
        for content in self._current.children:
            if content.value == old:
                content.value = new
                break

    def cwd(self) -> str:
        """Prints the current working directory."""
        r = []

        node: Optional[Node] = self._current
        while node is not None:
            r.append(node.value)
            node = node.parent

        return f"{os.sep}".join(reversed(r))

    def _to_root(self) -> None:
        self._current = self._root

    def cd(self, path: str) -> None:
        """Takes a string of a normalized relative to cwd and changes the current"""
        # Return to the current dir if something goes wrong
        current = self._current

        normalized_path = self._normalize(path)
        if normalized_path.startswith(os.sep):
            self._to_root()
            normalized_path = self._normalize(self._root.value + normalized_path)

        for idx, part in enumerate(normalized_path.split(os.sep)):
            if not part:
                continue

            if idx == 0 and part.lower() == self._root.value.lower():
                self._to_root()
                continue

            if part == "..":
                # looking at the parent here, so ensure its valid.
                if isinstance(self._current.parent, Folder):
                    assert (
                        isinstance(self._current.parent, Folder) is True
                    )  # for typing
                    self._current = self._current.parent
            else:
                hm = {
                    f.value: f for f in self._current.children if isinstance(f, Folder)
                }
                if part not in hm:
                    self._current = current
                    raise FictusException(
                        f"Could not path to {normalized_path} from {self.cwd()}, {part} not a child of {self._current.value}."
                    )

                self._current = hm[part]
