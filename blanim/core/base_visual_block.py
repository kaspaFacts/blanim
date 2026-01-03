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
    VGroup, ParsableManimColor, Mobject
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

        # Store creation-time values for true reset
        self._creation_block_fill_color = config.block_color

        self._creation_block_stroke_color = config.stroke_color
        self._creation_block_stroke_width = config.stroke_width


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

        #####BG Square#####
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
    # Override Functions
    ####################

    # Override get_center() so it returns the center of the visual block
    def get_center(self) -> np.ndarray:
        """Override to return only the square's center, ignoring label positioning."""
        return self.square.get_center()

    ########################################
    # Visual Appearance Methods
    ########################################

    def set_block_fill_color(self, manim_color:ParsableManimColor) -> Mobject:
        """
        Returns an animatable Mobject for block fill color transformation.

        This is the core implementation that creates the animatable mobject
        using Manim's .animate system. The visual block handles the actual
        square manipulation while the logical block provides the public API.

        Parameters:
            manim_color: Any parsable Manim color (RED, BLUE, "#FF0000", (1,0,0), etc.)
                        Supports predefined colors, hex strings, and RGB tuples.
                        Colors are applied to the block's fill while preserving
                        stroke color and other visual properties.

        Returns:
            Mobject: An animatable Square that changes fill color when passed
                    to scene.play(). The returned object supports method chaining
                    with other .animate transformations.

        Examples:
            # Basic color animation
            animated = self.square.animate.set_fill(color=RED)
            self.play(animated)

            # Chain with position change
            self.play(self.square.animate.set_fill(color=BLUE).shift(UP))

            # Complex transformation chain
            self.play(
                self.square.animate
                    .set_fill(color=GREEN)
                    .scale(0.8)
                    .rotate(PI/6)
                    .shift(RIGHT * 2)
            )

            # Using different color formats
            self.play(self.square.animate.set_fill(color="#FF5733"))  # Hex
            self.play(self.square.animate.set_fill(color=(1, 0, 0)))   # RGB Red
            self.play(self.square.animate.set_fill(color=(0, 1, 0)))   # RGB Green

        Implementation Details:
            Uses Manim's native .animate system which returns an animatable
            version of the mobject. The actual Animation object is created
            internally when passed to scene.play(). This follows the same
            pattern as other visual block methods.

        Performance Notes:
            - Method chaining creates a single optimized animation
            - Separate play() calls create multiple sequential animations
            - Chaining is both more efficient and provides smoother visual transitions

            # Efficient: Single combined animation
            self.play(self.square.animate.set_fill(RED).scale(2))

            # Less efficient: Multiple separate animations
            self.play(self.square.animate.set_fill(RED))
            self.play(self.square.animate.scale(2))

        See Also:
            create_highlight_animation: Create stroke highlight without fill change
            set_block_stroke_color: Change border color instead of fill
            reset_block_color: Reset fill to config default

        Notes:
            - Returns animatable mobject, not Animation object
            - Preserves stroke color, opacity, and other properties
            - Only modifies the fill color of the block's square
            - Follows blanim's animation return pattern for consistency
            - Config parameters like default colors are defined in consensus-specific configs
        """
        return self.square.animate.set_fill(color=manim_color)

    def reset_block_fill_color(self) -> Mobject:
        """
        Returns an animatable Mobject to reset fill color to creation-time values.

        This method restores the block's fill color to what it was when initially
        created, preserving the user's original design intent regardless of any
        subsequent config modifications or temporary color changes.

        Returns:
            Mobject: An animatable Square that resets fill color when passed to
                    scene.play(). The returned object supports method chaining
                    with other .animate transformations.

        Examples:
            # Reset fill color after temporary highlighting
            self.play(block.set_block_fill_color(RED))
            self.wait(1)
            self.play(block.reset_block_fill_color())

            # Chain reset with other transformations
            self.play(block.reset_block_fill_color().scale(1.2))

            # Reset multiple blocks simultaneously
            self.play(
                block1.reset_block_fill_color(),
                block2.reset_block_fill_color(),
                block3.reset_block_fill_color()
            )

            # Use in animation sequences
            self.play(
                block.set_block_fill_color(YELLOW),
                block.scale(1.5)
            )
            self.play(block.reset_block_fill_color())

        Implementation Details:
            Uses the creation-time color stored in self._creation_block_fill_color
            during BaseVisualBlock initialization. This preserves the original
            appearance even if config values are modified during the scene.
            The actual Animation object is created internally when passed to
            scene.play().

        Performance Notes:
            - Reset operations are single-property animations and are very fast
            - Can be chained with other animations for combined effects
            - More efficient than manually tracking and restoring color values

            # Efficient: Combined reset and transform
            self.play(block.reset_block_fill_color().shift(UP))

            # Less efficient: Separate operations
            self.play(block.reset_block_fill_color())
            self.play(block.shift(UP))

        See Also:
            set_block_fill_color: Change fill color to any specified color
            reset_block_stroke_color: Reset stroke color to creation values
            create_highlight_animation: Create stroke highlight without fill change

        Notes:
            - Returns animatable mobject, not Animation object
            - Only affects fill color, preserves stroke color and other properties
            - Uses creation-time values, not current config values
            - Follows blanim's animation return pattern for consistency
            - Creation values are stored during BaseVisualBlock initialization
        """
        return self.square.animate.set_fill(color=self._creation_block_fill_color)

    def set_block_stroke_color(self, manim_color: ParsableManimColor) -> Mobject:
        """
        Returns an animatable Mobject for block stroke color transformation.

        This method creates an animatable mobject that changes the block's border
        (stroke) color while preserving fill color and other visual properties.
        The stroke color change is commonly used for highlighting blocks during
        consensus algorithm visualization.

        Parameters:
            manim_color: Any parsable Manim color (RED, BLUE, "#FF0000", (1,0,0), etc.)
                        Supports predefined colors, hex strings, and RGB tuples.
                        Colors are applied to the block's stroke while preserving
                        fill color and other visual properties.

        Returns:
            Mobject: An animatable Square that changes stroke color when passed
                    to scene.play(). The returned object supports method chaining
                    with other .animate transformations.

        Examples:
            # Basic stroke color change
            self.play(block.set_block_stroke_color(YELLOW))

            # Chain with fill color change
            self.play(block.set_block_stroke_color(GREEN).set_block_fill_color(BLUE))

            # Chain with position and scale
            self.play(
                block.set_block_stroke_color(RED)
                    .shift(UP)
                    .scale(1.2)
            )

            # Using different color formats
            self.play(block.set_block_stroke_color("#FF5733"))  # Hex
            self.play(block.set_block_stroke_color((1, 0, 0)))   # RGB Red
            self.play(block.set_block_stroke_color((0, 1, 0)))   # RGB Green

            # Highlight during consensus evaluation
            self.play(block.set_block_stroke_color(YELLOW))
            self.wait(0.5)
            self.play(block.reset_block_stroke_color())

        Implementation Details:
            Uses Manim's native .animate system which returns an animatable
            version of the mobject. The actual Animation object is created
            internally when passed to scene.play(). This follows the same
            pattern as other visual block methods and only modifies the
            stroke property of the square.

        Performance Notes:
            - Method chaining creates a single optimized animation
            - Separate play() calls create multiple sequential animations
            - Stroke changes are typically faster than fill changes

            # Efficient: Single combined animation
            self.play(block.set_block_stroke_color(YELLOW).scale(1.1))

            # Less efficient: Multiple separate animations
            self.play(block.set_block_stroke_color(YELLOW))
            self.play(block.scale(1.1))

        See Also:
            reset_block_stroke_color: Reset stroke to creation color
            set_block_fill_color: Change fill color instead of stroke
            create_highlight_animation: Create comprehensive highlight effect

        Notes:
            - Returns animatable mobject, not Animation object
            - Preserves fill color, opacity, and other properties
            - Only modifies the stroke color of the block's square
            - Commonly used for block highlighting in consensus visualizations
            - Follows blanim's animation return pattern for consistency
        """
        return self.square.animate.set_stroke(color=manim_color)

    def reset_block_stroke_color(self) -> Mobject:
        """
        Returns an animatable Mobject to reset stroke color to creation-time values.

        This method restores the block's stroke (border) color to what it was when
        initially created, preserving the user's original design intent regardless
        of any subsequent highlighting or temporary color changes.

        Returns:
            Mobject: An animatable Square that resets stroke color when passed to
                    scene.play(). The returned object supports method chaining
                    with other .animate transformations.

        Examples:
            # Reset stroke color after highlighting
            self.play(block.set_block_stroke_color(YELLOW))
            self.wait(1)
            self.play(block.reset_block_stroke_color())

            # Chain reset with other transformations
            self.play(block.reset_block_stroke_color().scale(0.8))

            # Reset multiple blocks after consensus evaluation
            self.play(
                evaluated_block.reset_block_stroke_color(),
                candidate_block.reset_block_stroke_color(),
                selected_block.reset_block_stroke_color()
            )

            # Use in animation sequences
            self.play(
                block.set_block_stroke_color(RED),
                block.set_block_fill_color(BLUE)
            )
            self.play(block.reset_block_stroke_color())

        Implementation Details:
            Uses the creation-time color stored in self._creation_block_stroke_color
            during BaseVisualBlock initialization. This preserves the original
            appearance even after temporary highlighting during consensus algorithm
            visualization. The actual Animation object is created internally when
            passed to scene.play().

        Performance Notes:
            - Reset operations are single-property animations and are very fast
            - Can be chained with other animations for combined effects
            - Essential for clean consensus visualization state management

            # Efficient: Combined reset and transform
            self.play(block.reset_block_stroke_color().shift(DOWN))

            # Less efficient: Separate operations
            self.play(block.reset_block_stroke_color())
            self.play(block.shift(DOWN))

        See Also:
            set_block_stroke_color: Change stroke color to any specified color
            reset_block_fill_color: Reset fill color to creation values
            create_unhighlight_animation: Reset all visual properties

        Notes:
            - Returns animatable mobject, not Animation object
            - Only affects stroke color, preserves fill color and other properties
            - Uses creation-time values, not current config values
            - Essential for proper consensus visualization cleanup
            - Follows blanim's animation return pattern for consistency
        """
        return self.square.animate.set_stroke(color=self._creation_block_stroke_color)

    def set_block_stroke_width(self, width: float) -> Mobject:
        """Returns animatable Mobject to set block stroke width."""
        return self.square.animate.set_stroke(width=width)

    def reset_block_stroke_width(self) -> Mobject:
        """Returns animatable Mobject to reset stroke width to creation value."""
        return self.square.animate.set_stroke(width=self._creation_block_stroke_width)

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