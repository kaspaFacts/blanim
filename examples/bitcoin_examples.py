# blanim/examples/bitcoin_examples.py

from blanim import *


# ============================================================================
# CUSTOM CONFIGURATION FUNCTIONS - Type-safe config override
# ============================================================================

def test_bitcoin_theme() -> BitcoinConfig:
    """Test theme with various configuration parameters."""
    return {
        "block_color": PURPLE,
        "fill_opacity": 0.3,
        "stroke_color": GOLD,
        "stroke_width": 4,
        "side_length": 0.9,
        "label_font_size": 28,
        "label_color": YELLOW,
        "create_run_time": 3.0,
        "label_change_run_time": 0.8,
        "movement_run_time": 1.5,
        "line_color": RED
    }

def test_bitcoin_theme_with_offset() -> BitcoinConfig:
    """Custom theme with lower genesis position."""
    offset_config = test_bitcoin_theme()  # Your existing theme function
    offset_config["genesis_y"] = -2.0  # Position second DAG 2 units lower
    return offset_config

# ============================================================================
# BITCOIN TEST SCENES
# ============================================================================

class BitcoinChainWithConfig(HUD2DScene):
    """Demonstrate BitcoinDAG with config theming applied at DAG level.

    Shows:
    - Creating BitcoinDAG object
    - Applying custom theme using dag.apply_config()
    - Creating blocks through DAG methods
    - Config affects all blocks created by the DAG
    """

    def construct(self):
        self.narrate(r"Bitcoin Chain with Custom Config")
        self.caption(r"Using BitcoinDAG with theme applied")

        # Create DAG with default config
        dag = BitcoinDAG(scene=self)

        # Apply custom theme to the entire DAG
        dag.apply_config(test_bitcoin_theme())

        self.caption(r"Creating blocks with custom styling")

        # Create blocks using DAG methods (they inherit the applied config)
        genesis = dag.add_block()
        b1 = dag.add_block(parent=genesis)
        b2 = dag.add_block(parent=b1)
        b3 = dag.add_block(parent=b2)

        self.wait(2)

        # Demonstrate label changes with custom timing
        self.caption(r"Label changes use custom timing (0.8s)")
        self.play(b1.change_label("Custom1"))
        self.play(b2.change_label("Custom2"))

        self.wait(1)

        # Demonstrate movement with custom timing
        self.caption(r"Movement uses custom timing (1.5s)")
        self.play(
            b3.create_movement_animation(b3.animate.shift(UP * 1.5))
        )

        self.wait(2)

        # Show that all blocks have the custom styling
        self.caption(r"All blocks: PURPLE with GOLD stroke, YELLOW labels")
        self.wait(3)

        self.clear_narrate()
        self.clear_caption()


class BitcoinConfigComparison(HUD2DScene):
    """Compare default vs custom config side-by-side using BitcoinDAG objects."""

    def construct(self):
        self.narrate(r"Bitcoin Config Comparison")
        self.caption(r"Default vs Custom styling")

        # Create two DAGs with different configs
        default_dag = BitcoinDAG(scene=self)
        custom_dag = BitcoinDAG(scene=self)

        # Apply custom theme only to second DAG
        custom_dag.apply_config(test_bitcoin_theme_with_offset())

        # Create chains in both DAGs
        default_genesis = default_dag.add_block()
        default_b1 = default_dag.add_block(parent=default_genesis)

        custom_genesis = custom_dag.add_block()
        custom_b1 = custom_dag.add_block(parent=custom_genesis)

        self.wait(1)

        # Show visual difference
        self.caption(r"Top: Default BLUE blocks")
        self.caption(r"Bottom: Custom PURPLE blocks")
        self.wait(3)

        self.clear_narrate()
        self.clear_caption()
