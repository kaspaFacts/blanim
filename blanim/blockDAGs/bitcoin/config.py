# blanim/blanim/blockDAGs/bitcoin/config.py

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TypedDict
from manim import BLUE, WHITE, ParsableManimColor, ORANGE, logger

from ...core.base_config import BaseBlockConfig
from ...core.base_visual_block import validate_protocol_attributes

__all__ = ["DEFAULT_BITCOIN_CONFIG", "BitcoinConfig", "_BitcoinConfigInternal"]


# Public TypedDict for user type hints
class BitcoinConfig(TypedDict, total=False):
    """Typed configuration for Bitcoin blockchain visualization."""

    # Visual Styling - Block Appearance
    block_color: ParsableManimColor
    fill_opacity: float
    bg_rect_opacity: float
    stroke_color: ParsableManimColor
    stroke_width: float
    stroke_opacity: float
    side_length: float

    # Visual Styling - Label Appearance
    label_font_size: int
    label_color: ParsableManimColor
    label_opacity: float

    # Visual Styling - Line Appearance
    line_color: ParsableManimColor
    line_stroke_width: float
    line_stroke_opacity: float

    # Animation Timing
    create_run_time: float
    label_change_run_time: float
    movement_run_time: float
    camera_follow_time: float

    # Highlighting Behavior
    context_block_color: ParsableManimColor
    context_block_cycle_time: float
    context_block_stroke_width: float
    highlight_block_color: ParsableManimColor
    highlight_stroke_width: float
    fade_opacity: float
    flash_connections: bool
    highlight_line_cycle_time: float

    # Spatial Layout
    genesis_x: float
    genesis_y: float
    horizontal_spacing: float
    vertical_spacing: float

@dataclass
class _BitcoinConfigInternal(BaseBlockConfig):
    """Complete configuration for Bitcoin blockchain visualization.

    Combines visual styling and spatial layout into a single config.
    Each section is clearly separated for maintainability.

    WARNING opacity must ALWAYS be > 0
    """

    # ========================================
    # VISUAL STYLING - Block Appearance
    # ========================================
    block_color: ParsableManimColor = BLUE
    fill_opacity: float = 0.2
    bg_rect_opacity: float = 0.9  # Allows slight line visibility
    stroke_color: ParsableManimColor = BLUE
    stroke_width: float = 3
    stroke_opacity: float = 1.0
    side_length: float = 0.7

    # ========================================
    # VISUAL STYLING - Label Appearance
    # ========================================
    label_font_size: int = 24
    label_color: ParsableManimColor = WHITE
    label_opacity: float = 1.0

    # ========================================
    # VISUAL STYLING - Line Appearance
    # ========================================
    line_color: ParsableManimColor = BLUE
    line_stroke_width: float = 5
    line_stroke_opacity: float = 1.0

    # ========================================
    # ANIMATION TIMING
    # ========================================
    create_run_time: float = 2.0
    label_change_run_time: float = 1.0
    movement_run_time: float = 1.0
    camera_follow_time: float = 1.0

    # ========================================
    # HIGHLIGHTING BEHAVIOR
    # ========================================
    # Context Block is the block we show relationships of during highlighting
    context_block_color: ParsableManimColor = WHITE  # Color of pulsing stroke
    context_block_cycle_time: float = 2.0  # Seconds per complete pulse cycle
    context_block_stroke_width: float = 8

    # Highlight blocks with relationships to the Context Block
    highlight_block_color: ParsableManimColor = ORANGE
    highlight_stroke_width: float = 8

    fade_opacity: float = 0.3  # Opacity to fade unrelated blocks to during a highlight animation

    flash_connections: bool = True  # Directional flash animation cycling on lines
    highlight_line_cycle_time = 1  # Time for a single flash to pass on lines

    # ========================================
    # SPATIAL LAYOUT - Genesis Position
    # ========================================
    genesis_x: float = -5.5
    genesis_y: float = 0.0

    # ========================================
    # SPATIAL LAYOUT - Block Spacing
    # ========================================
    horizontal_spacing: float = 2.0
    vertical_spacing: float = 1.0  # For parallel blocks during forks

    def __post_init__(self):
        """Validate and auto-correct values with warnings."""
        # Auto-validate Protocol attributes
        validate_protocol_attributes(self)

        # Auto-correct opacity values
        if self.fill_opacity <= 0:
            logger.warning("fill_opacity must be > 0, auto-correcting to 0.01")
            self.fill_opacity = 0.01
        elif self.fill_opacity > 1.0:
            logger.warning("fill_opacity must be <= 1.0, auto-correcting to 1.0")
            self.fill_opacity = 1.0

        if self.stroke_opacity <= 0:
            logger.warning("stroke_opacity must be > 0, auto-correcting to 0.01")
            self.stroke_opacity = 0.01
        elif self.stroke_opacity > 1.0:
            logger.warning("stroke_opacity must be <= 1.0, auto-correcting to 1.0")
            self.stroke_opacity = 1.0

        if self.fade_opacity < 0:
            logger.warning("fade_opacity must be >= 0, auto-correcting to 0")
            self.fade_opacity = 0
        elif self.fade_opacity > 1.0:
            logger.warning("fade_opacity must be <= 1.0, auto-correcting to 1.0")
            self.fade_opacity = 1.0

            # Auto-correct other critical values
        if self.stroke_width < 1:
            logger.warning("stroke_width must be >= 1, auto-correcting to 1")
            self.stroke_width = 1

def _get_dataclass_fields(cls) -> set[str]:
    """Extract all field names from a dataclass."""
    return {field.name for field in fields(cls)}

def _get_typeddict_fields(cls) -> set[str]:
    """Extract all field names from a TypedDict."""
    return set(cls.__annotations__.keys())

def validate_typeddict_completeness() -> None:
    """Validate that BitcoinConfig TypedDict includes all _BitcoinConfigInternal fields."""
    dataclass_fields = _get_dataclass_fields(_BitcoinConfigInternal)
    typeddict_fields = _get_typeddict_fields(BitcoinConfig)

    missing_fields = dataclass_fields - typeddict_fields
    if missing_fields:
        raise AttributeError(
            f"BitcoinConfig TypedDict missing {len(missing_fields)} fields from _BitcoinConfigInternal: "
            f"{sorted(missing_fields)}. Add these fields to ensure users can modify all parameters."
        )

    # Default configuration instance

DEFAULT_BITCOIN_CONFIG = _BitcoinConfigInternal()