# blanim\blanim\blockDAGs\kaspa\logical_block.py

from __future__ import annotations

__all__ = ["KaspaLogicalBlock", "VirtualKaspaBlock"]

import secrets
from dataclasses import dataclass, field

from manim import ParsableManimColor, Mobject

from .visual_block import KaspaVisualBlock
from typing import Optional, List, Set, Any, Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import _KaspaConfigInternal

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
            if self.can_be_blue_local(candidate, local_blue_status, k):
                local_blue_status[candidate] = True
                blue_in_mergeset += 1
            else:
                local_blue_status[candidate] = False

        # Store the complete local POV (removed is_blue assignment)
        self.ghostdag.local_blue_pov = local_blue_status.copy()
        self.ghostdag.blue_score = selected_parent_blue_score + 1 + blue_in_mergeset

    def can_be_blue_local(self,
                           candidate: 'KaspaLogicalBlock',
                           local_blue_status: Dict['KaspaLogicalBlock', bool],
                           k: int) -> bool:
        """Check if candidate can be blue using local perspective."""

        # Get blue blocks from local perspective
        blue_blocks = {block for block, is_blue in local_blue_status.items() if is_blue}

        # Check 1: <= k blue blocks in candidate's anticone
        candidate_anticone = set(candidate.get_anticone_in_past(self))
        blue_in_anticone = len(candidate_anticone & blue_blocks)
        if blue_in_anticone > k:
            return False

        # Check 2: Adding candidate doesn't cause existing blues to have > k blues in anticone
        for blue_block in blue_blocks:
            blue_anticone = set(blue_block.get_anticone_in_past(self))
            if candidate in blue_anticone:
                blue_in_anticone = len(blue_anticone & blue_blocks) + 1
                if blue_in_anticone > k:
                    return False

        return True

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
    # Collecting Past/Future/Anticone
    ########################################

    def get_past_cone(self) -> List[KaspaLogicalBlock]:
        """
        Get all ancestors of this block via depth-first search.

        This method traverses the DAG structure by following parent relationships
        recursively to collect all blocks in the past cone (all ancestors). The
        past cone represents the complete history and context that this block
        builds upon.

        Returns:
            List[KaspaLogicalBlock]: All ancestor blocks reachable by following
            parent links. The order is not guaranteed as a set is used internally
            to avoid duplicates and handle DAG merge points correctly.

        Examples:
            # Get all blocks that influenced this block
            ancestors = block.get_past_cone()

            # Check if genesis is in the past cone
            genesis_in_past = dag.genesis in block.get_past_cone()

            # Count total ancestors
            history_depth = len(block.get_past_cone())

        Implementation Details:
            Uses an iterative depth-first search with a stack to avoid Python's
            recursion depth limits. A set tracks visited blocks to handle DAG
            structures where multiple paths may lead to the same ancestor
            (merge points). The algorithm starts from self and explores all
            parent relationships recursively.

        Performance Notes:
            - Time complexity: O(P) where P is the number of blocks in past cone
            - Space complexity: O(P) for the visited set and stack
            - More efficient than recursive DFS for deep DAG structures
            - Handles merge points correctly without duplicate visits

            # Efficient for typical Kaspa DAG structures
            past = block.get_past_cone()  # Usually completes quickly

        See Also:
            get_future_cone: Get all descendants instead of ancestors
            KaspaDAG.get_anticone: Calculate blocks neither in past nor future
            GhostDAGData: Uses past cone for consensus calculations

        Notes:
            - Returns list, but order is not guaranteed (set-based internally)
            - Excludes the block itself from the returned list
            - Essential for GHOSTDAG consensus algorithm calculations
            - Used internally by blue score computation and mergeset creation
        """
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
        """
        Get all descendants of this block via depth-first search.

        This method traverses the DAG structure by following child relationships
        recursively to collect all blocks in the future cone (all descendants).
        The future cone represents all blocks that directly or indirectly build
        upon this block.

        Returns:
            List[KaspaLogicalBlock]: All descendant blocks reachable by following
            child links. The order is not guaranteed as a set is used internally
            to avoid duplicates and handle DAG fork points correctly.

        Examples:
            # Get all blocks that build upon this block
            descendants = block.get_future_cone()

            # Check if a specific block is in the future
            is_future = target_block in block.get_future_cone()

            # Find tips that descend from this block
            tips = [b for b in block.get_future_cone() if not b.children]

        Implementation Details:
            Uses an iterative depth-first search with a stack to avoid Python's
            recursion depth limits. A set tracks visited blocks to handle DAG
            structures where multiple paths may lead to the same descendant
            (convergence points). The algorithm starts from self and explores
            all child relationships recursively.

        Performance Notes:
            - Time complexity: O(F) where F is the number of blocks in future cone
            - Space complexity: O(F) for the visited set and stack
            - More efficient than recursive DFS for deep DAG structures
            - Handles convergence points correctly without duplicate visits

            # Efficient for typical Kaspa DAG structures
            future = block.get_future_cone()  # Usually completes quickly

        See Also:
            get_past_cone: Get all ancestors instead of descendants
            KaspaDAG.get_anticone: Calculate blocks neither in past nor future
            KaspaDAG.get_current_tips: Find blocks without children

        Notes:
            - Returns list, but order is not guaranteed (set-based internally)
            - Excludes the block itself from the returned list
            - Essential for understanding block influence and reachability
            - Used by relationship highlighting and DAG analysis functions
        """
        future = set()
        to_visit = [self]

        while to_visit:
            current = to_visit.pop()
            for child in current.children:
                if child not in future:
                    future.add(child)
                    to_visit.append(child)

        return list(future)

    def get_anticone_in_past(self, ref_block: KaspaLogicalBlock) -> List[KaspaLogicalBlock]:
        """
        Get anticone blocks confined to the past cone of a reference block.

        This method calculates anticone within the limited context of ref_block's
        past cone, providing efficient localized analysis without requiring full
        DAG traversal. The anticone represents blocks that are neither ancestors
        nor descendants of this block within the specified boundary.

        Args:
            ref_block: Reference block whose past cone defines the search boundary.
                      The method calculates anticone within ref_block's past cone
                      plus the reference block itself.

        Returns:
            List[KaspaLogicalBlock]: All blocks in ref_block's past cone that are
            in the anticone of this block. The order is not guaranteed as a set
            is used internally to avoid duplicates and handle DAG structures.

        Examples:
            # Get anticone within a specific context
            context_anticone = block.get_anticone_in_past(reference_block)

            # Check if a specific block is in the confined anticone
            is_in_anticone = target_block in block.get_anticone_in_past(ref_block)

            # Count blocks in confined anticone
            anticone_size = len(block.get_anticone_in_past(reference_block))

        Implementation Details:
            Uses set operations to confine the search space to ref_block's past
            cone, then applies the standard anticone calculation: search_space
            - past - future - self. The method validates that self is within the
            reference block's past cone to ensure meaningful results.

        Performance Notes:
            - Time complexity: O(P + F) where P is past cone size and F is future cone size
            - Space complexity: O(P + F) for the intermediate sets
            - More efficient than full DAG anticone for localized analysis
            - Validation check ensures proper usage and prevents incorrect results

            # Efficient for localized consensus analysis
            confined_anticone = block.get_anticone_in_past(context_block)

        See Also:
            get_anticone: Get full DAG anticone without confinement
            get_past_cone: Get all ancestors of this block
            get_future_cone: Get all descendants of this block

        Notes:
            - Returns list, but order is not guaranteed (set-based internally)
            - Excludes the block itself from the returned list
            - Validates that self is in ref_block's past cone (raises ValueError otherwise)
            - Essential for GHOSTDAG consensus k-cluster validation
            - Used internally by blue candidate evaluation algorithms
        """
        # Validate that self is in ref_block's past cone
        ref_past = set(ref_block.get_past_cone())
        if self not in ref_past and self != ref_block:
            raise ValueError("Self must be in reference block's past cone")

            # Define search space as ref_block's past plus ref_block
        search_space = ref_past | {ref_block}

        # Calculate anticone within this confined space
        self_past = set(self.get_past_cone())
        self_future = set(self.get_future_cone())

        return list(search_space - self_past - self_future - {self})

    def get_anticone(self) -> List[KaspaLogicalBlock]:
        """
        Get all blocks that are neither ancestors nor descendants of this block.

        This method autonomously discovers the full DAG by traversing to genesis
        and then collecting all blocks in its future cone, providing complete
        anticone calculation without requiring external DAG context. The anticone
        represents blocks that have no ordering relationship with this block.

        Returns:
            List[KaspaLogicalBlock]: All blocks in the anticone of this block.
            The order is not guaranteed as a set is used internally to avoid
            duplicates and handle DAG structures correctly.

        Examples:
            # Get all concurrent blocks (neither ancestors nor descendants)
            concurrent_blocks = block.get_anticone()

            # Check if two blocks are concurrent
            block1_anticone = block1.get_anticone()
            is_concurrent = block2 in block1_anticone

            # Count total concurrent blocks in DAG
            concurrency_level = len(block.get_anticone())

        Implementation Details:
            Traverses the selected parent chain to find genesis (block with no
            parents), then collects the complete DAG from genesis's future cone.
            Calculates anticone using the standard formula: total_dag - past
            - future - self. This approach leverages the property that all Kaspa
            DAG blocks are descendants of a single genesis block.

        Performance Notes:
            - Time complexity: O(N) where N is total blocks in DAG
            - Space complexity: O(N) for the total DAG set
            - Suitable for educational/visualization "toy model" DAGs
            - More efficient than external DAG context for self-contained operations

            # Efficient for typical educational DAG sizes
            full_anticone = block.get_anticone()

        See Also:
            get_anticone_in_past: Get anticone confined to reference block's past
            get_past_cone: Get all ancestors of this block
            get_future_cone: Get all descendants of this block

        Notes:
            - Returns list, but order is not guaranteed (set-based internally)
            - Excludes the block itself from the returned list
            - Follows selected parent chain to find genesis
            - Sufficient for educational/visualization "toy model" DAGs
            - Essential for understanding block concurrency and DAG structure
            - Used by relationship highlighting and visualization systems
        """
        # Find genesis by traversing past until no parents found
        current = self
        while current.parents:
            current = current.parents[0]  # Follow selected parent chain

        genesis = current

        # Get total DAG by collecting genesis's future cone
        total_dag = set(genesis.get_future_cone())
        total_dag.add(genesis)  # Include genesis itself

        # Calculate anticone
        past = set(self.get_past_cone())
        future = set(self.get_future_cone())

        return list(total_dag - past - future - {self})

    ########################################
    # Accessing Visual Block
    ########################################

    @property
    def visual_block(self) -> KaspaVisualBlock:
        """
        Direct access to the visual block for internal system operations.

        **INTERNAL SYSTEMS ONLY**: This property provides full access to the underlying
        KaspaVisualBlock object for complex operations that cannot be handled by
        the wrapped visual methods.

        **END USERS**: Use the explicit wrapper methods instead:
        - block.set_block_fill_color(color)  # ✅ Preferred
        - block.visual_block.set_fill_color(color)  # ❌ Avoid

        **When to use this property**:
        - BlockManager positioning calculations (needs square.get_center())
        - Complex animation creation (create_with_lines, create_movement_animation)
        - System-level operations requiring full visual block access

        **Examples**:
        # Internal: BlockManager positioning
        rightmost = max(blocks, key=lambda p: p.visual_block.square.get_center()[0])

        # Internal: Complex animations
        animations.append(block.visual_block.create_with_lines())

        Returns:
            KaspaVisualBlock: The underlying visual block object
        """
        return self._visual

    def __getattr__(self, attr: str) -> Any:
        # TODO: Remove proxy delegation pattern for better type safety
        #
        # CURRENT ISSUE:
        # The proxy pattern silently delegates all unknown attributes to self._visual,
        # which hides bugs like method name mismatches (e.g., _can_be_blue_local vs can_be_blue_local).
        # This makes debugging difficult and prevents IDE from catching typos.
        #
        # REFACTORED APPROACH:
        # Since refactoring, we now explicitly wrap visual methods (set_block_fill_color,
        # reset_block_stroke_width, etc.) in KaspaLogicalBlock with proper type hints
        # and documentation. These wrappers provide a clean, documented API.
        #
        # BENEFITS OF REMOVING PROXY:
        # 1. Type Safety: IDE catches typos like block.set_block_flll_color immediately
        # 2. Clear API: Only explicitly wrapped methods are available
        # 3. Better Debugging: No more hidden delegation issues
        #
        # MIGRATION STEPS:
        # 1. Replace this method with: raise AttributeError(f"'{type(self).__name__}' object has no attribute '{attr}'")
        # 2. Audit codebase for any visual method calls not explicitly wrapped
        # 3. Apply same change to BitcoinLogicalBlock.__getattr__ for consistency
        #
        # The proxy pattern was originally designed for convenience (see blanim.py:83-91)
        # but explicit wrappers provide better developer experience and error catching.
        #
        if attr == '_visual':
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '_visual'")
        print(f"DEBUG: __getattr__ called for attribute: {attr}")
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
        """
        Returns an animatable Mobject for block stroke width transformation.

        This method delegates to the visual block while maintaining type hints
        and providing a clean public API through the proxy pattern. The stroke
        width adjustment affects only the border thickness of the block.

        Parameters:
            width: float
                  The stroke width to apply to the block's border.
                  Typical values range from 1 (thin) to 10 (very thick).
                  The width is applied while preserving stroke color and other
                  visual properties.

        Returns:
            Mobject: An animatable version of the block that changes stroke width
                    when passed to scene.play(). The returned object supports
                    method chaining with other .animate transformations.

        Examples:
            # Single stroke width change
            self.play(block.set_block_stroke_width(6))

            # Chain with color change
            self.play(block.set_block_stroke_width(8).set_block_stroke_color(YELLOW))

            # Chain with position and scale
            self.play(
                block.set_block_stroke_width(10)
                    .shift(UP)
                    .scale(1.2)
            )

            # Use in AnimationGroup with other animations
            self.play(
                block.set_block_stroke_width(12),
                other_block.animate.shift(RIGHT)
            )

            # Emphasize block during consensus evaluation
            self.play(block.set_block_stroke_width(15))
            self.wait(0.5)
            self.play(block.reset_block_stroke_width())

        Implementation Details:
            Uses the proxy delegation pattern to forward the stroke width
            operation to the visual block's set_block_stroke_width() method.
            The visual block handles the actual Manim .animate system
            implementation while the logical block provides the public API.

        Performance Notes:
            - Method chaining creates a single optimized animation
            - Separate play() calls create multiple sequential animations
            - Stroke width changes are very fast and efficient

            # Efficient: Single combined animation
            self.play(block.set_block_stroke_width(8).scale(2))

            # Less efficient: Multiple separate animations
            self.play(block.set_block_stroke_width(8))
            self.play(block.scale(2))

        See Also:
            reset_block_stroke_width: Reset stroke width to creation value
            set_block_stroke_color: Change stroke color instead of width
            visual_block.set_block_stroke_width: Direct visual block implementation

        Notes:
            - Returns animatable mobject, not Animation object
            - Preserves fill color, stroke color, and other properties
            - Only modifies the stroke width of the block's square
            - Follows Manim's .animate convention for chaining
            - Uses the proxy delegation pattern for clean API separation
        """
        return self.visual_block.set_block_stroke_width(width)

    def reset_block_stroke_width(self) -> Mobject:
        """
        Returns an animatable Mobject to reset stroke width to creation-time values.

        This method delegates to the visual block while maintaining type hints
        and providing a clean public API through the proxy pattern. The reset
        restores the block's stroke width to what it was when initially created,
        preserving the user's original design intent.

        Returns:
            Mobject: An animatable version of the block that resets stroke width
                    when passed to scene.play(). The returned object supports
                    method chaining with other .animate transformations.

        Examples:
            # Reset stroke width after emphasis
            self.play(block.set_block_stroke_width(12))
            self.wait(1)
            self.play(block.reset_block_stroke_width())

            # Chain reset with other transformations
            self.play(block.reset_block_stroke_width().scale(0.8))

            # Reset multiple blocks after consensus evaluation
            self.play(
                evaluated_block.reset_block_stroke_width(),
                candidate_block.reset_block_stroke_width(),
                selected_block.reset_block_stroke_width()
            )

            # Use in consensus visualization sequences
            self.play(
                block.set_block_stroke_width(10),
                block.set_block_stroke_color(RED)
            )
            self.play(block.reset_block_stroke_width())

            # Reset while maintaining other changes
            self.play(block.reset_block_stroke_width().set_block_fill_color(BLUE))

        Implementation Details:
            Uses the proxy delegation pattern to forward the reset operation
            to the visual block's reset_block_stroke_width() method. The visual
            block stores creation-time values during initialization and uses
            those for the reset rather than current config values.

        Performance Notes:
            - Reset operations are single-property animations and are very fast
            - Can be chained with other animations for combined effects
            - Essential for clean consensus visualization state management

            # Efficient: Combined reset and transform
            self.play(block.reset_block_stroke_width().shift(DOWN))

            # Less efficient: Separate operations
            self.play(block.reset_block_stroke_width())
            self.play(block.shift(DOWN))

        See Also:
            set_block_stroke_width: Change stroke width to any specified value
            reset_block_stroke_color: Reset stroke color to creation values
            reset_block_fill_color: Reset fill color to creation values
            visual_block.reset_block_stroke_width: Direct visual block implementation

        Notes:
            - Returns animatable mobject, not Animation object
            - Only affects stroke width, preserves stroke color, fill color and other properties
            - Uses creation-time values, not current config values
            - Follows the proxy delegation pattern for clean API separation
            - Essential for proper consensus visualization cleanup
        """
        return self.visual_block.reset_block_stroke_width()

    ########################################
    # END Logical Block
    ########################################

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

    def create_destroy_animation(self) -> List:
        """Fade to complete invisibility using Manim's FadeOut."""
        return [
            self.visual_block.square.animate.set_opacity(0),
            self.visual_block.background_rect.animate.set_opacity(0),
            self.visual_block.label.animate.set_opacity(0),
            *[line.animate.set_stroke(opacity=0) for line in self.visual_block.parent_lines]
        ]