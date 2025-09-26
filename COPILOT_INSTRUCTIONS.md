# Copilot Instructions for Notebooks Repository

## Repository Overview

This is a **random collection of Python notebooks** for mathematical explorations, visualizations, and interactive experiments. Each notebook should be self-contained and focused on a specific mathematical concept, algorithm, or visualization technique.

## Branch Naming Convention

**MANDATORY**: All Copilot branches MUST follow the pattern:

```
feature-descriptive-name
```

### Examples:
- `feature-weierstrass-playground`
- `feature-mandelbrot-explorer` 
- `feature-fourier-analysis`
- `feature-neural-network-viz`
- `feature-prime-spirals`

### ❌ Invalid branch names:
- `copilot/fix-xyz-123-456`
- `main`
- `fix-bug`
- `update-notebook`

## Code Architecture Guidelines

### 1. Separation of Concerns
- **Notebooks** should contain ONLY minimal imports and calls to UI modules
- **Mathematical/computational logic** should be extracted to `{notebook_name}_lib.py` modules  
- **UI code** should be extracted to `{notebook_name}_ui.py` modules
- Create three separate files for each major notebook

### 2. File Structure
```python
# Example structure for a notebook called "chaos_game":

# chaos_game.ipynb - MINIMAL notebook (3-4 cells max)
"""
Ultra-minimal notebook with just:
- Import preamble, lib, and ui modules
- Call setup from preamble
- Display UI
- Display output widget
"""

# chaos_game_preamble.py - Documentation and setup
"""
Contains:
- Comprehensive documentation and mathematical background
- Module docstring with detailed explanations  
- setup_environment() function for configuration
- get_help() function for user guidance
- All verbose explanations moved from notebook
"""

# chaos_game_lib.py - Mathematical/computational logic
"""
All mathematical functions and algorithms:
- Core computation functions
- Integration/simulation methods
- Data processing utilities
- Visualization helpers (backgrounds, contours, etc.)
"""

# chaos_game_ui.py - UI components and layout
"""
All UI widgets and interaction logic:
- Widget creation and configuration
- Layout and styling
- Event handlers that call lib functions
- Help button linking to preamble.get_help()
- Parameter validation
- File I/O operations
"""
```

### 3. Four-File Architecture Pattern
```python
# notebook_name.ipynb (ULTRA-MINIMAL)
from notebook_name_preamble import setup_environment
from notebook_name_lib import *
from notebook_name_ui import create_ui

setup_environment()

# notebook_name_preamble.py  
def setup_environment(): ...
def get_help(): ...
# Comprehensive documentation in module docstring

# notebook_name_lib.py
def mathematical_function(): ...
def visualization_function(): ...

# notebook_name_ui.py  
class UI:
    def show_help(self): 
        from notebook_name_preamble import get_help
        get_help()
ui.display()
display(ui.get_output_widget())

# notebook_name_lib.py  
def core_mathematical_function():
    """Core computation logic"""
    pass

def visualization_helper():
    """Visualization utilities"""
    pass

# notebook_name_ui.py
class NotebookUI:
    def __init__(self):
        self._create_widgets()
        self._setup_layout()
    
    def display(self):
        display(self.ui)
        
def create_ui():
    return NotebookUI()
```

## Quality Standards

### Documentation
- Each notebook must have a clear title and description
- Include mathematical background where relevant
- Provide usage instructions
- Add tips for interesting parameter values

### User Experience
- Controls should be intuitive and well-organized
- Include clear usage instructions at the top
- Provide meaningful error messages
- Add progress indicators for long computations

### Code Quality
- Extract complex logic to separate modules
- Use meaningful function and variable names
- Include docstrings for all functions
- Handle edge cases gracefully

## File Organization

```
repository-root/
├── notebook_name.ipynb          # MINIMAL notebook (imports + UI display only)
├── notebook_name_lib.py         # Mathematical/computational logic
├── notebook_name_ui.py          # UI widgets and layout code
├── test_notebook_name.py        # Optional: tests for library functions
├── requirements.txt             # Dependencies
└── README.md                    # Repository overview
```

## Dependencies

### Standard Stack
- `numpy` - Numerical computations
- `matplotlib` - Plotting and visualization  

### Additional Libraries (as needed)
- `scipy` - Scientific computing
- `sympy` - Symbolic mathematics
- `plotly` - Interactive plots
- `PIL/Pillow` - Image processing

## Commit Guidelines

### Commit Messages
- Use descriptive commit messages
- Reference issue numbers when applicable
- Example: `Add three-panel mode for Weierstrass playground`

### Progress Reporting
- Use `report_progress` tool frequently during development
- Update PR descriptions with checklists showing progress
- Commit working increments rather than large monolithic changes

## Testing

### Manual Testing
- Test all interactive controls
- Verify mathematical correctness with known cases
- Check edge cases and error handling
- Ensure notebook runs from top to bottom without errors

### Automated Testing (Optional)
- Create test files for library functions
- Validate mathematical computations
- Test visualization pipeline

## Example Workflow

1. **Create branch**: `feature-chaos-game`
2. **Plan implementation**:
   - Main notebook: `chaos_game.ipynb`
   - Library: `chaos_game_lib.py`
   - Functions: `iterate_chaos_game()`, `plot_attractor()`, etc.
3. **Develop iteratively**:
   - Implement core math in library
   - Create notebook UI
   - Test and refine
4. **Document and polish**:
   - Add clear instructions
   - Include interesting examples
   - Optimize performance

## Repository Goals

### Primary Objectives
- **Educational**: Help others learn mathematical concepts through interaction
- **Exploratory**: Enable experimentation with parameters and visualizations
- **Reusable**: Create modular code that can be adapted for other projects

### Secondary Objectives  
- **Performance**: Efficient computation for real-time interaction
- **Aesthetics**: Beautiful, publication-quality visualizations
- **Robustness**: Handle edge cases and provide helpful error messages

## Review Criteria

Before submitting:
- [ ] Branch name follows `feature-*` pattern
- [ ] Mathematical logic extracted to separate module
- [ ] Notebook runs completely from top to bottom
- [ ] UI controls are intuitive and well-organized
- [ ] Documentation is clear and helpful
- [ ] Error handling is robust
- [ ] Code is well-structured and documented