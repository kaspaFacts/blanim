# blanim\blanim\blockDAGs\kaspa\logical_block.py

from __future__ import annotations

__all__ = ["KaspaLogicalBlock", "VirtualKaspaBlock"]

import secrets
from dataclasses import dataclass, field

from manim import ParsableManimColor, Animation, Square, Mobject

from .visual_block import KaspaVisualBlock
from typing import Optional, List, Set, Any, Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ... import _KaspaConfigInternal

@dataclass
class GhostDAGData:
    """GHOSTDAG consensus data for a block."""
    blue_score: int = 0  # Total blue work in past cone
    unordered_mergeset: List['KaspaLogicalBlock'] = field(default_factory=list)
    blue_anticone: Set['KaspaLogicalBlock'] = field(default_factory=set)

    # NEW: Store local POV - blue status of all blocks evaluated from this block's perspective
    local_blue_pov: Dict['KaspaLogicalBlock', bool] = field(default_factory=dict)

class KaspaLogicalBlock:
    """Kaspa logical block with GHOSTDAG consensus."""

    def __init__(
            self,
            name: str,
            timestamp: Optional[float] = None,
            parents: Optional[List[KaspaLogicalBlock]] = None,
            position: tuple[float, float] = (0, 0),
            config: _KaspaConfigInternal = None,
            custom_label: Optional[str] = None,
            custom_hash: Optional[int] = None
    ):
        if config is None:
            raise ValueError("config parameter is required")
        self.config = config

        # Identity
        self.name = name
        # Time Created
        self.timestamp = timestamp
        # Tie-breaker (instead of actually hashing, just use a random number like a cryptographic hash)
        self.hash = custom_hash if custom_hash is not None else secrets.randbits(32)  # 32-bit random integer to keep prob(collision) = low

        # DAG structure (single source of truth)
        self.parents = parents if parents else []
        self.children: List[KaspaLogicalBlock] = []

        # GHOSTDAG data
        self.ghostdag = GhostDAGData()
        self.selected_parent: Optional['KaspaLogicalBlock'] = None

        # Parent selection and GHOSTDAG computation (before visualization)
        if self.parents:
            self.selected_parent = self._select_parent()
            self.parents.sort(key=lambda p: p != self.selected_parent) #move SP to the index 0 before sending to visual
            self._create_unordered_mergeset()
            self._compute_ghostdag(self.config.k)

        # Create visual after GHOSTDAG computation
        parent_visuals = [p.visual_block for p in self.parents]

        # Custom Label if passed
        label_text = custom_label if custom_label is not None else str(self.ghostdag.blue_score)

        self._visual = KaspaVisualBlock(
            label_text=label_text,#TODO update this  NOTE: when passing an empty string, positioning breaks (fixed moving blocks by overriding move_to with only visual.square)
            position=position,
            parents=parent_visuals,
            config=self.config
        )
        self._visual.logical_block = self  # Bidirectional link

        # Register as child in parents
        for parent in self.parents:
            parent.children.append(self)

    @staticmethod
    def _get_sort_key(block: 'KaspaLogicalBlock') -> tuple:
        """Standardized tie-breaking: (blue_score, -hash) for ascending order."""
        return block.ghostdag.blue_score, -block.hash

    def _select_parent(self) -> Optional['KaspaLogicalBlock']:
        """Select parent with highest blue score, deterministic hash tie-breaker."""
        if not self.parents:
            return None

        # Sort by (blue_score, -hash) - highest first, so reverse=True
        sorted_parents = sorted(
            self.parents,
            key=self._get_sort_key,
            reverse=True
        )
        return sorted_parents[0]

    def _create_unordered_mergeset(self):
        """Compute mergeset without sorting."""
        if not self.selected_parent:
            self.ghostdag.unordered_mergeset = []
            return

        self_past = set(self.get_past_cone())
        selected_past = set(self.selected_parent.get_past_cone())
        self.ghostdag.unordered_mergeset = list(self_past - selected_past)

    def get_sorted_mergeset_with_sp(self) -> List['KaspaLogicalBlock']:
        """Get sorted mergeset with selected parent at index 0."""
        if not self.selected_parent:
            return []

            # Start with selected parent
        sorted_mergeset = [self.selected_parent]

        # Add and sort the rest (excluding selected parent)
        remaining = [block for block in self.ghostdag.unordered_mergeset if block != self.selected_parent]
        remaining.sort(key=self._get_sort_key)
        sorted_mergeset.extend(remaining)

        return sorted_mergeset

    def get_sorted_mergeset_without_sp(self) -> List['KaspaLogicalBlock']:
        """Get sorted mergeset excluding selected parent."""
        evaluation_mergeset = [block for block in self.ghostdag.unordered_mergeset if block != self.selected_parent]
        evaluation_mergeset.sort(key=self._get_sort_key)
        return evaluation_mergeset

    def _compute_ghostdag(self, k: int):
        """Compute GHOSTDAG consensus with parameter k."""
        if not self.selected_parent:
            return

        total_view = set(self.get_past_cone())
        selected_parent_blue_score = self.selected_parent.ghostdag.blue_score

        # Start with selected parent's local POV as baseline
        local_blue_status = self.selected_parent.ghostdag.local_blue_pov.copy()

        # Add selected parent itself as blue
        local_blue_status[self.selected_parent] = True

        blue_candidates = self.get_sorted_mergeset_without_sp()

        # Initialize all candidates as not blue locally
        for candidate in blue_candidates:
            local_blue_status[candidate] = False

        blue_in_mergeset = 0

        # Process candidates using local blue status
        for candidate in blue_candidates:
            if self._can_be_blue_local(candidate, local_blue_status, k, total_view):
                local_blue_status[candidate] = True
                blue_in_mergeset += 1
            else:
                local_blue_status[candidate] = False

                # Store the complete local POV (removed is_blue assignment)
        self.ghostdag.local_blue_pov = local_blue_status.copy()
        self.ghostdag.blue_score = selected_parent_blue_score + 1 + blue_in_mergeset

    def _can_be_blue_local(self,
                           candidate: 'KaspaLogicalBlock',
                           local_blue_status: Dict['KaspaLogicalBlock', bool],
                           k: int,
                           total_view: Set['KaspaLogicalBlock']) -> bool:
        """Check if candidate can be blue using local perspective."""

        # Get blue blocks from local perspective
        blue_blocks = {block for block, is_blue in local_blue_status.items() if is_blue}

        # Check 1: <= k blue blocks in candidate's anticone
        candidate_anticone = self.get_anticone(candidate, total_view)
        blue_in_anticone = len(candidate_anticone & blue_blocks)
        if blue_in_anticone > k:
            return False

            # Check 2: Adding candidate doesn't cause existing blues to have > k blues in anticone
        for blue_block in blue_blocks:
            blue_anticone = self.get_anticone(blue_block, total_view)
            if candidate in blue_anticone:
                blue_in_anticone = len(blue_anticone & blue_blocks) + 1
                if blue_in_anticone > k:
                    return False

        return True

    # TODO figure out if this can be replaced or if dag.get_anticone can be replaced
    @staticmethod
    def get_anticone(block: 'KaspaLogicalBlock',
                      total_view: Set['KaspaLogicalBlock']
                      ) -> Set['KaspaLogicalBlock']:
        """Get anticone of a block within the given total view."""
        past = set(block.get_past_cone())
        future = set(block.get_future_cone())

        # Anticone = total_view - past - future - block itself
        return total_view - past - future - {block}

    def get_dag_pov(self, target_block: 'KaspaLogicalBlock') -> Dict['KaspaLogicalBlock', bool]:
        """Get the DAG blue status from target_block's perspective recursively."""
        if target_block == self:
            return self.ghostdag.local_blue_pov.copy()

        # Recursively find the target block in the past cone
        for parent in self.parents:
            pov = parent.get_dag_pov(target_block)
            if pov is not None:
                return pov

        return {}
    ########################################
    # Collecting Past/Future
    ########################################

    def get_past_cone(self) -> List[KaspaLogicalBlock]:
        """Get all ancestors via depth-first search."""
        past = set()
        to_visit = [self]

        while to_visit:
            current = to_visit.pop()
            for parent in current.parents:
                if parent not in past:
                    past.add(parent)
                    to_visit.append(parent)

        return list(past)

    def get_future_cone(self) -> List[KaspaLogicalBlock]:
        """Get all descendants via depth-first search."""
        future = set()
        to_visit = [self]

        while to_visit:
            current = to_visit.pop()
            for child in current.children:
                if child not in future:
                    future.add(child)
                    to_visit.append(child)

        return list(future)

    ########################################
    # Accessing Visual Block
    ########################################

    @property
    def visual_block(self) -> KaspaVisualBlock:
        """Public accessor for the visual block."""
        return self._visual

    def __getattr__(self, attr: str) -> Any:
        """Proxy pattern: delegate to _visual."""
        if attr == '_visual':
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '_visual'")
        return getattr(self._visual, attr)

    ########################################
    # Visual Appearance Methods - Delegated to Visual Block
    ########################################

    def set_block_fill_color(self, manim_color:ParsableManimColor) -> Mobject:
        """
        Returns an animatable Mobject for block fill color transformation.

        This method delegates to the visual block while maintaining type hints
        and providing a clean public API through the proxy pattern.

        Parameters:
            manim_color: Any parsable Manim color (RED, BLUE, "#FF0000", (1,0,0), etc.)
                        Supports predefined colors, hex strings, and RGB tuples.

        Returns:
            Mobject: An animatable version of the block that changes fill color
                    when passed to scene.play(). Supports method chaining.

        Examples:
            # Single color change
            self.play(block.set_block_fill_color(RED))

            # Chain with scale transformation
            self.play(block.set_block_fill_color(BLUE).scale(2))

            # Chain multiple transformations
            self.play(block.set_block_fill_color(GREEN).scale(1.5).rotate(PI/4))

            # Use in AnimationGroup with other animations
            self.play(
                block.set_block_fill_color(YELLOW),
                other_block.animate.shift(RIGHT)
            )

            # Using different color formats
            self.play(block.set_block_fill_color("#FF5733"))        # Hex color
            self.play(block.set_block_fill_color((1, 0, 0)))        # RGB tuple Red
            self.play(block.set_block_fill_color((0, 1, 0)))        # RGB tuple Green

        Performance Notes:
            Method chaining is more efficient than separate play() calls as it
            creates a single animation rather than multiple sequential ones.

            # Less efficient (creates 2 animations):
            self.play(block.set_block_fill_color(RED))
            self.play(block.scale(2))

            # More efficient (creates 1 combined animation):
            self.play(block.set_block_fill_color(RED).scale(2))

        See Also:
            set_block_stroke_color: Change border/stroke color
            set_block_opacity: Change transparency/fill opacity
            create_highlight_animation: Create stroke highlight effect
            visual_block.set_block_fill_color: Direct visual block implementation

        Notes:
            - Follows Manim's .animate convention for chaining
            - The returned Mobject is not an Animation object itself
            - Multiple animations on the same mobject in one play() call
              follow "last animation wins" rule unless chained
            - Uses the proxy delegation pattern
        """
        return self.visual_block.set_block_fill_color(manim_color)

    def reset_block_fill_color(self) -> Mobject:
        """
        Returns an animatable Mobject to reset fill color to creation-time values.

        This method delegates to the visual block while maintaining type hints
        and providing a clean public API through the proxy pattern. The reset
        restores the block's fill color to what it was when initially created,
        preserving the user's original design intent.

        Returns:
            Mobject: An animatable version of the block that resets fill color
                    when passed to scene.play(). The returned object supports
                    method chaining with other .animate transformations.

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
            Uses the proxy delegation pattern to forward the reset operation
            to the visual block's reset_block_fill_color() method. The visual
            block stores creation-time values during initialization and uses
            those for the reset rather than current config values.

        Performance Notes:
            - Reset operations are single-property animations and are very fast
            - Can be chained with other animations for combined effects
            - More efficient than manually tracking and restoring color values

            # Efficient: Combined reset and transform
            self.play(block.reset_block_fill_color().shift(DOWN))

            # Less efficient: Separate operations
            self.play(block.reset_block_fill_color())
            self.play(block.shift(DOWN))

        See Also:
            set_block_fill_color: Change fill color to any specified color
            reset_block_stroke_color: Reset stroke color to creation values
            visual_block.reset_block_fill_color: Direct visual block implementation

        Notes:
            - Returns animatable mobject, not Animation object
            - Only affects fill color, preserves stroke color and other properties
            - Uses creation-time values, not current config values
            - Follows the proxy delegation pattern for clean API separation
            - Preserves user's original design intent regardless of config changes
        """
        return self.visual_block.reset_block_fill_color()

    def set_block_stroke_color(self, manim_color: ParsableManimColor) -> Mobject:
        """
        Returns an animatable Mobject for block stroke color transformation.

        This method delegates to the visual block while maintaining type hints
        and providing a clean public API through the proxy pattern. The stroke
        color change affects only the border outline of the block.

        Parameters:
            manim_color: Any parsable Manim color (RED, BLUE, "#FF0000", (1,0,0), etc.)
                        Supports predefined colors, hex strings, and RGB tuples.
                        Colors are applied to the block's stroke while preserving
                        fill color and other visual properties.

        Returns:
            Mobject: An animatable version of the block that changes stroke color
                    when passed to scene.play(). The returned object supports
                    method chaining with other .animate transformations.

        Examples:
            # Single stroke color change
            self.play(block.set_block_stroke_color(YELLOW))

            # Chain with position change
            self.play(block.set_block_stroke_color(GREEN).shift(UP))

            # Chain multiple transformations
            self.play(
                block.set_block_stroke_color(ORANGE)
                      .scale(1.5)
                      .rotate(PI/6)
                      .shift(RIGHT * 2)
            )

            # Use in AnimationGroup with other animations
            self.play(
                block.set_block_stroke_color(PURPLE),
                other_block.animate.shift(LEFT)
            )

            # Using different color formats
            self.play(block.set_block_stroke_color("#FF5733"))     # Hex color
            self.play(block.set_block_stroke_color((1, 0, 0)))      # RGB Red
            self.play(block.set_block_stroke_color((0, 1, 0)))      # RGB Green

        Implementation Details:
            Uses the proxy delegation pattern to forward the stroke color
            operation to the visual block's set_block_stroke_color() method.
            The visual block handles the actual Manim .animate system
            implementation while the logical block provides the public API.

        Performance Notes:
            - Method chaining creates a single optimized animation
            - Separate play() calls create multiple sequential animations
            - Chaining is both more efficient and provides smoother visual transitions

            # Efficient: Single combined animation
            self.play(block.set_block_stroke_color(RED).scale(2))

            # Less efficient: Multiple separate animations
            self.play(block.set_block_stroke_color(RED))
            self.play(block.scale(2))

        See Also:
            set_block_fill_color: Change fill color instead of stroke
            reset_block_stroke_color: Reset stroke to creation values
            visual_block.set_block_stroke_color: Direct visual block implementation

        Notes:
            - Returns animatable mobject, not Animation object
            - Preserves fill color, opacity, and other properties
            - Only modifies the stroke color of the block's square
            - Follows Manim's .animate convention for chaining
            - Uses the proxy delegation pattern for clean API separation
        """
        return self.visual_block.set_block_stroke_color(manim_color)

    def reset_block_stroke_color(self) -> Mobject:
        """
        Returns an animatable Mobject to reset stroke color to creation-time values.

        This method delegates to the visual block while maintaining type hints
        and providing a clean public API through the proxy pattern. The reset
        restores the block's stroke color to what it was when initially created,
        preserving the user's original design intent.

        Returns:
            Mobject: An animatable version of the block that resets stroke color
                    when passed to scene.play(). The returned object supports
                    method chaining with other .animate transformations.

        Examples:
            # Reset stroke color after temporary highlighting
            self.play(block.set_block_stroke_color(YELLOW))
            self.wait(1)
            self.play(block.reset_block_stroke_color())

            # Chain reset with other transformations
            self.play(block.reset_block_stroke_color().scale(0.8))

            # Reset multiple blocks simultaneously
            self.play(
                block1.reset_block_stroke_color(),
                block2.reset_block_stroke_color(),
                block3.reset_block_stroke_color()
            )

            # Use in consensus visualization sequences
            self.play(
                block.set_block_stroke_color(RED),
                block.set_block_fill_color(BLUE)
            )
            self.play(block.reset_block_stroke_color())

        Implementation Details:
            Uses the proxy delegation pattern to forward the reset operation
            to the visual block's reset_block_stroke_color() method. The visual
            block stores creation-time values during initialization and uses
            those for the reset rather than current config values.

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
            visual_block.reset_block_stroke_color: Direct visual block implementation

        Notes:
            - Returns animatable mobject, not Animation object
            - Only affects stroke color, preserves fill color and other properties
            - Uses creation-time values, not current config values
            - Follows the proxy delegation pattern for clean API separation
            - Essential for proper consensus visualization cleanup
        """
        return self.visual_block.reset_block_stroke_color()

    def set_block_stroke_width(self, width: float) -> Mobject:
        """Returns animatable Mobject for block stroke width transformation."""
        return self.visual_block.set_block_stroke_width(width)

    def reset_block_stroke_width(self) -> Mobject:
        """Returns animatable Mobject to reset stroke width to creation value."""
        return self.visual_block.reset_block_stroke_width()

class VirtualKaspaBlock(KaspaLogicalBlock):
    """Virtual block for GHOSTDAG template calculation with visual representation."""

    def __init__(self, tips : List[KaspaLogicalBlock], v_config: _KaspaConfigInternal):

        # Calculate position: right of tallest parent, at genesis_y
        if not tips:
            # No parents (empty DAG) - use genesis position
            x_position = v_config.genesis_x
            y_position = v_config.genesis_y
        else:
            # Find rightmost parent by x-position
            rightmost_parent = max(tips, key=lambda p: p.visual_block.square.get_center()[0])
            parent_pos = rightmost_parent.visual_block.square.get_center()
            x_position = parent_pos[0] + v_config.horizontal_spacing
            y_position = v_config.genesis_y  # Always at genesis level

        # Initialize with calculated position
        super().__init__(
            name="__virtual__",
            parents=tips,
            position=(x_position, y_position),
            config=v_config
        )

        # Override visual block with "V" label (same position)
        parent_visuals = [p.visual_block for p in self.parents]
        self._visual = KaspaVisualBlock(
            label_text="V",
            position=(x_position, y_position),
            parents=parent_visuals,
            config=v_config
        )
        self._visual.logical_block = self

    def create_destroy_animation(self) -> list:
        """Fade to complete invisibility using Manim's FadeOut."""
        return [
            self.visual_block.square.animate.set_opacity(0),
            self.visual_block.background_rect.animate.set_opacity(0),
            self.visual_block.label.animate.set_opacity(0),
            *[line.animate.set_stroke(opacity=0) for line in self.visual_block.parent_lines]
        ]