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
├── docs/                          # Browser playground (GitHub Pages)
│   ├── index.html                # Main web interface  
│   ├── css/style.css            # Styling
│   ├── js/weierstrass-app.js    # JavaScript application
│   ├── python/weierstrass_core.py  # Python math library for Pyodide
│   └── README.md                # Detailed development docs
├── weierstrass_lib.py           # Mathematical functions library  
├── weierstrass_ui.py            # UI components
├── weierstrass_preamble.py      # Setup and documentation
├── weierstrass_playground.ipynb  # Jupyter notebook version
└── requirements.txt             # Python dependencies
```

## Common Framework

The playground uses a modular architecture where each "page" acts like a Jupyter notebook:
- **Math library components**: Core mathematical functions
- **UI components**: Interactive controls and visualization
- **Page structure**: Similar to notebook cells but browser-native

## Development

See `docs/README.md` for detailed development instructions.

For local development:
```bash
cd docs
python -m http.server 8000
# Visit http://localhost:8000
```
