# blanim/examples/kaspa_examples.py
import hashlib

from blanim import *

####################
# Some examples NOT using anything but hud_2d_scene
####################

class ZChainedBecomeExample(Scene):
    def construct(self):
        # Create initial text
        initial_text = Text("init", font_size=48, color=WHITE)
        self.add(initial_text)

        # Create target text and explicitly set properties
        target_text = Text("Hello Manim! Long String!", font_size=48, color=WHITE)
        target_text.set_color(RED)  # Set color
        target_text.set_fill(opacity=1)  # Set fill opacity explicitly

        # Create target text and explicitly set properties
        target_text2 = Text("test", font_size=48, color=WHITE)
        target_text2.set_color(WHITE)  # Set color
        target_text2.set_fill(opacity=1)  # Set fill opacity explicitly

        # Use become() with target that has properly set properties
        self.play(initial_text.animate.become(target_text))
        self.play(initial_text.animate.set_opacity(0.2))
        self.play(initial_text.animate.become(target_text2))
        self.play(initial_text.animate.set_opacity(0.2))
        self.play(initial_text.animate.become(target_text))
        self.play(initial_text.animate.set_opacity(0.2))
        self.play(initial_text.animate.become(target_text2))
        self.play(initial_text.animate.set_opacity(0.2))
        self.play(initial_text.animate.become(target_text))
        self.play(initial_text.animate.set_opacity(0.2))
        self.wait(1)


class ZChainedBecomeSquareExample(Scene):
    def construct(self):
        # Create initial square
        initial_square = Square(fill_color=RED, fill_opacity=1.0, side_length=2)
        self.add(initial_square)

        # Create target squares with different properties
        target_square = Square(fill_color=BLUE, fill_opacity=1.0, side_length=3)
        target_square2 = Square(fill_color=GREEN, fill_opacity=1.0, side_length=2)

        # Same sequence as your text example
        self.play(initial_square.animate.become(target_square))
        self.play(initial_square.animate.set_opacity(opacity=0.2))
        self.play(initial_square.animate.become(target_square2))
        self.play(initial_square.animate.set_opacity(opacity=0.2))
        self.play(initial_square.animate.become(target_square))
        self.play(initial_square.animate.set_opacity(opacity=0.2))
        self.play(initial_square.animate.become(target_square2))
        self.play(initial_square.animate.set_opacity(opacity=0.2))
        self.play(initial_square.animate.become(target_square))
        self.play(initial_square.animate.set_opacity(opacity=0.2))
        self.wait(1)

class BlockComparisonScene(HUD2DScene):
    def __init__(self):
        super().__init__()
        self.kaspa_header_fields = None
        self.btc_header_fields = None
        self.kaspa_header_rect_original = None
        self.btc_header_rect_original = None
        self.kaspa_body_rect_original = None
        self.btc_body_rect_original = None
        self.kaspa_txs = None
        self.btc_txs = None
        self.kaspa_sections = None
        self.bitcoin_sections = None
        self.kaspa_square = None
        self.bitcoin_square = None
        self.btc_body_original_scale = None
        self.kaspa_body_original_pos = None
        self.btc_body_original_pos = None

    def construct(self):
        # Add narration and caption
        self.narrate(r"Bitcoin vs Kaspa", run_time=1)

        # Create two labeled squares with adjusted spacing and size
        bitcoin_square = self.create_labeled_square("Bitcoin Block", LEFT * 3.75)
        kaspa_square = self.create_labeled_square("Kaspa Block", RIGHT * 3.75)

        self.caption(r"Let us compare Bitcoin and Kaspa Blocks.", run_time=1)

        # Animate squares first (index [0] is the square)
        self.play(
            Create(bitcoin_square[0]),
            Create(kaspa_square[0]),
            run_time=1
        )

        # Then animate labels (index [1] is the label)
        self.play(
            Create(bitcoin_square[1]),
            Create(kaspa_square[1]),
            run_time=1
        )

        # Create header and body rectangles for both blocks
        bitcoin_sections = self.create_block_sections(bitcoin_square[0])
        kaspa_sections = self.create_block_sections(kaspa_square[0])

        # Animate header RECTANGLES first (index [0][0] is header rect)
        self.play(
            Create(bitcoin_sections[0][0]),  # Bitcoin header rectangle
            Create(kaspa_sections[0][0]),  # Kaspa header rectangle
            run_time=1
        )

        # Then animate header LABELS (index [0][1] is header label)
        self.play(
            Create(bitcoin_sections[0][1]),  # Bitcoin header label
            Create(kaspa_sections[0][1]),  # Kaspa header label
            run_time=1
        )

        # Animate body RECTANGLES (index [1][0] is body rect)
        self.play(
            Create(bitcoin_sections[1][0]),  # Bitcoin body rectangle
            Create(kaspa_sections[1][0]),  # Kaspa body rectangle
            run_time=1
        )

        # Then animate body LABELS (index [1][1] is body label)
        self.play(
            Create(bitcoin_sections[1][1]),  # Bitcoin body label
            Create(kaspa_sections[1][1]),  # Kaspa body label
            run_time=1
        )

        self.wait(3)

        # Store references for zoom operations
        self.bitcoin_square = bitcoin_square
        self.kaspa_square = kaspa_square
        self.bitcoin_sections = bitcoin_sections
        self.kaspa_sections = kaspa_sections

        self.caption(r"First we examine the body.", run_time=1)

        # Perform zoom sequence
        self.zoom_to_bodies()
        self.caption(r"Here we can see the body contains transactions...", run_time=1)

        self.wait(2)

        self.caption(r"the first transaction is always a coinbase transaction...", run_time=1)

        self.wait(2)

        self.caption(r"this is where block rewards are paid...", run_time=1)

        self.wait(2)

        self.caption(r"every other transaction is a user transaction...", run_time=1)

        self.wait(2)
        self.clear_caption()

        self.zoom_out_from_bodies()

        self.caption(r"Next we examine the headers.", run_time=1)

        # Now zoom to headers
        self.zoom_to_headers()
        self.wait(2)
        self.caption(r"The header contains the version...", run_time=1)
        self.wait(2)
        self.caption(r"then the hash of the previous block/s...", run_time=1)
        self.wait(2)
        self.caption(r"this blocks 'parent' or 'parents'...", run_time=1)
        self.wait(2)
        self.caption(r"next is the merkle root of the transactions in this block...", run_time=1)
        self.wait(2)
        self.caption(r"timestamp is another shared field...", run_time=1)
        self.wait(2)
        self.caption(r"followed by target difficulty bits...", run_time=1)
        self.wait(2)
        self.caption(r"and a nonce to reproduce a valid PoW hash...", run_time=1)
        self.wait(2)
        self.clear_caption()
        self.zoom_out_from_headers()
        self.wait(3)

    @staticmethod
    def create_labeled_square(label_text, position):
        """Create a white rounded square with a label"""
        from manim import Square, Text, VGroup, WHITE, UP

        # Create square with white stroke and rounded corners
        square = Square(
            side_length=4.75,
            stroke_color=WHITE,
            stroke_width=3,
            fill_opacity=0
        )
        square.round_corners(radius=0.3)

        # Create label
        label = Text(label_text, font_size=28, color=WHITE)
        label.next_to(square, UP, buff=0.3)

        # Group square and label together
        group = VGroup(square, label)
        group.move_to(position)

        return group

    @staticmethod
    def create_block_sections(parent_square):
        """Create header and body rectangles inside a square with spacing"""
        from manim import Rectangle, Text, VGroup, WHITE, UP, DOWN

        # Get parent square dimensions and position
        square_width = parent_square.width * 0.85
        square_height = parent_square.height * 0.85
        square_center = parent_square.get_center()

        # Add buffer between sections
        section_buff = 0.15  # Space between header and body

        # Calculate section heights (header is 1/3, body is 2/3)
        # Subtract half the buffer from each section
        header_height = (square_height * 0.33) - (section_buff / 2)
        body_height = (square_height * 0.67) - (section_buff / 2)

        # Create header rectangle at top
        header_rect = Rectangle(
            width=square_width,
            height=header_height,
            stroke_color=WHITE,
            stroke_width=2,
            fill_opacity=0
        )
        header_rect.round_corners(radius=0.2)

        # Position header at top - ADD buffer to push it up
        header_y_offset = (square_height - header_height) / 2 + (section_buff / 2)
        header_rect.move_to(square_center + UP * header_y_offset)

        # Create header label
        header_label = Text("Header", font_size=20, color=WHITE)
        header_label.move_to(header_rect.get_center())

        # Group header rect and label
        header_group = VGroup(header_rect, header_label)

        # Create body rectangle at bottom
        body_rect = Rectangle(
            width=square_width,
            height=body_height,
            stroke_color=WHITE,
            stroke_width=2,
            fill_opacity=0
        )
        body_rect.round_corners(radius=0.2)

        # Position body at bottom - ADD buffer to push it down
        body_y_offset = (square_height - body_height) / 2 + (section_buff / 2)
        body_rect.move_to(square_center + DOWN * body_y_offset)

        # Create body label
        body_label = Text("Body", font_size=20, color=WHITE)
        body_label.move_to(body_rect.get_center())

        # Group body rect and label
        body_group = VGroup(body_rect, body_label)

        return VGroup(header_group, body_group)

    def zoom_to_bodies(self):
        """Zoom into body sections by transforming body rectangles to block size"""

        # Get body sections
        btc_body = self.bitcoin_sections[1]  # VGroup(body_rect, body_label)
        kaspa_body = self.kaspa_sections[1]

        # Get just the body rectangles (index [0] within each body section)
        btc_body_rect = btc_body[0]
        kaspa_body_rect = kaspa_body[0]

        # Store original states for zoom out
        self.btc_body_rect_original = btc_body_rect.copy()
        self.kaspa_body_rect_original = kaspa_body_rect.copy()

        # Fade out everything except body sections
        fade_targets = [
            self.bitcoin_square[0],  # Bitcoin outer square box
            self.bitcoin_square[1],  # Bitcoin label
            self.kaspa_square[0],  # Kaspa outer square box
            self.kaspa_square[1],  # Kaspa label
            self.bitcoin_sections[0],  # Bitcoin header
            self.kaspa_sections[0],  # Kaspa header
            btc_body[1],  # Body label (fade this too)
            kaspa_body[1],  # Body label (fade this too)
        ]

        self.play(
            *[mob.animate.fade(0.9) for mob in fade_targets],
            run_time=1
        )

        # Create target rectangles with block-like dimensions
        # Make them similar size to original blocks (4.75 side length)
        target_width = 4.5
        target_height = 5.5

        btc_target_rect = Rectangle(
            width=target_width,
            height=target_height,
            stroke_color=WHITE,
            stroke_width=2,
            fill_opacity=0
        )
        btc_target_rect.round_corners(radius=0.2)
        btc_target_rect.move_to(LEFT * 3.75)

        kaspa_target_rect = Rectangle(
            width=target_width,
            height=target_height,
            stroke_color=WHITE,
            stroke_width=2,
            fill_opacity=0
        )
        kaspa_target_rect.round_corners(radius=0.2)
        kaspa_target_rect.move_to(RIGHT * 3.75)

        # Transform body rectangles to target size/shape
        self.play(
            Transform(btc_body_rect, btc_target_rect),
            Transform(kaspa_body_rect, kaspa_target_rect),
            run_time=2
        )

        # Create transactions one by one
        self.btc_txs = VGroup()
        self.kaspa_txs = VGroup()

        # Calculate how many transactions fit in the body
        body_height = btc_body_rect.height
        tx_font_size = 18
        tx_spacing = 0.35  # Reduced spacing to fit more

        # Estimate number of transactions that fit (accounting for text height)
        num_txs = int((body_height - 1.0) / tx_spacing)  # Leave margin at top/bottom

        tx_start_y = btc_body_rect.get_top()[1] - 0.5

        for i in range(num_txs):
            btc_tx = Text(f"tx{i}", font_size=tx_font_size, color=WHITE)
            btc_tx.move_to(
                btc_body_rect.get_center() + UP * (tx_start_y - i * tx_spacing - btc_body_rect.get_center()[1])
            )
            btc_tx.shift(LEFT * 1.5)

            kaspa_tx = Text(f"tx{i}", font_size=tx_font_size, color=WHITE)
            kaspa_tx.move_to(
                kaspa_body_rect.get_center() + UP * (tx_start_y - i * tx_spacing - kaspa_body_rect.get_center()[1])
            )
            kaspa_tx.shift(LEFT * 1.5)

            if i == 0:
                btc_coinbase = Text("coinbase", font_size=16, color=YELLOW)
                btc_coinbase.next_to(btc_tx, RIGHT, buff=0.3)

                kaspa_coinbase = Text("coinbase", font_size=16, color=YELLOW)
                kaspa_coinbase.next_to(kaspa_tx, RIGHT, buff=0.3)

                self.play(
                    Create(btc_tx),
                    Create(kaspa_tx),
                    Create(btc_coinbase),
                    Create(kaspa_coinbase),
                    run_time=0.8
                )

                self.btc_txs.add(btc_tx, btc_coinbase)
                self.kaspa_txs.add(kaspa_tx, kaspa_coinbase)
            else:
                self.play(
                    Create(btc_tx),
                    Create(kaspa_tx),
                    run_time=0.4  # Faster for subsequent transactions
                )

                self.btc_txs.add(btc_tx)
                self.kaspa_txs.add(kaspa_tx)

    def zoom_out_from_bodies(self):
        """Zoom out from bodies back to full block view"""

        # Fade out transactions
        self.play(
            FadeOut(self.btc_txs),
            FadeOut(self.kaspa_txs),
            run_time=1
        )

        # Get body rectangles
        btc_body = self.bitcoin_sections[1]
        kaspa_body = self.kaspa_sections[1]
        btc_body_rect = btc_body[0]
        kaspa_body_rect = kaspa_body[0]

        # Transform bodies back to original size and position
        self.play(
            Transform(btc_body_rect, self.btc_body_rect_original),
            Transform(kaspa_body_rect, self.kaspa_body_rect_original),
            run_time=2
        )

        # Separate rectangles (stroke-only) from text labels (fill-based)
        rect_targets = [
            self.bitcoin_square[0],  # Bitcoin outer square box
            self.kaspa_square[0],  # Kaspa outer square box
            self.bitcoin_sections[0][0],  # Bitcoin header rectangle
            self.kaspa_sections[0][0],  # Kaspa header rectangle
            btc_body[0],  # Bitcoin body rectangle
            kaspa_body[0],  # Kaspa body rectangle
        ]

        text_targets = [
            self.bitcoin_square[1],  # Bitcoin block label
            self.kaspa_square[1],  # Kaspa block label
            self.bitcoin_sections[0][1],  # Bitcoin header label
            self.kaspa_sections[0][1],  # Kaspa header label
            btc_body[1],  # Bitcoin body label
            kaspa_body[1],  # Kaspa body label
        ]

        # Restore stroke opacity for rectangles and fill opacity for text
        self.play(
            *[mob.animate.set_stroke(opacity=1.0) for mob in rect_targets],
            *[mob.animate.set_fill(opacity=1.0) for mob in text_targets],
            run_time=1
        )

        self.wait(3)

    def zoom_to_headers(self):
        """Zoom into header sections by transforming header rectangles to block size"""

        # Get header sections
        btc_header = self.bitcoin_sections[0]
        kaspa_header = self.kaspa_sections[0]

        # Get just the header rectangles
        btc_header_rect = btc_header[0]
        kaspa_header_rect = kaspa_header[0]

        # Store original states for zoom out
        self.btc_header_rect_original = btc_header_rect.copy()
        self.kaspa_header_rect_original = kaspa_header_rect.copy()

        # Fade out everything except header sections
        fade_targets = [
            self.bitcoin_square[0],
            self.bitcoin_square[1],
            self.kaspa_square[0],
            self.kaspa_square[1],
            self.bitcoin_sections[1],  # Bitcoin body
            self.kaspa_sections[1],  # Kaspa body
            btc_header[1],  # Header label
            kaspa_header[1],  # Header label
        ]

        self.play(
            *[mob.animate.fade(0.9) for mob in fade_targets],
            run_time=1
        )

        # Create target rectangles with specific dimensions
        target_width = 6.0
        target_height = 5.5

        btc_target_rect = Rectangle(
            width=target_width,
            height=target_height,
            stroke_color=WHITE,
            stroke_width=2,
            fill_opacity=0
        )
        btc_target_rect.round_corners(radius=0.2)
        btc_target_rect.move_to(LEFT * 3.75)

        kaspa_target_rect = Rectangle(
            width=target_width,
            height=target_height,
            stroke_color=WHITE,
            stroke_width=2,
            fill_opacity=0
        )
        kaspa_target_rect.round_corners(radius=0.2)
        kaspa_target_rect.move_to(RIGHT * 3.75)

        # Transform header rectangles
        self.play(
            Transform(btc_header_rect, btc_target_rect),
            Transform(kaspa_header_rect, kaspa_target_rect),
            run_time=2
        )

        # Define header fields - Bitcoin (all white)
        btc_fields = [
            "version:",
            "hashPrevBlock:",
            "hashMerkleRoot:",
            "Time:",
            "Bits:",
            "Nonce:"
        ]

        # Define header fields - Kaspa (white for common, yellow for unique)
        # Format: (field_text, color)
        kaspa_fields = [
            ("hash:", WHITE),  # Common
            ("version:", WHITE),  # Common
            ("parents_by_level:", WHITE),  # Kaspa-hashchain
            ("hash_merkle_root:", WHITE),  # Common
            ("accepted_id_merkle_root:", YELLOW),  # Kaspa-specific
            ("utxo_commitment:", YELLOW),  # Kaspa-specific
            ("timestamp:", WHITE),  # Common
            ("bits:", WHITE),  # Common
            ("nonce:", WHITE),  # Common
            ("daa_score:", YELLOW),  # Kaspa-specific
            ("blue_work:", YELLOW),  # Kaspa-specific
            ("blue_score:", YELLOW),  # Kaspa-specific
            ("pruning_point:", YELLOW),  # Kaspa-specific
        ]

        field_font_size = 16
        field_spacing = 0.35

        # Calculate centering for Bitcoin fields
        btc_num_fields = len(btc_fields)
        btc_total_height = (btc_num_fields - 1) * field_spacing
        btc_field_start_y = btc_total_height / 2

        # Calculate centering for Kaspa fields
        kaspa_num_fields = len(kaspa_fields)
        kaspa_total_height = (kaspa_num_fields - 1) * field_spacing
        kaspa_field_start_y = kaspa_total_height / 2

        self.btc_header_fields = VGroup()
        self.kaspa_header_fields = VGroup()

        # Create Bitcoin fields (all white)
        for i, btc_field_text in enumerate(btc_fields):
            btc_field = Text(btc_field_text, font_size=field_font_size, color=WHITE)
            btc_field.move_to(
                btc_header_rect.get_center() + UP * (btc_field_start_y - i * field_spacing)
            )

            # Create corresponding Kaspa field with appropriate color
            kaspa_field_text, kaspa_color = kaspa_fields[i] if i < len(kaspa_fields) else ("", WHITE)
            kaspa_field = Text(kaspa_field_text, font_size=field_font_size, color=kaspa_color)
            kaspa_field.move_to(
                kaspa_header_rect.get_center() + UP * (kaspa_field_start_y - i * field_spacing)
            )

            self.play(
                Create(btc_field),
                Create(kaspa_field),
                run_time=0.4
            )

            self.btc_header_fields.add(btc_field)
            self.kaspa_header_fields.add(kaspa_field)

            # Create remaining Kaspa-only fields (all yellow)
        for i in range(len(btc_fields), len(kaspa_fields)):
            kaspa_field_text, kaspa_color = kaspa_fields[i]
            kaspa_field = Text(kaspa_field_text, font_size=field_font_size, color=kaspa_color)
            kaspa_field.move_to(
                kaspa_header_rect.get_center() + UP * (kaspa_field_start_y - i * field_spacing)
            )

            self.play(
                Create(kaspa_field),
                run_time=0.4
            )

            self.kaspa_header_fields.add(kaspa_field)

        self.wait(2)


    def zoom_out_from_headers(self):
        """Zoom out from headers back to full block view"""

        # Fade out header fields
        self.play(
            FadeOut(self.btc_header_fields),
            FadeOut(self.kaspa_header_fields),
            run_time=1
        )

        # Get header rectangles
        btc_header = self.bitcoin_sections[0]
        kaspa_header = self.kaspa_sections[0]
        btc_header_rect = btc_header[0]
        kaspa_header_rect = kaspa_header[0]

        # Transform headers back to original size and position
        self.play(
            Transform(btc_header_rect, self.btc_header_rect_original),
            Transform(kaspa_header_rect, self.kaspa_header_rect_original),
            run_time=2
        )

        # Separate rectangles (stroke-only) from text labels (fill-based)
        rect_targets = [
            self.bitcoin_square[0],
            self.kaspa_square[0],
            self.bitcoin_sections[1][0],  # Body rectangle
            self.kaspa_sections[1][0],  # Body rectangle
            btc_header[0],  # Header rectangle
            kaspa_header[0],  # Header rectangle
        ]

        text_targets = [
            self.bitcoin_square[1],
            self.kaspa_square[1],
            self.bitcoin_sections[1][1],  # Body label
            self.kaspa_sections[1][1],  # Body label
            btc_header[1],  # Header label
            kaspa_header[1],  # Header label
        ]

        # Restore stroke opacity for rectangles and fill opacity for text
        self.play(
            *[mob.animate.set_stroke(opacity=1.0) for mob in rect_targets],
            *[mob.animate.set_fill(opacity=1.0) for mob in text_targets],
            run_time=1
        )

        self.wait(3)


class MerkleRootConstruction(HUD2DScene):
    def construct(self):
        # Phase 1: Build logical tree structure (no animation)
        transactions = [
            "Tx0: Alice -> Bob: 1 BTC",
            "Tx1: Bob -> Charlie: 0.5 BTC",
            "Tx2: Charlie -> David: 0.3 BTC",
            "Tx3: David -> Eve: 0.2 BTC"
        ]

        tx_hashes = [hashlib.sha256(tx.encode()).hexdigest()[:8] for tx in transactions]

        # Build tree structure logically first
        tree_structure = self.build_merkle_tree(tx_hashes)

        # Phase 2: Animate construction bottom-up
        self.animate_merkle_construction(tree_structure)

    def build_merkle_tree(self, tx_hashes):
        """Build the complete tree structure and return all nodes organized by level."""
        level_height = 2.5  # Increased for better spacing
        node_spacing = 3

        # Create leaf nodes
        leaf_nodes = []
        for i, hash_text in enumerate(tx_hashes):
            x = (i - len(tx_hashes) / 2 + 0.5) * node_spacing
            node = self.create_styled_hash_node(hash_text, f"Tx{i}")
            node.move_to([x, -2, 0])
            leaf_nodes.append(node)

            # Build tree structure
        all_levels = [leaf_nodes]
        current_level = leaf_nodes

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    parent = self.create_parent_node(current_level[i], current_level[i + 1])
                else:
                    parent = self.create_parent_node(current_level[i], current_level[i])
                next_level.append(parent)

                # Position next level - FIXED: use -2 as base
            y = -2 + len(all_levels) * level_height
            for i, node in enumerate(next_level):
                x = (i - len(next_level) / 2 + 0.5) * node_spacing * 1.5
                node.move_to([x, y, 0])

            all_levels.append(next_level)
            current_level = next_level

        return all_levels

    def animate_merkle_construction(self, tree_structure):
        """Animate the already-built tree structure."""
        # Create leaf nodes
        self.play(*[Create(node) for node in tree_structure[0]])
        self.wait(1)

        # Animate each level
        for level_idx in range(1, len(tree_structure)):
            level = tree_structure[level_idx]
            prev_level = tree_structure[level_idx - 1]

            # Animate each parent node individually
            for i, node in enumerate(level):
                child1_idx = i * 2
                child2_idx = min(i * 2 + 1, len(prev_level) - 1)

                # Do copy animation, then immediately create parent
                self.animate_hashing_with_copy(
                    prev_level[child1_idx],
                    prev_level[child2_idx],
                    node
                )
                self.play(Create(node))

            self.wait(0.5)

            # Highlight final root
        root = tree_structure[-1][0]
        self.play(
            root.animate.set_color(GOLD).set_stroke_width(4),
            Indicate(root, scale_factor=1.2)
        )

        # Add title
        title = Text("Merkle Root", font_size=36, color=GOLD)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(2)

    def animate_hashing_with_copy(self, left, right, parent):
        """Create copies that move up and merge to form parent."""
        # Create copies with different colors
        left_copy = left.copy().set_color(YELLOW).set_opacity(0.8)
        right_copy = right.copy().set_color(YELLOW).set_opacity(0.8)

        # Position copies slightly offset for visibility
        left_copy.move_to(left.get_center())
        right_copy.move_to(right.get_center())

        # Animate copies moving upward and merging
        self.play(
            Create(left_copy),
            Create(right_copy),
            run_time=0.3
        )

        # Move copies toward parent position
        self.play(
            left_copy.animate.move_to(parent.get_center() + LEFT * 0.3),
            right_copy.animate.move_to(parent.get_center() + RIGHT * 0.3),
            run_time=0.5
        )

        # Merge and fade out - FIXED: removed radius parameter
        self.play(
            FadeOut(left_copy),
            FadeOut(right_copy),
            Flash(parent.get_center(), color=YELLOW),  # Removed radius=0.5
            run_time=0.3
        )

    def create_styled_hash_node(self, hash_text, label):
        """Create a white rounded square node with hash and label."""
        # Main square with white stroke and rounded corners
        square = Rectangle(
            width=3,
            height=2,
            stroke_color=WHITE,
            stroke_width=3,
            fill_opacity=0.1,
            color=BLUE
        )
        square.round_corners(radius=0.3)

        # Hash text inside square (centered)
        hash_mob = Text(hash_text, font_size=16, color=WHITE)
        hash_mob.move_to(square.get_center())

        # Label inside square, near upper edge and centered
        label_mob = Text(label, font_size=14, color=WHITE)
        # Position at upper edge but slightly inside
        label_y = square.get_top()[1] - 0.3  # 0.3 units down from top edge
        label_mob.move_to([square.get_center()[0], label_y, 0])

        # Group everything
        group = VGroup(square, hash_mob, label_mob)
        return group

    def create_parent_node(self, left_child, right_child):
        """Create a parent hash node from two children."""
        # Extract hash text from children (index 1 is the hash text in VGroup)
        left_hash = left_child[1].text
        right_hash = right_child[1].text
        combined_hash = f"H({left_hash}+{right_hash})"[:8]

        parent = self.create_styled_hash_node(combined_hash, "Hash")
        return parent

    def animate_hashing(self, left, right, parent):
        # Show data flowing upward
        left_copy = left.copy().set_color(YELLOW)
        right_copy = right.copy().set_color(YELLOW)

        self.play(
            left_copy.animate.move_to(parent.get_center()),
            right_copy.animate.move_to(parent.get_center()),
            FadeOut(left_copy), FadeOut(right_copy)
        )

####################
# Kaspa Specific Examples
####################

def test_theme() -> KaspaConfig:
    """Test theme with various configuration parameters."""
    return {
        "block_color": RED,
        "fill_opacity": 0.7,
        "stroke_color": BLUE,
        "stroke_width": 5,
        "k": 25,
        "label_font_size": 32,
        "horizontal_spacing": 2.5,
        "vertical_spacing": 1.5,
    }

class PastFutureAnticone(HUD2DScene):
    """Explainer for Dag Relationships."""

    def construct(self):
        wait_time = 5

        dag = KaspaDAG(scene=self)
        dag.config.k = 18
        dag.config.genesis_x = -4

        self.wait(1)
        self.narrate("Kaspa DAG Relationships")

        block_g, block_a, block_b, block_c, block_d = dag.create_blocks_from_list_instant([
            ("Gen", None, "G"),
            ("b1", ["Gen"], "A"),
            ("b2", ["b1"], "B"),
            ("b3", ["b2"], "C"),
            ("b4", ["b3"], "D"),
        ])

        self.caption("A Linear Chain is a restricted DAG.")
        self.wait(wait_time)
        self.caption("Here we have a Chain of Blocks.")
        self.wait(wait_time)
        self.caption("A BlockChain has Past relationships.")
        dag.highlight_past(block_b)
        self.wait(wait_time)
        self.caption("The Past of Block B includes G and A.")
        self.wait(wait_time)
        self.caption("A BlockChain has Future relationships.")
        dag.highlight_future(block_b)
        self.wait(wait_time)
        self.caption("The Future of Block B includes C and D.")
        self.wait(wait_time)
        self.caption("A BlockChain is restricted to Past and Future relationships.")
        dag.reset_highlighting()
        self.wait(wait_time)
        self.clear_caption()
        dag.clear_all_blocks()

        block_g, block_a, block_b, block_c, block_d, block_e = dag.create_blocks_from_list_instant([
            ("Gen", None, "G"),
            ("b1", ["Gen"], "A"),
            ("b2", ["b1"], "B"),
            ("b2a", ["b1"], "C"),
            ("b3", ["b2", "b2a"], "D"),
            ("b4", ["b3"], "E"),
        ])

        self.wait(wait_time)
        self.caption("A BlockDAG has one more relationship to define.")
        self.wait(wait_time)
        self.caption("A BlockDAG has Past relationships.")
        dag.highlight_past(block_b)
        self.wait(wait_time)
        self.caption("The Past of Block B includes G and A.")
        self.wait(wait_time)
        self.caption("A BlockDAG has Future relationships.")
        dag.highlight_future(block_b)
        self.wait(wait_time)
        self.caption("The Future of Block B includes D and E.")
        self.wait(wait_time)
        dag.reset_highlighting()
        self.caption("Block C is not in the Past or Future of Block B.")
        self.wait(wait_time)
        self.caption("This relationship is Anticone.")
        self.wait(wait_time)
        self.caption("Block C is in the Anticone of Block B.")
        dag.fade_except_anticone(block_c)
        self.play(block_c.animate.set_stroke_color(YELLOW))
        self.wait(wait_time)
        self.caption("Block B is in the Anticone of Block C.")
        self.play(block_c.animate.reset_stroke_color(),
                  block_b.animate.set_stroke_color(YELLOW))
        self.wait(wait_time)
        self.caption("Block C and Block B are Anticone each other.")
        self.play(block_c.animate.set_stroke_color(YELLOW))
        self.wait(wait_time)
        self.caption("Block B and Block C are in each other's Anticone.")

        self.wait(8.0)

class FinalityDepth(HUD2DScene):
    """Explainer for Finality Depth."""

    def construct(self):
        dag = KaspaDAG(scene=self)
        self.wait(1)
        self.narrate("Kaspa Finality Depth - Oversimplified", run_time=1.0)
        # Create entire structure from scratch, including genesis
        all_blocks = dag.create_blocks_from_list_instant([
            ("Gen", None),  # Genesis block (no parents)
            ("b1", ["Gen"]),  # Child of genesis
            ("b2", ["b1"]),  # Child of b1
            ("b3", ["b2"]),  # Child of b2
            ("b4", ["b3"]),  # Child of b3
            ("b5", ["b4"]),  # Child of b4
        ])
        self.caption("This is our current view of the DAG", run_time=1.0)
        self.wait(5)
        self.caption("Finality Depth in this example is $4$", run_time=1.0)
        dag.highlight(all_blocks[1])
        self.wait(5)

        other_blocks = dag.create_blocks_from_list_instant([
            ("b1a", ["Gen"]),  # Child of genesis
            ("b2a", ["b1a"]),  # Child of b1
            ("b3a", ["b2a"]),  # Child of b2
            ("b4a", ["b3a"]),  # Child of b3
            ("b5a", ["b4a"]),  # Child of b4
        ])

        self.caption("This newly revealed fork is NOT in the future of Finality Point", run_time=1.0)
        self.wait(5)
        self.caption("This fork is rejected with a Finality Violation", run_time=1.0)
        dag.fade_blocks(other_blocks)
        self.wait(5)
        self.clear_caption(run_time=1.0)
        dag.clear_all_blocks()

        # Create entire structure from scratch, including genesis
        all_blocks = dag.create_blocks_from_list_instant([
            ("Gen", None),  # Genesis block (no parents)
            ("b1", ["Gen"]),  # Child of genesis
            ("b2", ["b1"]),  # Child of b1
            ("b3", ["b2"]),  # Child of b2
            ("b4", ["b3"]),  # Child of b3
            ("b5", ["b4"]),  # Child of b4
        ])

        self.caption("Back to our current view of the DAG", run_time=1.0)
        self.wait(5)
        self.caption("Finality Depth is still $4$", run_time=1.0)
        dag.highlight(all_blocks[1])
        self.wait(5)

        other_blocks = dag.create_blocks_from_list_instant([
            ("b2a", ["b1"]),  # Child of b1
            ("b3a", ["b2a"]),  # Child of b2
            ("b4a", ["b3a"]),  # Child of b3
            ("b5a", ["b4a"]),  # Child of b4
        ])

        self.caption("This newly revealed fork is in the future of Finality Point", run_time=1.0)
        self.wait(5)
        self.caption("This fork does NOT violate Finality", run_time=1.0)
        self.wait(5)
        self.caption("Kaspa uses $432,000$ as its Finality Depth", run_time=1.0)
        self.wait(5)
        self.caption(r"The probability of a 49\% adversary successfully creating this fork...", run_time=1.0)
        self.wait(5)
        self.caption("...is $(49/51)^{432000}$ or $10^{-7522}$", run_time=1.0)
        self.wait(5)
        self.caption("In cryptography, $10^{-100}$ is already accepted as 'Effectively Zero'.", run_time=1.0)
        self.wait(5)
        self.caption("At $10^{-7522}$, this event is physically impossible in our universe.", run_time=1.0)
        self.wait(8)

class MergeDepthBound(HUD2DScene):
    """Explainer for Merge Depth."""

    def construct(self):
        wait_time = 5

        dag = KaspaDAG(scene=self)
        dag.config.k = 2

        self.wait(1)
        self.narrate("Kaspa Merge Depth Bound - Oversimplified")
        # Create entire structure from scratch, including genesis
        all_blocks = dag.create_blocks_from_list_instant([
            ("Gen", None, "G"),
            ("b1", ["Gen"], "A"),
            ("b2", ["b1"], "B"),
            ("b3", ["b2"], "C"),
            ("b4", ["b3"], "D"),
            ("b5", ["b4"], "E"),
        ])
        self.caption("This demonstration uses k=2")
        self.wait(wait_time)
        self.caption("Merge Depth Bound in this example is $4$")
        self.wait(wait_time)
        self.play(all_blocks[5].animate.set_stroke_color(YELLOW).set_stroke_width(7))
        self.play(all_blocks[4].animate.set_label_text(1).set_stroke_color(YELLOW).set_stroke_width(7),
                  all_blocks[5].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[3].animate.set_label_text(2).set_stroke_color(YELLOW).set_stroke_width(7),
                  all_blocks[4].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[2].animate.set_label_text(3).set_stroke_color(YELLOW).set_stroke_width(7),
                  all_blocks[3].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[1].animate.set_stroke_width(8).set_stroke_color(YELLOW).set_label_text(4),
                  all_blocks[2].animate.reset_stroke_color().reset_stroke_width())
        self.wait(wait_time)

        other_blocks = dag.create_blocks_from_list_instant([
            ("b1a", ["Gen"], "F"),
            ("b5a", ["b1a","b4"], "H"),
        ])

        self.play(all_blocks[1].animate.reset_stroke_width().reset_stroke_color().reset_label_text(),
                  all_blocks[2].animate.reset_label_text(),
                  all_blocks[3].animate.reset_label_text(),
                  all_blocks[4].animate.reset_label_text(),
                  )

        self.wait(wait_time)
        self.caption("From Block H, identify the Merge Depth Root.")
        self.wait(wait_time)
        self.play(other_blocks[1].animate.set_stroke_color(YELLOW).set_stroke_width(7))
        self.play(all_blocks[4].animate.set_label_text(1).set_stroke_color(YELLOW).set_stroke_width(7),
                  other_blocks[1].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[3].animate.set_label_text(2).set_stroke_color(YELLOW).set_stroke_width(7),
                  all_blocks[4].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[2].animate.set_label_text(3).set_stroke_color(YELLOW).set_stroke_width(7),
                  all_blocks[3].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[1].animate.set_stroke_width(8).set_stroke_color(YELLOW).set_label_text(4),
                  all_blocks[2].animate.reset_stroke_color().reset_stroke_width())

        self.wait(wait_time)
        self.caption("Block H attempts to Merge a block NOT in the Future of Merge Depth Root.")
        self.wait(wait_time)
        self.caption("Because Block F violates the Merge Depth Bound...")
        self.play(other_blocks[0].animate.set_fill_color(BLACK))
        self.wait(wait_time)
        self.caption("Block H is invalid.")
        self.play(other_blocks[1].animate.set_fill_color(BLACK))
        self.wait(wait_time)
        self.caption("Block H will NOT become a Parent of any Future blocks.")
        self.wait(wait_time)
        dag.fade_blocks(other_blocks)
        self.wait(wait_time)
        self.clear_caption()
        dag.clear_all_blocks()

        all_blocks = dag.create_blocks_from_list_instant([
            ("Gen", None, "G"),
            ("b1", ["Gen"], "A"),
            ("b2", ["b1"], "B"),
            ("b3", ["b2"], "C"),
            ("b4", ["b3"], "D"),
            ("b5", ["b4"], "E"),
        ])

        self.caption("Back to our current view of the DAG")
        self.wait(wait_time)

        other_blocks = dag.create_blocks_from_list_instant([
            ("b1a", ["Gen"], "F"),
            ("b4a", ["b1a","b3"], "H"),
        ])

        self.caption("The Merge Depth Bound is still 4.")
        self.wait(wait_time)
        self.play(other_blocks[1].animate.set_stroke_color(YELLOW).set_stroke_width(7))
        self.play(all_blocks[3].animate.set_label_text(1).set_stroke_color(YELLOW).set_stroke_width(7),
                  other_blocks[1].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[2].animate.set_label_text(2).set_stroke_color(YELLOW).set_stroke_width(7),
                  all_blocks[3].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[1].animate.set_label_text(3).set_stroke_color(YELLOW).set_stroke_width(7),
                  all_blocks[2].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[0].animate.set_stroke_width(8).set_stroke_color(YELLOW).set_label_text(4),
                  all_blocks[1].animate.reset_stroke_color().reset_stroke_width())
        self.wait(wait_time)
        self.caption("Block H Merges Block F")
        self.wait(wait_time)
        self.caption("Block F is in the Future of the Merge Depth Root, Block F is valid.")
        self.wait(wait_time)
        self.caption("Block F does NOT invalidate Block H, Block H can be included as a Parent.")
        self.wait(wait_time)

        self.play(all_blocks[0].animate.reset_stroke_width().reset_stroke_color().reset_label_text(),
                  all_blocks[1].animate.reset_label_text(),
                  all_blocks[2].animate.reset_label_text(),
                  all_blocks[3].animate.reset_label_text(),
                  )
        self.wait(wait_time)

        final_block = dag.create_blocks_from_list_instant([
            ("b6", ["b4a","b5"], "I"),
        ])

        self.caption("Block I is added to Merge blocks E and H.")
        self.wait(wait_time)
        self.caption("The Merge Depth Root from Block I is 4.")
        self.wait(wait_time)
        self.play(final_block[0].animate.set_stroke_color(YELLOW).set_stroke_width(7))
        self.play(all_blocks[5].animate.set_stroke_color(YELLOW).set_label_text(1).set_stroke_width(7),
                  final_block[0].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[4].animate.set_stroke_color(YELLOW).set_label_text(2).set_stroke_width(7),
                  all_blocks[5].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[3].animate.set_stroke_color(YELLOW).set_label_text(3).set_stroke_width(7),
                  all_blocks[4].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[2].animate.set_stroke_color(YELLOW).set_stroke_width(8).set_label_text(4),
                  all_blocks[3].animate.reset_stroke_color().reset_stroke_width())
        self.wait(wait_time)
        self.caption("Even though there is a red block that violates the Merge Depth Bound")
        self.play(other_blocks[0].animate.set_fill_color(color=PURE_RED))
        self.wait(wait_time)
        self.play(all_blocks[5].animate.reset_label_text(),
                  all_blocks[4].animate.reset_label_text(),
                  all_blocks[3].animate.reset_label_text(),
                  all_blocks[2].animate.reset_label_text().reset_stroke_width().reset_stroke_color())
        self.wait(wait_time)
        self.caption("This block is \"Kosherized\" by the Blue block in the Mergeset")
        self.play(other_blocks[1].animate.set_fill_color(color=PURE_BLUE))
        self.play(other_blocks[1].animate.set_stroke_color(YELLOW).set_stroke_width(7))
        self.play(all_blocks[3].animate.set_stroke_color(YELLOW).set_stroke_width(7).set_label_text(1),
                  other_blocks[1].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[2].animate.set_stroke_color(YELLOW).set_stroke_width(7).set_label_text(2),
                  all_blocks[3].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[1].animate.set_stroke_color(YELLOW).set_stroke_width(7).set_label_text(3),
                  all_blocks[2].animate.reset_stroke_color().reset_stroke_width())
        self.play(all_blocks[0].animate.set_stroke_color(YELLOW).set_stroke_width(7).set_label_text(4),
                  all_blocks[1].animate.reset_stroke_color().reset_stroke_width())
        self.wait(wait_time)
        self.caption("This is the only exception to the Merge Depth Bound")
        self.wait(8)

class DAGvsCHAIN(HUD2DScene):
    """Explainer for DAG vs CHAIN."""

    def construct(self):
        dag = KaspaDAG(scene=self)
        dag.config.k = 0

        self.wait(1)
        self.narrate("Kaspa BlockDAG vs BlockChain", run_time=1.0)
        # Create entire structure from scratch, including genesis
        all_blocks = dag.create_blocks_from_list_instant([
            ("Gen", None),
            ("b1", ["Gen"]),
            ("b2", ["b1"]),
            ("b3", ["b2"]),
            ("b4", ["b3"]),
            ("b5", ["b4"]),
        ])
        self.caption("This is a BlockDAG", run_time=1.0)
        self.wait(5)
        self.caption("A Directed Acyclic Graph of Blocks", run_time=1.0)
        self.wait(5)
        self.caption("Edges(Connections) are Directional, only pointing one way.", run_time=1.0)
        chain_lines = dag.highlight_lines(all_blocks)
        self.wait(5)
        self.caption("Follow Edges from any Node(Block), there are No Cycles(Acyclic).", run_time=1.0)
        self.wait(5)
        self.caption("This appears as a BlockChain, but it's really a constrained BlockDAG", run_time=1.0)
        self.wait(5)
        self.caption("BlockChain = BlockDAG with artificial Single Parent Rule", run_time=1.0)
        self.wait(5)

        other_blocks = dag.create_blocks_from_list_instant([
            ("b5a", ["b4"]),
        ])
        other_chain_lines = dag.highlight_lines(other_blocks)
        self.caption("Occasionally a Parallel Block is created", run_time=1.0)
        self.wait(5)
        self.caption("The blocks in this BlockDAG can only link a Single Parent.", run_time=1.0)
        self.wait(5)
        final_block = dag.create_blocks_from_list_with_camera_movement([
            ("b6", ["b5"]),
        ])
        final_chain_line = dag.highlight_lines(final_block)
        self.caption("Leaving all but one block, Orphaned.", run_time=1.0)
        self.wait(5)
        self.caption("The Single Parent Restriction on a BlockDAG, results in a BlockChain", run_time=1.0)
        self.wait(5)
        self.clear_caption(run_time=1.0)
        dag.unhighlight_lines(chain_lines, other_chain_lines, final_chain_line)
        dag.clear_all_blocks()
        dag.reset_camera()

        all_blocks = dag.create_blocks_from_list_instant([
            ("Gen", None),
            ("b1", ["Gen"]),
            ("b2", ["b1"]),
            ("b3", ["b2"]),
            ("b4", ["b3"]),
            ("b5", ["b4"]),
        ])
        dag.highlight_lines(all_blocks)

        self.caption("Back to our original BlockDAG", run_time=1.0)
        self.wait(5)

        other_blocks = dag.create_blocks_from_list_instant([
            ("b5a", ["b4"]),
        ])
        dag.highlight_lines(other_blocks)

        self.caption("When a Parallel Block is created without the Single Parent Limit", run_time=1.0)
        self.wait(5)
        self.caption("Removing the artificial constraint unlocks the full BlockDAG", run_time=1.0)
        self.wait(5)

        final_block = dag.create_blocks_from_list_with_camera_movement([
            ("b6", ["b5a", "b5"]),
        ])
        dag.highlight_lines(final_block)

        self.caption("A new block can reference Multiple Parents", run_time=1.0)
        self.wait(5)
        self.caption("A BlockChain is a BlockDAG restricted to a Single Parent", run_time=1.0)
        self.wait(5)
        self.caption("A BlockDAG is a BlockChain without artificial constraints", run_time=1.0)
        self.wait(8)

class LongestvsHeaviest(HUD2DScene):
    """Explainer for Longest vs Heaviest."""

    def construct(self):
        dag = KaspaDAG(scene=self)
        dag.config.k = 1
        dag.config.other_parent_line_color = BLUE # Override other lines to be blue too, DAG behavior deviates from logical block

        self.wait(1)
        self.narrate("Kaspa - Longest Chain vs Heaviest DAG", run_time=1.0)
        # Create entire structure from scratch, including genesis
        all_blocks = dag.create_blocks_from_list_instant([
            ("Gen", None, "1"),
            ("b1", ["Gen"], "2"),
            ("b2", ["b1"], "3"),
            ("b3", ["b2"], "4"),
            ("b4", ["b3"], "5"),
            ("b5", ["b4"], "6"),
        ])
        self.caption("Starting with the Longest Chain Rule", run_time=1.0)
        self.wait(5)
        self.caption("This Chain is 6 blocks long.", run_time=1.0)
        self.wait(5)

        other_blocks = dag.create_blocks_from_list_instant([
            ("b1a", ["Gen"], "2"),
            ("b2a", ["b1a"], "3"),
            ("b3a", ["b2a"], "4"),
            ("b4a", ["b3a"], "5"),
        ])

        self.caption("A competing Chain is 5 blocks long.", run_time=1.0)
        self.wait(5)
        self.caption("There is a problem with this measurement.", run_time=1.0)
        self.wait(5)
        self.caption("``Longest Chain'' ignores the Work required to create a block.", run_time=1.0)
        self.wait(5)

        self.play(
            all_blocks[1].animate.set_label_text("1.5"),
            all_blocks[2].animate.set_label_text("2"),
            all_blocks[3].animate.set_label_text("2.5"),
            all_blocks[4].animate.set_label_text("3"),
            all_blocks[5].animate.set_label_text("3.5"),
        )

        self.caption("Inspecting the Work required to create these Chains...", run_time=1.0)
        self.wait(5)
        self.caption("...we see ``Longest Chain'' favors blocks over Work.", run_time=1.0)
        dag.highlight(all_blocks[5])
        self.wait(5)
        self.caption("In a Proof of Work system, you need to measure Work.", run_time=1.0)
        self.wait(5)
        self.caption("``Longest Chain'' was changed very early to ``Heaviest Chain''", run_time=1.0)
        self.wait(5)
        self.caption("To avoid the ``Longest Chain'' with less Work being accepted.", run_time=1.0)
        self.wait(5)
        dag.reset_highlighting()
        self.caption("Measuring Work ensures the Chain with the most Work is Selected", run_time=1.0)
        dag.highlight(other_blocks[3])
        self.wait(5)
        self.caption("Preserving the Security of Bitcoin.", run_time=1.0)
        self.wait(5)
        self.clear_caption(run_time=1.0)
        dag.clear_all_blocks()
        dag.reset_camera()

        all_blocks = dag.create_blocks_from_list_instant([
            ("Gen", None, "1"),
            ("b1", ["Gen"], "2"),
            ("b2", ["b1"], "3"),
            ("b3", ["b2"], "4"),
            ("b4", ["b3"], "5"),
            ("b5", ["b4"], "6"),
        ])

        self.caption("Back to our original BlockDAG", run_time=1.0)
        self.wait(5)

        other_blocks = dag.create_blocks_from_list_instant([
            ("b1a", ["Gen"], "2"),
            ("b2a", ["b1a"], "3"),
            ("b3a", ["b2a"], "4"),
            ("b4a", ["b3a"], "5"),
        ])

        self.caption("Kaspa uses the same ``Heaviest Chain'' Idea", run_time=1.0)
        self.wait(5)

        self.play(
            all_blocks[1].animate.set_label_text("1.5"),
            all_blocks[2].animate.set_label_text("2"),
            all_blocks[3].animate.set_label_text("2.5"),
            all_blocks[4].animate.set_label_text("3"),
            all_blocks[5].animate.set_label_text("3.5"),
        )

        self.caption("Inspect the Work of these competing Chains, just like Bitcoin.", run_time=1.0)
        self.wait(5)
        self.caption("By inspecting the Work, Kaspa also preserves Security.", run_time=1.0)
        self.wait(5)

        final_block = dag.create_blocks_from_list_with_camera_movement_override_sp([
            ("b6", ["b4a", "b5"], "8.5"),
        ])

        self.caption("Kaspa uses Work to identify the Parent Chain within the DAG", run_time=1.0)
        dag.highlight(final_block[0])
        self.wait(5)
        self.caption("Critical for Linear Block Ordering", run_time=1.0)
        self.wait(3)
        dag.highlight(other_blocks[3])
        dag.highlight(other_blocks[2])
        self.play(self.camera.frame.animate.move_to(all_blocks[4].get_center()), run_time=1.0)
        dag.highlight(other_blocks[1])
        self.play(self.camera.frame.animate.move_to(all_blocks[3].get_center()), run_time=1.0)
        dag.highlight(other_blocks[0])
        dag.highlight(all_blocks[0])
        self.wait(3)
        self.clear_caption(run_time=1.0)
        self.wait(5)

class GHOSTDAGFig3Concise(HUD2DScene):
    """GHOSTDAG Fig 3 from the 'PHANTOM GHOSTDAG A Scalable Generalization of Nakamoto Consensus, 11/10/21', animated, concise version"""

    def construct(self):
        dag = KaspaDAG(scene=self)
        dag.config.k = 3
        animation_wait_time = 5.0
        animation_coloring_time = 1.0
        caption_time = 1.0

        self.wait(1)
        self.narrate("PHANTOM GHOSTDAG (fig 3)", run_time=caption_time)

        block_gen, block_e, block_d, block_c, block_b, block_i, block_h, block_f, block_l, block_k, block_j, block_m = dag.create_blocks_from_list_instant_with_vertical_centering(
            [
                ("Gen", None, "Gen"),
                ("E", ["Gen"], "E", 2),
                ("D", ["Gen"], "D", 0),
                ("C", ["Gen"], "C", 1),
                ("B", ["Gen"], "B"),
                ("I", ["E"], "I"),
                ("H", ["D", "C", "E"], "H"),
                ("F", ["B", "C"], "F"),
                ("L", ["I", "D"], "L"),
                ("K", ["B", "H", "I"], "K"),
                ("J", ["F", "H"], "J"),
                ("M", ["K", "F"], "M")
            ])

        virtual = dag.add_virtual_to_scene()

        self.caption("GHOSTDAG: Selecting chain with highest Blue Scores", run_time=caption_time)
        self.wait(animation_wait_time)

        ##########
        # First check
        ##########

        dag.fade_blocks(block_gen, block_e, block_d, block_c, block_b, block_i, block_h, block_f, block_k)
        self.caption("Tips M, J, L compete - highest Blue Score wins", run_time=caption_time)
        self.play(block_m.animate.set_label_text(block_m.ghostdag.blue_score))
        self.play(block_j.animate.set_label_text(block_j.ghostdag.blue_score))
        self.play(block_l.animate.set_label_text(block_l.ghostdag.blue_score))
        self.play(block_m.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("M selected: highest Blue Score among tips", run_time=caption_time)
        self.play(block_m.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.play(block_m.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_m.animate.set_label_text(block_m.name))
        self.play(block_j.animate.set_label_text(block_j.name))
        self.play(block_l.animate.set_label_text(block_l.name))
        self.wait(animation_wait_time)
        self.clear_caption()

        ##########
        # Reset for next check
        ##########

        dag.fade_blocks(block_j, block_l)
        dag.unfade_blocks(block_k, block_f)
        self.play(block_k.animate.set_label_text(block_k.ghostdag.blue_score))
        self.play(block_f.animate.set_label_text(block_f.ghostdag.blue_score))
        self.play(block_k.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("K selected: highest scoring parent of M", run_time=caption_time)
        self.play(block_k.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.play(block_k.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_k.animate.set_label_text(block_k.name))
        self.play(block_f.animate.set_label_text(block_f.name))
        self.wait(animation_wait_time)
        self.clear_caption()

        ##########
        # Reset for next check
        ##########

        dag.fade_blocks(block_f)
        dag.unfade_blocks(block_h, block_i, block_b)
        self.play(block_h.animate.set_label_text(block_h.ghostdag.blue_score))
        self.play(block_i.animate.set_label_text(block_i.ghostdag.blue_score))
        self.play(block_b.animate.set_label_text(block_b.ghostdag.blue_score))
        self.play(block_h.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("H selected: highest scoring parent of K", run_time=caption_time)
        self.play(block_h.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.play(block_h.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text(block_h.name))
        self.play(block_i.animate.set_label_text(block_i.name))
        self.play(block_b.animate.set_label_text(block_b.name))
        self.wait(animation_wait_time)
        self.clear_caption()

        ##########
        # Reset for next check
        ##########

        dag.fade_blocks(block_b, block_i)
        dag.unfade_blocks(block_d, block_c, block_e)
        self.play(block_d.animate.set_label_text(block_d.ghostdag.blue_score))
        self.play(block_c.animate.set_label_text(block_c.ghostdag.blue_score))
        self.play(block_e.animate.set_label_text(block_e.ghostdag.blue_score))
        self.play(block_d.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("D selected: breaks C, D, E tie by hash (deterministic)", run_time=caption_time)
        self.play(block_d.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.play(block_d.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_d.animate.set_label_text(block_d.name))
        self.play(block_c.animate.set_label_text(block_c.name))
        self.play(block_e.animate.set_label_text(block_e.name))
        self.wait(animation_wait_time)
        self.clear_caption()

        ##########
        # Reset for next check
        ##########

        dag.fade_blocks(block_c, block_e)
        dag.unfade_blocks(block_gen)
        self.play(block_gen.animate.set_label_text(block_gen.ghostdag.blue_score))
        self.play(block_gen.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("Genesis selected: root of the chain", run_time=caption_time)
        self.play(block_gen.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.play(block_gen.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_gen.animate.set_label_text(block_gen.name))
        self.wait(animation_wait_time)

        ##########
        # Build Blue Set
        ##########

        self.caption("Building blue set: start with empty set", run_time=caption_time)
        self.narrate(r"Blue Set \{\}", run_time=caption_time)
        self.wait(animation_wait_time)

        dag.fade_blocks(block_h, block_k, block_m, virtual)
        self.caption("Visit D: add Genesis (only block in past)", run_time=caption_time)
        self.play(block_gen.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.narrate(r"Blue Set \{Gen\}", run_time=caption_time)
        self.play(block_gen.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.wait(animation_wait_time)
        self.clear_caption()

        dag.unfade_blocks(block_h, block_c, block_e)
        self.caption("Visit H: add C, D, E (all fit k=3 limit)", run_time=caption_time)
        self.play(block_d.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.play(block_c.animate.set_fill_color(BLUE_E), run_time=animation_coloring_time)
        self.play(block_e.animate.set_fill_color(BLUE_E), run_time=animation_coloring_time)
        self.narrate(r"Blue Set \{Gen, D, C, E\}", run_time=caption_time)
        self.play(block_d.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.wait(animation_wait_time)
        self.clear_caption()

        dag.unfade_blocks(block_k, block_b, block_i)
        self.caption("Visit K: add H, I (B excluded - 4 blues in anticone)", run_time=caption_time)
        self.play(block_k.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.play(block_b.animate.set_fill_color(RED_E), run_time=animation_coloring_time)
        self.play(block_i.animate.set_fill_color(BLUE_E), run_time=animation_coloring_time)
        self.narrate(r"Blue Set \{Gen, D, C, E, H, I\}", run_time=caption_time)
        self.play(block_k.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.wait(animation_wait_time)
        self.clear_caption()

        dag.unfade_blocks(block_m, block_f)
        self.caption("Visit M: add K (F excluded - large blue anticone)", run_time=caption_time)
        self.play(block_m.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.play(block_f.animate.set_fill_color(RED_E), run_time=animation_coloring_time)
        self.narrate(r"Blue Set \{Gen, D, C, E, H, I, K\}", run_time=caption_time)
        self.play(block_m.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.wait(animation_wait_time)
        self.clear_caption()

        dag.unfade_blocks(virtual, block_j, block_l)
        self.caption("Visit V: add M (L, J excluded - would violate k-cluster)", run_time=caption_time)
        self.play(virtual.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.play(block_l.animate.set_fill_color(RED_E), run_time=animation_coloring_time)
        self.play(block_j.animate.set_fill_color(RED_E), run_time=animation_coloring_time)
        self.narrate(r"Blue Set \{Gen, D, C, E, H, I, K, M\}", run_time=caption_time)
        self.play(virtual.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.wait(3.0)

class GHOSTDAGFig3kExplained(HUD2DScene):
    """GHOSTDAG Fig 3 from the 'PHANTOM GHOSTDAG A Scalable Generalization of Nakamoto Consensus, 11/10/21', animated k explained version"""

    def construct(self):
        dag = KaspaDAG(scene=self)
        dag.config.k = 3
        animation_wait_time = 5.0
        animation_coloring_time = 1.0
        caption_time = 1.0

        self.wait(1)
        self.narrate("PHANTOM GHOSTDAG (fig 3)", run_time=caption_time)

        block_gen, block_e, block_d, block_c, block_b, block_i, block_h, block_f, block_l, block_k, block_j, block_m = dag.create_blocks_from_list_instant_with_vertical_centering([
            ("Gen", None, "Gen"),
            ("E", ["Gen"], "E", 2),
            ("D", ["Gen"], "D", 0),
            ("C", ["Gen"], "C", 1),
            ("B", ["Gen"], "B"),
            ("I", ["E"], "I"),
            ("H", ["D", "C", "E"], "H"),
            ("F", ["B", "C"], "F"),
            ("L", ["I", "D"], "L"),
            ("K", ["B", "H", "I"], "K"),
            ("J", ["F", "H"], "J"),
            ("M", ["K", "F"], "M")
        ])

        virtual = dag.add_virtual_to_scene()

        self.caption("GHOSTDAG: Selecting Chain with highest Blue Scores", run_time=caption_time)
        self.wait(animation_wait_time)

        ##########
        # First check
        ##########

        dag.fade_blocks(block_gen, block_e, block_d, block_c, block_b, block_i, block_h, block_f, block_k)
        self.caption("Tips M, J, L compete - highest Blue Score wins", run_time=caption_time)
        self.play(block_m.animate.set_label_text(block_m.ghostdag.blue_score))
        self.play(block_j.animate.set_label_text(block_j.ghostdag.blue_score))
        self.play(block_l.animate.set_label_text(block_l.ghostdag.blue_score))
        self.play(block_m.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("M selected: highest Blue Score among Tips", run_time=caption_time)
        self.play(block_m.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.wait(animation_wait_time)
        self.play(block_m.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_m.animate.set_label_text(block_m.name))
        self.play(block_j.animate.set_label_text(block_j.name))
        self.play(block_l.animate.set_label_text(block_l.name))
        self.clear_caption()

        ##########
        # Reset for next check
        ##########

        dag.fade_blocks(block_j, block_l)
        dag.unfade_blocks(block_k, block_f)
        self.play(block_k.animate.set_label_text(block_k.ghostdag.blue_score))
        self.play(block_f.animate.set_label_text(block_f.ghostdag.blue_score))
        self.play(block_k.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("K selected: highest Blue Score Parent of M", run_time=caption_time)
        self.play(block_k.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.wait(animation_wait_time)
        self.play(block_k.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_k.animate.set_label_text(block_k.name))
        self.play(block_f.animate.set_label_text(block_f.name))
        self.clear_caption()

        ##########
        # Reset for next check
        ##########

        dag.fade_blocks(block_f)
        dag.unfade_blocks(block_h, block_i, block_b)
        self.play(block_h.animate.set_label_text(block_h.ghostdag.blue_score))
        self.play(block_i.animate.set_label_text(block_i.ghostdag.blue_score))
        self.play(block_b.animate.set_label_text(block_b.ghostdag.blue_score))
        self.play(block_h.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("H selected: highest Blue Score Parent of K", run_time=caption_time)
        self.play(block_h.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.wait(animation_wait_time)
        self.play(block_h.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text(block_h.name))
        self.play(block_i.animate.set_label_text(block_i.name))
        self.play(block_b.animate.set_label_text(block_b.name))
        self.clear_caption()

        ##########
        # Reset for next check
        ##########

        dag.fade_blocks(block_b, block_i)
        dag.unfade_blocks(block_d, block_c, block_e)
        self.play(block_d.animate.set_label_text(block_d.ghostdag.blue_score))
        self.play(block_c.animate.set_label_text(block_c.ghostdag.blue_score))
        self.play(block_e.animate.set_label_text(block_e.ghostdag.blue_score))
        self.play(block_d.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("D selected: breaks C, D, E tie by hash (deterministic)", run_time=caption_time)
        self.play(block_d.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.wait(animation_wait_time)
        self.play(block_d.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_d.animate.set_label_text(block_d.name))
        self.play(block_c.animate.set_label_text(block_c.name))
        self.play(block_e.animate.set_label_text(block_e.name))
        self.clear_caption()

        ##########
        # Reset for next check
        ##########

        dag.fade_blocks(block_c, block_e)
        dag.unfade_blocks(block_gen)
        self.play(block_gen.animate.set_label_text(block_gen.ghostdag.blue_score))
        self.play(block_gen.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.caption("Genesis selected: root of the chain", run_time=caption_time)
        self.play(block_gen.animate.set_fill_color(PURE_BLUE), run_time=animation_coloring_time)
        self.wait(animation_wait_time)
        self.play(block_gen.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.play(block_gen.animate.set_label_text(block_gen.name))
        self.wait(animation_wait_time)

        ##########
        # Build Blue Set WITH k-cluster checks #TODO Automate this somehow
        ##########

        self.caption("Building Blue Set: start with empty set", run_time=caption_time)
        self.narrate(r"Blue Set k=3 \{\}", run_time=caption_time)
        self.wait(animation_wait_time)

        # SP Blue
        dag.fade_blocks(block_h, block_k, block_m, virtual)

        self.caption("Visit D: add Genesis: Selected Parent Blue by default", run_time=caption_time)
        self.play(block_gen.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_gen.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # SP Blue
        dag.unfade_blocks(block_h, block_c, block_e)

        self.caption("Visit H: add D: Selected Parent Blue by default", run_time=caption_time)
        self.play(block_d.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_d.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # Check block_c
        self.caption("Blue Candidate C: first in Mergeset, first checked", run_time=caption_time)
        self.play(block_c.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate C: has 1 Blue in Anticone", run_time=caption_time)
        self.play(block_d.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate C: 1 $\leq$ k :Passed first check", run_time=caption_time)
        self.play(block_d.animate.set_label_text(block_d.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate C: if C is Blue, D has 1 Anticone Blue", run_time=caption_time)
        self.play(block_c.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate C: 1 $\leq$ k :Passed second check", run_time=caption_time)
        self.play(block_c.animate.set_label_text(block_c.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate C: becomes Blue", run_time=caption_time)
        self.play(block_c.animate.set_fill_color(BLUE_E), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D, C\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_c.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # Check block_e
        self.caption("Blue Candidate E: next in Mergeset, next checked", run_time=caption_time)
        self.play(block_e.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate E: has 2 Blue in Anticone", run_time=caption_time)
        self.play(block_d.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_c.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate E: 2 $\leq$ k :Passed first check", run_time=caption_time)
        self.play(block_d.animate.set_label_text(block_d.name), run_time=animation_coloring_time)
        self.play(block_c.animate.set_label_text(block_c.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate E: if E is Blue, D has 2 Anticone Blues", run_time=caption_time)
        self.play(block_c.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate E: 2 $\leq$ k :Passed this second check", run_time=caption_time)
        self.play(block_c.animate.set_label_text(block_c.name), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text(block_e.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate E: if E is Blue, C has 2 Anticone Blues", run_time=caption_time)
        self.play(block_d.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate E: 2 $\leq$ k :Passed this second check", run_time=caption_time)
        self.play(block_d.animate.set_label_text(block_d.name), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text(block_e.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate E: becomes Blue", run_time=caption_time)
        self.play(block_e.animate.set_fill_color(BLUE_E), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D, C, E\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_e.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # SP Blue
        dag.unfade_blocks(block_k, block_b, block_i)

        self.caption("Visit K: add H: Selected Parent Blue by default", run_time=caption_time)
        self.play(block_h.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D, C, E, H\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_h.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # Check block_b
        self.caption("Blue Candidate B: first in Mergeset, first checked", run_time=caption_time)
        self.play(block_b.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate B: has 4 Blues in Anticone", run_time=caption_time)
        self.play(block_d.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_c.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text("3"), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text("4"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate B: 4 $>$ k :Failed first check", run_time=caption_time)
        self.play(block_d.animate.set_label_text(block_d.name), run_time=animation_coloring_time)
        self.play(block_c.animate.set_label_text(block_c.name), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text(block_e.name), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text(block_h.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate B: becomes Red", run_time=caption_time)
        self.play(block_b.animate.set_fill_color(RED_E), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D, C, E, H\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_b.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # Check block_i
        self.caption("Blue Candidate I: next in Mergeset, next checked", run_time=caption_time)
        self.play(block_i.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate I: has 3 Blues in Anticone", run_time=caption_time)
        self.play(block_d.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_c.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text("3"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate I: 3 $\leq$ k :Passed first check", run_time=caption_time)
        self.play(block_d.animate.set_label_text(block_d.name), run_time=animation_coloring_time)
        self.play(block_c.animate.set_label_text(block_c.name), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text(block_h.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate I: if I is Blue, D has 3 Anticone Blues", run_time=caption_time)
        self.play(block_c.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.play(block_i.animate.set_label_text("3"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate I: 3 $\leq$ k :Passed this second check", run_time=caption_time)
        self.play(block_c.animate.set_label_text(block_c.name), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text(block_e.name), run_time=animation_coloring_time)
        self.play(block_i.animate.set_label_text(block_i.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate I: if I is Blue, C has 3 Anticone Blues", run_time=caption_time)
        self.play(block_d.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.play(block_i.animate.set_label_text("3"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate I: 3 $\leq$ k :Passed this second check", run_time=caption_time)
        self.play(block_d.animate.set_label_text(block_d.name), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text(block_e.name), run_time=animation_coloring_time)
        self.play(block_i.animate.set_label_text(block_i.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate I: if I is Blue, H has 1 Anticone Blue", run_time=caption_time)
        self.play(block_i.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate I: 1 $\leq$ k :Passed this second check", run_time=caption_time)
        self.play(block_i.animate.set_label_text(block_i.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate I: becomes Blue", run_time=caption_time)
        self.play(block_i.animate.set_fill_color(BLUE_E), run_time=animation_coloring_time)

        self.narrate(r"Blue Set \{Gen, D, C, E, H, I\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_i.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # SP Blue
        dag.unfade_blocks(block_m, block_f)

        self.caption("Visit M: add K: Selected Parent Blue by default", run_time=caption_time)
        self.play(block_k.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D, C, E, H, I, K\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_k.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # Check block_f
        self.caption("Blue Candidate F: first in Mergeset, first checked", run_time=caption_time)
        self.play(block_f.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate F: has 5 Blues in Anticone", run_time=caption_time)
        self.play(block_d.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text("3"), run_time=animation_coloring_time)
        self.play(block_i.animate.set_label_text("4"), run_time=animation_coloring_time)
        self.play(block_k.animate.set_label_text("5"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate F: 5 $>$ k :Failed first check", run_time=caption_time)
        self.play(block_d.animate.set_label_text(block_d.name), run_time=animation_coloring_time)
        self.play(block_e.animate.set_label_text(block_e.name), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text(block_h.name), run_time=animation_coloring_time)
        self.play(block_i.animate.set_label_text(block_i.name), run_time=animation_coloring_time)
        self.play(block_k.animate.set_label_text(block_k.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate F: becomes Red", run_time=caption_time)
        self.play(block_f.animate.set_fill_color(RED_E), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D, C, E, H, I, K\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_f.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # SP Blue
        dag.unfade_blocks(virtual, block_j, block_l)

        self.caption("Visit V: add M: Selected Parent Blue by default", run_time=caption_time)
        self.play(block_m.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D, C, E, H, I, K, M\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_m.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # Check block_l
        self.caption("Blue Candidate L: first in Mergeset, first checked", run_time=caption_time)
        self.play(block_l.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate L: has 4 Blues in Anticone", run_time=caption_time)
        self.play(block_c.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.play(block_k.animate.set_label_text("3"), run_time=animation_coloring_time)
        self.play(block_m.animate.set_label_text("4"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate L: 4 $>$ k :Failed first check", run_time=caption_time)
        self.play(block_c.animate.set_label_text(block_c.name), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text(block_h.name), run_time=animation_coloring_time)
        self.play(block_k.animate.set_label_text(block_k.name), run_time=animation_coloring_time)
        self.play(block_m.animate.set_label_text(block_m.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate L: becomes Red", run_time=caption_time)
        self.play(block_l.animate.set_fill_color(RED_E), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D, C, E, H, I, K, M\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_l.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        # Check block_j
        self.caption("Blue Candidate J: next in Mergeset, next checked", run_time=caption_time)
        self.play(block_j.animate.set_stroke_color(YELLOW), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate J: has 3 Blues in Anticone", run_time=caption_time)
        self.play(block_i.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_k.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.play(block_m.animate.set_label_text("3"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate J: 3 $\leq$ k :Passed first check", run_time=caption_time)
        self.play(block_i.animate.set_label_text(block_i.name), run_time=animation_coloring_time)
        self.play(block_k.animate.set_label_text(block_k.name), run_time=animation_coloring_time)
        self.play(block_m.animate.set_label_text(block_m.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate J: if J is Blue, I has 4 Anticone Blues", run_time=caption_time)
        self.play(block_d.animate.set_label_text("1"), run_time=animation_coloring_time)
        self.play(block_c.animate.set_label_text("2"), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text("3"), run_time=animation_coloring_time)
        self.play(block_j.animate.set_label_text("4"), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption(r"Blue Candidate J: 4 $>$ k :Failed this second check", run_time=caption_time)
        self.play(block_d.animate.set_label_text(block_d.name), run_time=animation_coloring_time)
        self.play(block_c.animate.set_label_text(block_c.name), run_time=animation_coloring_time)
        self.play(block_h.animate.set_label_text(block_h.name), run_time=animation_coloring_time)
        self.play(block_j.animate.set_label_text(block_j.name), run_time=animation_coloring_time)
        self.wait(animation_wait_time)

        self.caption("Blue Candidate J: becomes Red", run_time=caption_time)
        self.play(block_j.animate.set_fill_color(RED_E), run_time=animation_coloring_time)

        self.narrate(r"Blue Set k=3 \{Gen, D, C, E, H, I, K, M\}", run_time=caption_time)
        self.wait(animation_wait_time)
        self.play(block_j.animate.reset_stroke_color(), run_time=animation_coloring_time)
        self.clear_caption()

        self.wait(3.0)

class GHOSTDAGLinearOrdering(HUD2DScene):
    """GHOSTDAG Fig 3 from the 'PHANTOM GHOSTDAG A Scalable Generalization of Nakamoto Consensus, 11/10/21', linear ordering version"""

    def construct(self):
        dag = KaspaDAG(scene=self)
        dag.config.k = 3
        animation_wait_time = 5.0
        animation_coloring_time = 1.0
        caption_time = 1.0

        self.wait(1)
        self.narrate("PHANTOM GHOSTDAG (fig 3) - Confirmations", run_time=caption_time)
        self.caption("First Draft", run_time=caption_time)

        block_gen = dag.add_block_with_params("Gen", None, "Gen", stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_b = dag.add_block_with_params("B", ["Gen"], "B", stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_c = dag.add_block_with_params("C", ["Gen"], "C", 1, stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_d = dag.add_block_with_params("D", ["Gen"], "D", 0, stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_e = dag.add_block_with_params("E", ["Gen"], "E", 2, stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_f = dag.add_block_with_params("F", ["B", "C"], "F", stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_h = dag.add_block_with_params("H", ["D", "C", "E"], "H", stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_i = dag.add_block_with_params("I", ["E"], "I", stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_j = dag.add_block_with_params("J", ["F", "H"], "J", stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_k = dag.add_block_with_params("K", ["B", "H", "I"], "K", stack_to_bottom=False)
#        self.play(block_j.visual_block.change_label(" "))
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_l = dag.add_block_with_params("L", ["I", "D"], "L", stack_to_bottom=False)
#        self.play(block_j.visual_block.change_label("test"))
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)
#        virtual = dag.destroy_virtual_block()

        block_m = dag.add_block_with_params("M", ["K", "F"], "M", stack_to_bottom=False)
#        virtual = dag.add_virtual_to_scene()
#        dag.show_ghostdag(virtual)

        animate_labels = []
        for block in dag.fade_except_future(block_b):
            if block == block_b:
                animate_labels.append(block.animate.set_label_text("TX").set_stroke_color(YELLOW).set_stroke_width(6))
            else:
                animate_labels.append(block.animate.set_label_text(1))
        self.play(*animate_labels)
        self.wait(animation_wait_time)

        self.play(*[block.animate.reset_block() for block in dag.all_blocks])

        animate_labels = []
        for block in dag.fade_except_future(block_c, with_unfade=True):
            if block == block_c:
                animate_labels.append(block.animate.set_label_text("TX").set_stroke_color(YELLOW).set_stroke_width(6))
            else:
                animate_labels.append(block.animate.set_label_text(1))
        self.play(*animate_labels)
        self.wait(animation_wait_time)

        self.play(*[block.animate.reset_block() for block in dag.all_blocks])

        animate_labels = []
        for block in dag.fade_except_future(block_d, with_unfade=True):
            if block == block_d:
                animate_labels.append(block.animate.set_label_text("TX").set_stroke_color(YELLOW).set_stroke_width(6))
            else:
                animate_labels.append(block.animate.set_label_text(1))
        self.play(*animate_labels)
        self.wait(animation_wait_time)

        self.play(*[block.animate.reset_block() for block in dag.all_blocks])

        animate_labels = []
        for block in dag.fade_except_future(block_e, with_unfade=True):
            if block == block_e:
                animate_labels.append(block.animate.set_label_text("TX").set_stroke_color(YELLOW).set_stroke_width(6))
            else:
                animate_labels.append(block.animate.set_label_text(1))
        self.play(*animate_labels)
        self.wait(animation_wait_time)

        self.play(*[block.animate.reset_block() for block in dag.all_blocks])
        dag.unfade_blocks(dag.all_blocks)

        # for block in dag.all_blocks:
        #     if block.parents:  # Genesis has no parents
        #         dag.show_blue_red_pov(block)
        #         self.caption(f"Blue-Red Past from Block {block.name}")
        #         self.wait(4)
        #         self.clear_caption()

#        self.caption("GHOSTDAG: Virtual PoV is the nodes PoV", run_time=caption_time)
        self.wait(animation_wait_time)

        ##########
        #
        ##########