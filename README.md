# Weierstrass ℘ Playground

**Interactive visualization of the Weierstrass ℘ function running entirely in your browser**

**🚀 [Try it now: https://litlfred.github.io/notebooks/](https://litlfred.github.io/notebooks/)**

- **Zero Installation**: Works immediately in any modern web browser
- **Powered by Pyodide**: Full Python + NumPy + Matplotlib running via WebAssembly
- **Mobile Friendly**: Responsive design works on phones and tablets
- **Dynamic Visualizations**: Re-renders when browser is resized

## Features

- **Interactive parameter controls** with real-time visual feedback
- **Multiple visualization modes**: Two-panel, three-panel, and five-panel layouts
- **Particle trajectory integration** following z''(t) = -℘(z(t)) * z(t)
- **Lattice trajectory visualization** option for exploring periodic structure
- **Dynamic rendering** with visual indicators during re-computation
- **PNG export** functionality for high-quality visualizations
- **Comprehensive help system** with mathematical background

## Mathematical Background

The Weierstrass ℘ function is implemented using a truncated lattice sum:

℘(z) = 1/z² + Σ[1/(z-ω)² - 1/ω²]

where the sum runs over non-zero lattice points ω ∈ Λ = ℤp + ℤiq within truncation bound N.

**Particle trajectories** follow the second-order differential equation:
**z''(t) = -℘(z(t)) * z(t)**

Integration uses RK4 method with automatic blow-up detection near poles.

## Quick Start

1. Visit https://litlfred.github.io/notebooks/
2. Wait for Pyodide to load (~30 seconds first time)
3. Try default settings: p=11, q=5, N=3
4. Click "Render" to generate visualization
5. Experiment with different particles: z₀ = `5+2j`, v₀ = `0+1j`
6. Resize your browser window to see dynamic re-rendering

## Repository Structure

This repository contains a modular framework for mathematical visualizations:

```
├── src/weierstrass_playground/    # Main Python package
│   ├── __init__.py               # Package initialization
│   ├── core.py                   # Core mathematical functions
│   ├── visualization.py          # Visualization and plotting
│   ├── integration.py            # Trajectory integration and ODEs
│   └── browser.py                # Browser-specific adaptations
├── docs/                          # Browser playground (GitHub Pages)
│   ├── index.html                # Main web interface  
│   ├── css/style.css            # Styling
│   ├── js/weierstrass-app.js    # JavaScript application
│   ├── python/weierstrass_playground/  # Browser-compatible package copy
│   └── README.md                # Detailed development docs
├── weierstrass_lib.py           # Legacy library (maintained for compatibility)
├── weierstrass_ui.py            # Legacy UI components
├── weierstrass_preamble.py      # Setup and documentation
├── weierstrass_playground.ipynb  # Jupyter notebook version
├── setup.py & pyproject.toml    # Package configuration
└── requirements.txt             # Dependencies
```

## Common Framework

The playground uses a modular architecture where each "page" acts like a Jupyter notebook:
- **Math library components**: Core mathematical functions (`weierstrass_playground.core`)
- **UI components**: Interactive controls and visualization (`weierstrass_playground.visualization`)
- **Integration components**: Trajectory computation (`weierstrass_playground.integration`)
- **Browser adaptations**: Web-specific functionality (`weierstrass_playground.browser`)

### Package Installation

Install the Python package locally:
```bash
# Development installation
pip install -e .

# Or install from PyPI (when published)
pip install weierstrass-playground
```

### Python Usage

```python
import weierstrass_playground as wp

# Basic function evaluation
z = 2.0 + 1.5j
p, q, N = 11.0, 5.0, 3
wp_val = wp.wp_rect(z, p, q, N)

# Create visualization
fig = wp.browser.create_complete_visualization(
    mode='two_panel', p=p, q=q, N=N, 
    nx=100, ny=100, particles=[(5+0j, 0+1j)], 
    # ... other parameters
)
```

## Development

See `docs/README.md` for detailed development instructions.

For local development:
```bash
cd docs
python -m http.server 8000
# Visit http://localhost:8000
```
