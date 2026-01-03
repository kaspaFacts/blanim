# blanim\blanim\core\base_visual_block.py

from __future__ import annotations

__all__ = ["BaseVisualBlock", "validate_protocol_attributes"]

from typing import Union, Protocol, get_type_hints

import numpy as np
from manim import (
    Square,
    Text,
    WHITE,
    Transform,
    BLACK,
    Create,
    AnimationGroup,
    VGroup, YELLOW_C, PURE_BLUE, BLUE_E, RED_E, ParsableManimColor, BLUE
)

class BaseVisualBlock(VGroup):
    """Base class for blockchain block visualization.

    This is an abstract base class - do not instantiate directly.
    Child classes MUST set self.config in their __init__ before calling
    any highlighting methods.
    """

    square: Square
    label: Text

    def __init__(
            self,
            label_text: str,
            position: tuple[float, float],
            config: BlockConfigProtocol,
    ) -> None:
        super().__init__()

        self.config = config
        self._label_text = label_text

        #####Square#####
        self.square = Square(
            fill_color=config.block_color,
            fill_opacity=config.fill_opacity,
            stroke_color=config.stroke_color,
            stroke_width=config.stroke_width,
            stroke_opacity=config.stroke_opacity,
            side_length=config.side_length,
        )

        self.square.move_to((position[0], position[1], 0))

        self.background_rect = Square(
            side_length=config.side_length,
            fill_color=BLACK,
            fill_opacity=config.bg_rect_opacity,  # Allows slight line visibility
            stroke_width=0,
        )

        # Position background BEHIND square
        self.background_rect.move_to(self.square.get_center())

        #####Label (Primer Pattern)#####
        # Create invisible primer with 5-character capacity
        self.label = Text(
            "00000",  # 5 0's for default capacity
            font_size=1,
            color=BLACK,
        )
        self.label.move_to(self.square.get_center())

        # Add to VGroup
        self.add(self.background_rect, self.square, self.label)

        self.parent_lines = []

        # Set z_index at the end
        self.background_rect.set_z_index(11)
        self.square.set_z_index(12)
        self.label.set_z_index(13)

    def _get_label(self, text: str) -> Text:
        if not text or text.isspace():
            text = "\u200B"  # Zero-width space maintains position #TODO verify(this does not appear to maintain position)

        new_label = Text(
            text,
            font_size=self.config.label_font_size,
            color=self.config.label_color
        )
        new_label.move_to(self.square.get_center())
        return new_label

#TODO creates label by default but setting "" or " " breaks positioning of get_center on vgroup, figure out how to create invisible label that does not break positioning,
#   similar to narrate/caption  (Pretty sure positioning is fixed by overriding get_center() to return center of square, need to test label after setting to empty)
    def create_with_label(self):

        run_time = self.config.create_run_time

        # Create the square only (not the entire self)
        create_anim = Create(self.square, run_time=run_time)
        bgsquare_anim = Create(self.background_rect, run_time=run_time)

        # Transform primer to actual label (same run_time)
        actual_label = self._get_label(self._label_text)
        label_transform = Transform(self.label, actual_label, run_time=run_time)

        return AnimationGroup(create_anim, bgsquare_anim, label_transform)

    def change_label(self, text: Union[str, int]):
        # Convert int to str if needed
        if isinstance(text, int):
            text = str(text)

        run_time = self.config.label_change_run_time

        new_label = self._get_label(text)
        self._label_text = text
        return Transform(self.label, new_label, run_time=run_time)

    #TODO this is used in Bitcoin DAG only, REMOVE/REPLACE with create with label for consitency?
    def create_with_lines(self):
        """Returns AnimationGroup of block + label + lines creation."""
        run_time = self.config.create_run_time

        # Create animations for square AND background_rect together
        create_square = Create(self.square, run_time=run_time)
        create_bg = Create(self.background_rect, run_time=run_time)

        actual_label = self._get_label(self._label_text)
        label_transform = Transform(self.label, actual_label, run_time=run_time)

        anims = [create_square, create_bg, label_transform]
        for line in self.parent_lines:
            anims.append(Create(line, run_time=run_time))

        return AnimationGroup(*anims)

#TODO finish refactoring to eliminate base_config
    def create_highlight_animation(self, color=None, stroke_width=None):
        """Returns animation for highlighting this block's stroke."""
        if color is None:
            color = self.config.highlight_block_color
        if stroke_width is None:
            stroke_width = self.config.highlight_stroke_width

        return self.square.animate.set_stroke(color=color, width=stroke_width)

    def create_unhighlight_animation(self):
        """Returns animation to reset stroke to original config."""
        return self.square.animate.set_stroke(
            self.config.stroke_color,
            width=self.config.stroke_width
        )

    def create_pulsing_highlight(self, color=None, min_width=None, max_width=None):
        """Returns updater function for pulsing stroke effect."""
        if color is None:
            color = WHITE
        if min_width is None:
            min_width = self.config.stroke_width
        if max_width is None:
            max_width = self.config.highlight_stroke_width

        def pulse_stroke(mob, dt):
            t = getattr(mob, 'time', 0) + dt
            mob.time = t
            width = min_width + (max_width - min_width) * (np.sin(t * np.pi) + 1) / 2
            mob.set_stroke(color, width=width)

        return pulse_stroke

    ####################
    # Coloring Block Functions
    ####################

    def set_block_pure_blue(self):
        """Returns animation to set a block fill to BLUE"""
        return self.square.animate.set_fill(
            color=PURE_BLUE,
            opacity=0.9
        )

    def set_block_blue(self):
        """Returns animation to set a block fill to BLUE"""
        return self.square.animate.set_fill(
            color=BLUE_E,
            opacity=0.9
        )

    def set_block_red(self):
        """Returns animation to set a block fill to RED"""
        return self.square.animate.set_fill(
            color=RED_E,
            opacity=0.9
        )

    def set_block_stroke_yellow(self):
        """Returns animation to set a block stroke to YELLOW"""
        return self.square.animate.set_stroke(
            color=YELLOW_C
        )

    def reset_block_stroke_color(self):
        """Returns animation to set a block stroke to YELLOW"""
        return self.square.animate.set_stroke(
            color=self.stroke_color
        )

    ####################
    # Override Functions
    ####################

    # Override get_center() so it returns the center of the visual block
    def get_center(self) -> np.ndarray:
        """Override to return only the square's center, ignoring label positioning."""
        return self.square.get_center()


class BlockConfigProtocol(Protocol):
    """
    Protocol defining required interface for block configurations.

    WHY THIS EXISTS:
    ---------------
    This Protocol replaces BaseBlockConfig inheritance while maintaining type safety.
    It defines the exact contract that all consensus-type configs must implement
    to work with BaseVisualBlock. Every field in this protocol is REQUIRED in
    your consensus config class - missing any field will cause BaseVisualBlock
    to fail at runtime.

    DEVELOPER REQUIREMENTS:
    -----------------------
    When creating a new consensus config (e.g., NewConsensusConfig), you MUST
    implement ALL of these attributes with appropriate types. The Protocol
    ensures IDE autocomplete and static type checking work correctly.

    This is an INTERNAL interface - only developers extending the framework
    need to implement this. End users never interact with this Protocol directly.
    """

    # Visual styling - Block Appearance (REQUIRED for Square creation)
    block_color: ParsableManimColor
    fill_opacity: float
    bg_rect_opacity: float
    stroke_color: ParsableManimColor
    stroke_width: float
    stroke_opacity: float
    side_length: float

    # Label styling (REQUIRED for text rendering)
    label_font_size: int
    label_color: ParsableManimColor

    # Animation timing (REQUIRED for all animation methods)
    create_run_time: float
    label_change_run_time: float

    # Highlighting (REQUIRED for block highlighting effects)
    highlight_block_color: ParsableManimColor
    highlight_stroke_width: float

def _get_protocol_attributes() -> list[str]:
    """Extract all required attributes from Protocol automatically."""
    return [attr for attr, _ in get_type_hints(BlockConfigProtocol).items()
            if not attr.startswith('_')]

def validate_protocol_attributes(config) -> None:
    """Validate config has all Protocol attributes - auto-syncs with Protocol."""
    required_attrs = _get_protocol_attributes()
    missing = [attr for attr in required_attrs if not hasattr(config, attr)]
    if missing:
        raise AttributeError(f"Config missing required Protocol attributes: {missing}")