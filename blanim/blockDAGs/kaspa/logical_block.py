# blanim\blanim\blockDAGs\kaspa\logical_block.py

from __future__ import annotations

__all__ = ["KaspaLogicalBlock", "VirtualKaspaBlock"]

import secrets
from dataclasses import dataclass, field

from manim import ParsableManimColor, AnimationGroup, Animation

from .visual_block import KaspaVisualBlock
from typing import Optional, List, Set, Dict, Union, Iterator

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

    def get_sorted_mergeset_blues(self) -> List['KaspaLogicalBlock']:
        """Get the ordered list of mergeset blocks that are blue."""
        if not self.selected_parent:
            return []

            # Get the sorted mergeset excluding selected parent
        mergeset = self.get_sorted_mergeset_without_sp()

        # Filter to only include blue blocks from local perspective
        blue_blocks = [
            block for block in mergeset
            if self.ghostdag.local_blue_pov.get(block, False)
        ]

        return blue_blocks

    def get_blue_blocks(self) -> Set['KaspaLogicalBlock']:
        """
        Get all blocks that are blue from this block's perspective. note: does not include self

        Returns:
            Set[KaspaLogicalBlock]: All blocks marked as blue in this block's
            ghostdag local_blue_pov dictionary.
        """
        return {block for block, is_blue in self.ghostdag.local_blue_pov.items() if is_blue}

    # TODO test and verify this
    def get_consensus_ordered_past(self) -> List['KaspaLogicalBlock']:
        """
        Get all blocks in the past cone ordered by GHOSTDAG consensus.

        Returns:
            List[KaspaLogicalBlock]: Ordered list starting from genesis,
            following the pattern: Gen -> sp -> ordered mergeset -> sp ->
            ordered mergeset -> ... -> self
        """

        def build_reverse_chain(block: 'KaspaLogicalBlock', result: List['KaspaLogicalBlock']) -> None:
            """Build the chain in reverse order (from self to genesis)."""
            # Add current block first
            result.append(block)

            if not block.selected_parent:
                # Genesis reached
                return

            # Add the mergeset (excluding selected parent) before the selected parent
            mergeset_without_sp = block.get_sorted_mergeset_without_sp()
            result.extend(mergeset_without_sp)

            # Recursively continue with selected parent
            build_reverse_chain(block.selected_parent, result)

        # Build in reverse order and then reverse
        reverse_chain = []
        build_reverse_chain(self, reverse_chain)
        reverse_chain.reverse()

        return reverse_chain

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
            current = to_visit.pop(0)
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

    def get_selected_parent_chain(self) -> List['KaspaLogicalBlock']:
        """Get ordered list of selected parents from self back to genesis."""
        selected_parent_chain_to_genesis = []
        current_block = self

        while current_block and current_block.selected_parent:
            selected_parent_chain_to_genesis.append(current_block.selected_parent)
            current_block = current_block.selected_parent

        return selected_parent_chain_to_genesis

    def get_all_selected_parents_pov(self) -> Dict['KaspaLogicalBlock', bool]:
        """Get the complete blue/red classification from all selected parents in the chain."""
        all_pov = {}

        # Get ordered list of selected parents
        sp_chain = self.get_selected_parent_chain()

        # Collect blue/red data from each selected parent
        for sp in sp_chain:
            all_pov.update(sp.ghostdag.local_blue_pov)

        return all_pov

    ########################################
    # Accessing Visual Block
    ########################################

    def get_center(self):
        return self.visual_block.get_center()

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

    @property
    def animate(self) -> BlockAnimationBuilder:
        """Return custom animation builder for multi-mobject chaining."""
        return BlockAnimationBuilder(self)

    ########################################
    # END Logical Block
    ########################################


class BlockAnimationBuilder(AnimationGroup):
    """Custom animation builder that handles multi-mobject animations.

    This builder enables chaining animations that target different mobjects
    (square, label, background_rect) while avoiding Manim's "last animation
    wins" limitation. Each mobject gets exactly one combined animation.

    How to Add a New Animation:
    -------------------------

    1. Identify the target mobject (square, label, or background_rect)
    2. Create a method that returns 'self' for chaining
    3. Use the _animations_by_mobject pattern to combine animations:

    def set_your_property(self, value) -> 'BlockAnimationBuilder':
        # Get the target mobject
        target = self.block.visual_block.your_mobject

        # Check if we already have an animation for this mobject
        if target not in self._animations_by_mobject:
            # Create new animate object if none exists
            self._animations_by_mobject[target] = target.animate

        # Chain the new property onto existing animation
        self._animations_by_mobject[target] = \
            self._animations_by_mobject[target].set_your_property(value)

        return self

    Examples:
    --------
    # Adding a new square animation (follows existing pattern)
    def set_square_opacity(self, opacity: float) -> 'BlockAnimationBuilder':
        target = self.block.visual_block.square
        if target not in self._animations_by_mobject:
            self._animations_by_mobject[target] = target.animate
        self._animations_by_mobject[target] = \
            self._animations_by_mobject[target].set_fill(opacity=opacity)
        return self

    # Adding a new label animation
    def set_label_font_size(self, size: int) -> 'BlockAnimationBuilder':
        target = self.block.visual_block.label
        if target not in self._animations_by_mobject:
            self._animations_by_mobject[target] = target.animate
        self._animations_by_mobject[target] = \
            self._animations_by_mobject[target].set_font_size(size)
        return self

    Key Points:
    ----------
    - Always check if target exists in _animations_by_mobject first
    - Use target.animate for the first animation on a mobject
    - Chain subsequent animations onto the existing animate object
    - Return 'self' to enable method chaining
    - The __iter__ method automatically handles combining animations for play()

    See Also:
    --------
    - set_fill_color: Example of square animation pattern
    - change_label: Example of label animation pattern
    - set_bg_rect_opacity: Example of background_rect animation pattern
    """

    def __init__(self, block: 'KaspaLogicalBlock'):
        super().__init__()
        self.block = block
        self._animations_by_mobject = {}  # Track animations by target

    def set_fill_color(self, color: ParsableManimColor) -> 'BlockAnimationBuilder':
        """Set square fill color."""
        if self.block.visual_block.square not in self._animations_by_mobject:
            self._animations_by_mobject[self.block.visual_block.square] = \
                self.block.visual_block.square.animate
        self._animations_by_mobject[self.block.visual_block.square] = \
            self._animations_by_mobject[self.block.visual_block.square].set_fill(color=color)
        return self

    def reset_fill_color(self) -> 'BlockAnimationBuilder':
        """Reset fill color to block creation fill color.
        NOTE: if setting and resetting color on the same animation chain(or within the same play call), only one will
        win, typically the last one called.
        """
        if self.block.visual_block.square not in self._animations_by_mobject:
            self._animations_by_mobject[self.block.visual_block.square] = \
                self.block.visual_block.square.animate
        self._animations_by_mobject[self.block.visual_block.square] = \
            self._animations_by_mobject[self.block.visual_block.square].set_fill(color=self.block.visual_block.creation_block_fill_color)
        return self

    def set_stroke_width(self, width: float) -> 'BlockAnimationBuilder':
        """Set stroke width."""
        if self.block.visual_block.square not in self._animations_by_mobject:
            self._animations_by_mobject[self.block.visual_block.square] = \
                self.block.visual_block.square.animate
        self._animations_by_mobject[self.block.visual_block.square] = \
            self._animations_by_mobject[self.block.visual_block.square].set_stroke(width=width)
        return self

    def reset_stroke_width(self) -> 'BlockAnimationBuilder':
        """Reset stroke width to block creation stroke width.
        NOTE: if setting and resetting stroke on the same animation chain(or within the same play call), only one will
        win, typically the last one called.
        """
        if self.block.visual_block.square not in self._animations_by_mobject:
            self._animations_by_mobject[self.block.visual_block.square] = \
                self.block.visual_block.square.animate
        self._animations_by_mobject[self.block.visual_block.square] = \
            self._animations_by_mobject[self.block.visual_block.square].set_stroke(width=self.block.visual_block.creation_block_stroke_width)
        return self

    def set_stroke_color(self, color: ParsableManimColor) -> 'BlockAnimationBuilder':
        """Set stroke color."""
        if self.block.visual_block.square not in self._animations_by_mobject:
            self._animations_by_mobject[self.block.visual_block.square] = \
                self.block.visual_block.square.animate
        self._animations_by_mobject[self.block.visual_block.square] = \
            self._animations_by_mobject[self.block.visual_block.square].set_stroke(color=color)
        return self

    def reset_stroke_color(self) -> 'BlockAnimationBuilder':
        """Reset stroke color to block creation stroke color.
        NOTE: if setting and resetting stroke on the same animation chain(or within the same play call), only one will
        win, typically the last one called.
        """
        if self.block.visual_block.square not in self._animations_by_mobject:
            self._animations_by_mobject[self.block.visual_block.square] = \
                self.block.visual_block.square.animate
        self._animations_by_mobject[self.block.visual_block.square] = \
            self._animations_by_mobject[self.block.visual_block.square].set_stroke(color=self.block.visual_block.creation_block_stroke_color)
        return self

    def set_label_text(self, text: Union[str, int]) -> 'BlockAnimationBuilder':
        """Set label text."""
        self._animations_by_mobject[self.block.visual_block.label] = \
            self.block.visual_block.change_label(text)
        return self

    def reset_label_text(self) -> 'BlockAnimationBuilder':
        """Reset label text to creation label text."""
        self._animations_by_mobject[self.block.visual_block.label] = \
            self.block.visual_block.change_label(self.block.visual_block.creation_block_label)
        return self

    def set_label_color(self, color: ParsableManimColor) -> 'BlockAnimationBuilder':
        """Set label color."""
        if self.block.visual_block.label not in self._animations_by_mobject:
            self._animations_by_mobject[self.block.visual_block.label] = \
                self.block.visual_block.label.animate
        self._animations_by_mobject[self.block.visual_block.label] = \
            self._animations_by_mobject[self.block.visual_block.label].set_color(color)
        return self

    # TODO fully test this
    def reset_block(self) -> 'BlockAnimationBuilder':
        """Reset all block properties to creation-time values."""
        # Reset square properties individually
        if self.block.visual_block.square not in self._animations_by_mobject:
            self._animations_by_mobject[self.block.visual_block.square] = \
                self.block.visual_block.square.animate

        # Chain individual property resets
        self._animations_by_mobject[self.block.visual_block.square] = \
            self._animations_by_mobject[self.block.visual_block.square] \
                .set_fill(color=self.block.visual_block.creation_block_fill_color) \
                .set_stroke(color=self.block.visual_block.creation_block_stroke_color) \
                .set_stroke(width=self.block.visual_block.creation_block_stroke_width)

        # Reset label text
        self._animations_by_mobject[self.block.visual_block.label] = \
            self.block.visual_block.change_label(self.block.visual_block.creation_block_label)

        return self

    def set_bg_rect_opacity(self, opacity: float) -> 'BlockAnimationBuilder':
        """Set background rectangle opacity."""
        if self.block.visual_block.background_rect not in self._animations_by_mobject:
            self._animations_by_mobject[self.block.visual_block.background_rect] = \
                self.block.visual_block.background_rect.animate
        self._animations_by_mobject[self.block.visual_block.background_rect] = \
            self._animations_by_mobject[self.block.visual_block.background_rect].set_fill(opacity=opacity)
        return self

    def __iter__(self) -> Iterator[Animation]:
        """Return all animations, combined by mobject."""
        return iter(self._animations_by_mobject.values())

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
            name="V",
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