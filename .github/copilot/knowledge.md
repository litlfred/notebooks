# Knowledge Base for Mathematical Notebooks Repository

## Repository Overview

This repository contains interactive Python mathematical notebooks focused on complex analysis and visualization, specifically featuring the Weierstrass ℘ (elliptic) function playground.

## Key Architecture Components

### Core Technologies
- **Python**: Mathematical computations using NumPy and Matplotlib
- **Pyodide**: Browser-based Python execution via WebAssembly
- **GitHub Pages**: Static hosting with Jekyll integration
- **Interactive Widgets**: Mathematical visualizations and parameter controls

### Repository Structure
```
notebooks/
├── docs/                          # GitHub Pages source
│   ├── weierstrass-playground/    # Interactive playground
│   ├── _layouts/default.html      # Jekyll template
│   └── index.md                   # Landing page
├── src/weierstrass_playground/    # Python package
│   ├── core.py                    # Mathematical functions
│   ├── visualization.py           # Plotting utilities
│   ├── integration.py             # Trajectory computation
│   └── browser.py                 # Pyodide adaptations
├── legacy/                        # Old Jupyter notebooks
└── COPILOT_INSTRUCTIONS.md        # Development guidelines
```

## Mathematical Domain Knowledge

### Weierstrass ℘ Function
The Weierstrass elliptic function ℘(z) is defined by:
```
℘(z) = 1/z² + Σ[(1/(z-ω)² - 1/ω²)]
```
where the sum is over all non-zero lattice points ω.

### Key Features
- **Lattice Structure**: Rectangular lattice Λ = ℤp + ℤiq
- **Periodicity**: ℘(z + ω) = ℘(z) for all ω ∈ Λ
- **Poles**: Second-order poles at lattice points
- **Trajectory Integration**: Second-order ODE: z''(t) = -℘(z(t))·z(t)

## Development Guidelines

### File Organization Pattern
Each major notebook follows a 4-file architecture:
1. `notebook_name.ipynb` - Minimal notebook (3-4 cells max)
2. `notebook_name_preamble.py` - Documentation and setup
3. `notebook_name_lib.py` - Mathematical/computational logic
4. `notebook_name_ui.py` - UI widgets and layout

### Testing Strategy
- Mathematical correctness tests in `test_weierstrass.py`
- Visualization tests in `test_visualization.py`
- Browser compatibility tests in `test_browser_playground.py`
- CI/CD via GitHub Actions (quality-check.yml, deploy.yml)

### Deployment Process
1. **Development**: Local testing with Python/Jupyter
2. **Browser Adaptation**: Pyodide compatibility layer
3. **Static Generation**: Jekyll builds for GitHub Pages
4. **Quality Gates**: Mathematical tests + frontend validation
5. **Deployment**: Automatic deployment to https://litlfred.github.io/notebooks/

## Common Issues and Solutions

### Mathematical Precision
- Use truncated lattice sums (parameter N) for performance
- Handle pole singularities with epsilon thresholds
- Implement blow-up detection for trajectory integration

### Browser Compatibility
- All Python code must work with Pyodide
- Use matplotlib for plotting (compatible with Pyodide)
- Memory management important for long-running calculations

### Performance Optimization
- Grid computations can be expensive - use reasonable resolutions
- Trajectory integration should have configurable step sizes
- Background color generation benefits from vectorization

## Extension Points

### Adding New Notebooks
1. Follow 4-file architecture pattern
2. Extract mathematical logic to separate modules
3. Create browser-compatible version in `docs/`
4. Add tests for mathematical functions
5. Update main index with navigation links

### Mathematical Extensions
- Other elliptic functions (ζ, σ)
- Different lattice types (triangular, hexagonal)
- Additional integration schemes
- Interactive parameter exploration widgets