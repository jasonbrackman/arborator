from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional

T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    """A Node can have a maximum of one parent and zero to N number of children."""

    value: T
    parent: Optional[Node]
    children: list[Node] = field(default_factory=list)

    _height: int = field(init=False, default=0)

    def __post_init__(self):
        if self.parent:
            self._height = self.parent._height + 1

    def __lt__(self, other: Node) -> bool:
        return self.value > other.value

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, int) -> None:
        raise NotImplementedError("Not expected to be set externally.")


class File(Node):
    def __init__(self, name: str, parent: Node):
        super().__init__(name, parent)


class Folder(Node):
    def __init__(
        self, name, parent: Optional[Node], children: Optional[list[Node]] = None
    ):
        if children is None:
            children = []
        super().__init__(name, parent, children)
