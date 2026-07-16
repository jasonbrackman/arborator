from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from .constants import PIPE, SPACER_PREFIX, ELBOW, TEE, SPACER
from .fictusexception import FictusException
from .fictusfilesystem import FictusFileSystem
from .fictusnode import Folder, Node, File
from .renderer import Renderer, defaultRenderer, RenderTagEnum


class FictusDisplay:
    def __init__(self, ffs: FictusFileSystem):
        self._ffs = ffs
        self._renderer = defaultRenderer
        self._ignore: set[int] = set()

    @property
    def renderer(self) -> Renderer:
        return self._renderer

    @renderer.setter
    def renderer(self, renderer: Renderer) -> None:
        self._renderer = renderer

    def _wrap_node_name_with_tags(self, node: Node):
        # setup defaults
        key = RenderTagEnum.FILE

        # account for the distinction between root and all other folders
        if isinstance(node, Folder):
            if node == self._ffs.root():
                key = RenderTagEnum.ROOT
            else:
                key = RenderTagEnum.FOLDER

        tags = self.renderer.tags(key)

        return f"{tags.open}{node.value}{tags.close}"

    def _display_node(self, node: Node, last: bool, node_level_start: int) -> str:
        """
        Bookkeeping of nested node depth, node siblings, and order in the queue are
        used to present the FicusSystem in an aesthetic way.
        """

        parts = [PIPE + SPACER_PREFIX for _ in range(node_level_start, node.height)]

        for index in self._ignore:
            if 0 < len(parts) > index - 1:
                parts[index - 1] = SPACER + SPACER_PREFIX

        if parts:
            parts[-1] = ELBOW if last is True else TEE

        return f'{"".join(parts)}{self._wrap_node_name_with_tags(node)}'

    @staticmethod
    def _custom_sort(nodes: list[Node]) -> list[Node]:
        """Reverse sort the children by file, then name."""
        return sorted(nodes, key=lambda x: (isinstance(x, File), x.value.lower()), reverse=True)

    def pprint(self, renderer: Optional[Renderer] = None) -> None:
        """Displays the file system structure to stdout."""

        old_renderer, self._renderer = self._renderer, renderer or self._renderer

        node_start = self._ffs.current()

        # sometimes the height starts offset from the start, so account for that
        offset = node_start.height
        node_level_start = node_start.height

        self._ignore = set()

        prefix: int = -1  # not set

        buffer: list[str] = []

        q: list[tuple[Node, bool]] = [(node_start, True)]
        while q:
            node, last = q.pop()
            if last is False:
                if node.height in self._ignore:
                    self._ignore.remove(node.height)
            line: str = self._display_node(node, last, node_level_start)

            # This needs to happen only once and applied
            # thereafter to each subsequent line.
            prefix = len(line) - len(line.lstrip()) if prefix == -1 else prefix
            buffer.append(f"{line[prefix:]}\n")
            if last is True:
                # track nodes without children.
                self._ignore.add(node.height - offset)

            if isinstance(node, Folder) and node.children:
                children = self._custom_sort(node.children)
                sorted_children = [(child, False) for child in children]
                c, _ = sorted_children[0]
                sorted_children[0] = (c, True)

                q += sorted_children

        # output data
        sys.stdout.write(self._renderer.tags(RenderTagEnum.DOC).open)
        sys.stdout.writelines(buffer)
        sys.stdout.write(self._renderer.tags(RenderTagEnum.DOC).close)

        # reset renderer to what it was
        self._renderer = old_renderer

    # Reforestation methods - - - - - - -
    @staticmethod
    def _validate_output_name(name: str) -> None:
        """Ensure a virtual node name cannot escape the output directory."""
        if not name or name in {".", ".."} or "/" in name or "\\" in name:
            raise FictusException(
                f"Cannot materialize unsafe virtual node name {name!r}."
            )

    @staticmethod
    def _path_within(candidate: Path, destination: Path) -> bool:
        try:
            candidate.resolve().relative_to(destination)
        except ValueError:
            return False
        return True

    def reforestation(
        self, path: Path, encoding: str = "utf-8", overwrite: bool = False
    ) -> None:
        """
        Materialize the current virtual subtree under ``path``.

        Existing directories are reused. Existing files are preserved unless
        ``overwrite`` is explicitly True. Virtual node names that could escape the
        destination directory are rejected.
        """
        destination = Path(path).resolve()
        if destination.exists() and not destination.is_dir():
            raise FictusException(f"Output path must be a directory: {destination}")
        destination.mkdir(parents=True, exist_ok=True)

        node_start = self._ffs.current()
        q: list[tuple[Node, Path]] = [(node_start, destination)]
        while q:
            node, real_path = q.pop()
            if isinstance(node, Folder):
                real_path.mkdir(parents=True, exist_ok=True)
            else:
                if real_path.exists() and not overwrite:
                    raise FictusException(
                        f"Refusing to overwrite existing file: {real_path}"
                    )
                with real_path.open("w", encoding=encoding) as f:
                    f.write("")

            if isinstance(node, Folder):
                for child in node.children:
                    self._validate_output_name(child.value)
                    child_path = real_path / child.value
                    if not self._path_within(child_path, destination):
                        raise FictusException(
                            f"Refusing to write outside output path: {child_path}"
                        )
                    q.append((child, child_path))
