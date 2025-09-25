# Weierstrass ℘ Playground

Interactive visualization of the Weierstrass ℘ function with particle trajectory dynamics, available in two versions:

## 🌐 Browser Playground (Recommended)

**Run entirely in your browser - no installation required!**

**🚀 Try it now: [https://litlfred.github.io/notebooks/](https://litlfred.github.io/notebooks/)**

- **Zero setup**: Works immediately in any modern web browser
- **Powered by Pyodide**: Full Python + NumPy + Matplotlib running via WebAssembly
- **Mobile friendly**: Responsive design works on phones and tablets
- **Offline capable**: After initial load, works without internet

### Features
- Interactive parameter controls with real-time feedback
- Two-panel visualization: ℘(z) and ℘′(z) fields with color mapping
- Particle trajectory integration following z''(t) = -℘(z(t)) * z(t)
- Lattice trajectory visualization option
- PNG export functionality
- Comprehensive help system

## 📔 Jupyter Notebook Version

Traditional Jupyter notebook with ipywidgets interface (from PR #2).

### Setup
1. Install dependencies:
   ```bash
   pip install numpy matplotlib ipywidgets
   ```

2. Enable Jupyter widgets:
   ```bash
   jupyter nbextension enable --py widgetsnbextension --sys-prefix
   ```

3. Run the notebook:
   ```bash
   jupyter notebook weierstrass_playground.ipynb
   ```

### Features
- **Multiple visualization modes**: Two-panel, three-panel, and five-panel layouts
- **Advanced controls**: Full parameter customization with sliders and inputs
- **High-resolution export**: 600 DPI PNG output capability
- **Modular architecture**: Separated into lib, ui, and preamble modules

## Mathematical Background

The Weierstrass ℘ function is implemented using a truncated lattice sum:

℘(z) = 1/z² + Σ[1/(z-ω)² - 1/ω²]

where the sum runs over non-zero lattice points ω ∈ Λ = ℤp + ℤiq within truncation bound N.

**Particle trajectories** follow the second-order differential equation:
**z''(t) = -℘(z(t)) * z(t)**

Integration uses RK4 method with automatic blow-up detection near poles.

## Quick Start Examples

### Browser Version
1. Visit https://litlfred.github.io/notebooks/
2. Wait for libraries to load (~30 seconds first time)
3. Try default settings: p=11, q=5, N=3
4. Click "Render" to generate visualization
5. Experiment with different particles: z₀ = `5+2j`, v₀ = `0+1j`

### Jupyter Version  
1. Open `weierstrass_playground.ipynb`
2. Run all cells from top to bottom
3. Use interactive controls at the bottom
4. Try different visualization modes and particle configurations

## Performance Notes

**Browser version**: Keep grid resolution ≤150 and N≤4 for responsive interaction  
**Jupyter version**: Can handle higher resolution (300×300) and N≤6 with more computational resources

## Repository Structure

```
├── docs/                          # Browser playground (GitHub Pages)
│   ├── index.html                # Main web interface  
│   ├── css/style.css            # Styling
│   ├── js/weierstrass-app.js    # JavaScript application
│   ├── python/weierstrass_core.py  # Python math library for Pyodide
│   └── README.md                # Detailed browser version docs
├── weierstrass_playground.ipynb  # Main Jupyter notebook (minimal)
├── weierstrass_lib.py           # Mathematical functions library  
├── weierstrass_ui.py            # Jupyter UI components
├── weierstrass_preamble.py      # Setup and documentation
└── requirements.txt             # Python dependencies for Jupyter version
```

## Dependencies

**Browser version**: None (libraries loaded automatically via CDN)
**Jupyter version**: `numpy`, `matplotlib`, `ipywidgets`

## Development

See `docs/README.md` for detailed development instructions for the browser version.

For local development of the browser version:
```bash
cd docs
python -m http.server 8000
# Visit http://localhost:8000
```