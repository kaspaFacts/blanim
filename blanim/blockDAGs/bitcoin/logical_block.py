# blanim\blanim\blockDAGs\bitcoin\logical_block.py

from __future__ import annotations

__all__ = ["BitcoinLogicalBlock"]

from typing import Optional, List

from .visual_block import BitcoinVisualBlock

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import _BitcoinConfigInternal

class BitcoinLogicalBlock:
    """Bitcoin logical block with proxy pattern delegation."""

    def __init__(
            self,
            name: str,
            parent: Optional[BitcoinLogicalBlock] = None,
            position: tuple[float, float] = (0, 0),
            config: _BitcoinConfigInternal = None
    ):
        if config is None:
            raise ValueError("config parameter is required")
        self.config = config

        # Identity
        self.name = name
        self.hash = id(self)

        # DAG structure (single source of truth)
        self.parent = parent
        self.children: List[BitcoinLogicalBlock] = []

        # Weight = height for Bitcoin (single parent chain)
        # Genesis has weight 1, each child adds 1
        self.weight = 1 if parent is None else parent.weight + 1

        # Selected parent (always parent)
        self.selected_parent = self.parent if self.parent else None

        # Create visual (composition)
        # noinspection PyProtectedMember
        parent_visual = self.parent._visual if self.parent else None
        self._visual = BitcoinVisualBlock(
            label_text=str(self.name),
            position=position,
            parent=parent_visual,
            config=config  # Type-specific parameter
        )
        self._visual.logical_block = self  # Bidirectional link

        # Register as child in parents
        if parent:
            parent.children.append(self)

    def __getattr__(self, attr: str):
        """Proxy pattern: delegate to _visual."""
        # Avoid infinite recursion for _visual itself
        if attr == '_visual':
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '_visual'")
        # Delegate everything else to visual block
        return getattr(self._visual, attr)