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
- **Notebooks** should contain ONLY UI code and presentation logic
- **Mathematical/computational logic** should be extracted to Python modules/libraries
- Create a `{notebook_name}_lib.py` file for each major notebook

### 2. Library Structure
```python
# Example: weierstrass_lib.py
"""
Mathematical functions for Weierstrass ℘ playground.
Separated from notebook for reusability and maintainability.
"""

def core_mathematical_function():
    """Core computation logic"""
    pass

def visualization_helper():
    """Visualization utilities"""
    pass

def integration_solver():
    """Numerical methods"""
    pass
```

### 3. Notebook Structure
```python
# Notebook should primarily contain:
import notebook_lib
import ipywidgets as widgets

# UI setup
controls = widgets.VBox([...])

# Event handlers that call library functions
def on_render_click():
    result = notebook_lib.compute_something(params)
    notebook_lib.visualize(result)
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
├── notebook_name.ipynb          # Main interactive notebook
├── notebook_name_lib.py         # Mathematical/computational logic
├── test_notebook_name.py        # Optional: tests for library functions
├── requirements.txt             # Dependencies
└── README.md                    # Repository overview
```

## Dependencies

### Standard Stack
- `numpy` - Numerical computations
- `matplotlib` - Plotting and visualization  
- `ipywidgets` - Interactive controls
- `jupyter` - Notebook environment

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