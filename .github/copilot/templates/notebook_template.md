# Mathematical Notebook Template

## Overview

This is a template for creating new mathematical notebooks following the repository's 4-file architecture pattern.

## File Structure

For a notebook called `example_notebook`, create these files:

### 1. `example_notebook.ipynb` (Ultra-minimal notebook)
```python
# Cell 1: Imports and setup
from example_notebook_preamble import setup_environment
from example_notebook_lib import *
from example_notebook_ui import create_ui

setup_environment()

# Cell 2: Display UI
ui = create_ui()
ui.display()

# Cell 3: Display output widget  
display(ui.get_output_widget())
```

### 2. `example_notebook_preamble.py` (Documentation and setup)
```python
"""
Example Notebook - Mathematical Exploration

Mathematical Background:
Provide detailed explanation of the mathematical concepts,
including relevant formulas, theorems, and references.

Usage Instructions:
1. Run all cells in order
2. Adjust parameters using the interactive controls
3. Observe how the mathematical properties change
4. Experiment with different parameter ranges

Tips:
- Start with default parameters
- Try extreme values to observe boundary behavior
- Compare results with analytical solutions where possible
"""

def setup_environment():
    """Configure the notebook environment."""
    # Any environment-specific setup
    print("📘 Mathematical Notebook Template")
    print("🔧 Environment configured successfully")

def get_help():
    """Display detailed help information."""
    print(__doc__)
    print("\n📖 Additional Resources:")
    print("- Mathematical references...")
    print("- Code documentation...")
```

### 3. `example_notebook_lib.py` (Mathematical logic)
```python
"""
Mathematical computation library for example notebook.
"""

import numpy as np
from typing import Tuple, Optional, Any

def core_mathematical_function(z: complex, param1: float, param2: float) -> complex:
    """
    Core mathematical computation.
    
    Args:
        z: Complex input
        param1, param2: Mathematical parameters
        
    Returns:
        Complex result
    """
    # Implement mathematical algorithm
    pass

def visualization_helper(data: np.ndarray, **kwargs) -> Any:
    """
    Helper function for creating visualizations.
    
    Args:
        data: Input data for visualization
        **kwargs: Visualization parameters
        
    Returns:
        Matplotlib figure or similar visualization object
    """
    # Implement visualization logic
    pass

def validate_results(test_cases: list) -> bool:
    """
    Validate mathematical results against known solutions.
    
    Args:
        test_cases: List of test cases with expected results
        
    Returns:
        True if all tests pass
    """
    # Implement validation logic
    pass
```

### 4. `example_notebook_ui.py` (User interface)
```python
"""
User interface components for example notebook.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
from example_notebook_preamble import get_help
import example_notebook_lib as lib

class NotebookUI:
    """Main UI class for the notebook."""
    
    def __init__(self):
        self.output = widgets.Output()
        self._create_widgets()
        self._setup_layout()
        self._setup_event_handlers()
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Parameter controls
        self.param1_slider = widgets.FloatSlider(
            value=11.0, min=1.0, max=20.0, step=0.1,
            description='Parameter 1:', continuous_update=False
        )
        
        self.param2_slider = widgets.FloatSlider(
            value=5.0, min=1.0, max=10.0, step=0.1,
            description='Parameter 2:', continuous_update=False
        )
        
        # Control buttons
        self.render_button = widgets.Button(
            description='🎨 Render',
            button_style='primary',
            tooltip='Generate visualization'
        )
        
        self.help_button = widgets.Button(
            description='ℹ️ Help',
            button_style='info',
            tooltip='Show help information'
        )
        
        self.save_button = widgets.Button(
            description='💾 Save PNG',
            button_style='success',
            tooltip='Save current visualization'
        )
    
    def _setup_layout(self):
        """Organize widgets into layout."""
        parameter_box = widgets.VBox([
            widgets.HTML("<h3>📊 Parameters</h3>"),
            self.param1_slider,
            self.param2_slider
        ])
        
        control_box = widgets.HBox([
            self.render_button,
            self.help_button,
            self.save_button
        ])
        
        self.ui = widgets.VBox([
            widgets.HTML("<h2>🧮 Example Mathematical Notebook</h2>"),
            parameter_box,
            control_box,
            widgets.HTML("<hr>")
        ])
    
    def _setup_event_handlers(self):
        """Setup button click handlers."""
        self.render_button.on_click(self._render_visualization)
        self.help_button.on_click(self._show_help)
        self.save_button.on_click(self._save_visualization)
    
    def _render_visualization(self, button):
        """Render the mathematical visualization."""
        with self.output:
            clear_output(wait=True)
            
            # Get current parameter values
            param1 = self.param1_slider.value
            param2 = self.param2_slider.value
            
            print(f"🎨 Rendering with parameters: {param1}, {param2}")
            
            try:
                # Generate visualization using library functions
                fig = lib.visualization_helper(
                    param1=param1,
                    param2=param2
                )
                
                plt.show()
                print("✅ Visualization complete!")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _show_help(self, button):
        """Display help information."""
        with self.output:
            clear_output(wait=True)
            get_help()
    
    def _save_visualization(self, button):
        """Save current visualization as PNG."""
        with self.output:
            print("💾 Saving visualization...")
            try:
                plt.savefig('notebook_output.png', dpi=300, bbox_inches='tight')
                print("✅ Saved as notebook_output.png")
            except Exception as e:
                print(f"❌ Save error: {e}")
    
    def display(self):
        """Display the main UI."""
        display(self.ui)
    
    def get_output_widget(self):
        """Get the output widget for displaying results."""
        return self.output

def create_ui():
    """Create and return the main UI instance."""
    return NotebookUI()
```

## Testing Template

Create `test_example_notebook.py`:

```python
import unittest
import numpy as np
from example_notebook_lib import *

class TestExampleNotebook(unittest.TestCase):
    
    def test_mathematical_function(self):
        """Test core mathematical function."""
        # Add specific test cases
        pass
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Add edge case tests
        pass
    
    def test_mathematical_properties(self):
        """Test mathematical properties like periodicity, symmetry.""" 
        # Add property tests
        pass

if __name__ == '__main__':
    unittest.main()
```

## Integration Checklist

When creating a new notebook:

- [ ] Follow the 4-file architecture pattern
- [ ] Include comprehensive mathematical documentation
- [ ] Implement proper error handling and validation
- [ ] Add interactive parameter controls with meaningful ranges
- [ ] Create visualization with clear labels and legends
- [ ] Write unit tests for mathematical functions
- [ ] Ensure browser compatibility (Pyodide-compatible code)
- [ ] Add to main repository index/navigation
- [ ] Follow branch naming convention: `feature-descriptive-name`