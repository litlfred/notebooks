# Weierstrass ℘ Playground - Browser Edition

An interactive mathematical visualization of the Weierstrass ℘ (Weierstrass P) function running entirely in your browser using [Pyodide](https://pyodide.org/). No Python installation, Jupyter notebooks, or server required!

## 🌟 Features

- **Zero Installation**: Runs completely in your browser using WebAssembly
- **Interactive Visualization**: Real-time parameter adjustment and immediate visual feedback
- **Mathematical Accuracy**: Full NumPy/matplotlib computation in the browser
- **Trajectory Integration**: RK4 integration of second-order differential equations
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Offline Capable**: After initial load, works without internet connection

## 🚀 Live Demo

Visit the playground at: **https://litlfred.github.io/notebooks/**

## 📖 Usage

### Getting Started

1. Open the playground in your web browser
2. Wait for Pyodide and mathematical libraries to load (first time takes ~30 seconds)
3. Configure parameters using the control panel
4. Click "Render" to generate visualizations
5. Click "Save PNG" to download your visualizations

### Parameters

#### Lattice Parameters
- **p, q**: Lattice periods defining the rectangular lattice Λ = ℤp + ℤiq
- **N**: Truncation level (0-6). Higher values = more accurate but slower computation

#### Rendering Options  
- **Grid X/Y**: Resolution of the field visualization (50-200)
- **Contours**: Number of topographic contour lines (0-30)
- **Vector Density**: Density of vector field arrows (0-30)
- **Show vector field arrows**: Toggle vector field display

#### Color Palette
- **Saturation**: Color intensity (0-1)
- **Value Floor**: Minimum brightness (0-1) 
- **Magnitude Scale**: Scaling of field magnitude for color mapping

#### Integration & Particles
- **Time Step (dt)**: Integration step size (0.001-0.1)
- **Duration (T)**: Total simulation time (1-30)
- **Show lattice trajectories**: Display systematic trajectories for z=1,2,3...p-1 with z'=i

#### Initial Conditions
Define particles with:
- **z₀**: Initial position (complex number, e.g., `5.5+0j`, `3+2j`)
- **v₀**: Initial velocity (complex number, e.g., `0+1j`, `1-0.5j`)

### Mathematical Background

The playground visualizes the Weierstrass ℘ function:

℘(z) = 1/z² + Σ[1/(z-ω)² - 1/ω²]

where the sum runs over non-zero lattice points ω ∈ Λ = ℤp + ℤiq.

Particle trajectories follow the second-order differential equation:
**z''(t) = -℘(z(t)) * z(t)**

Integration uses the RK4 method with automatic blow-up detection near poles.

### Performance Tips

For best performance in the browser:

- Keep grid resolution moderate (50-150) for real-time interaction
- Use N ≤ 4 for responsive computation
- Reduce particle count for faster rendering
- Higher N values provide more accuracy but require more computation time

## 🛠 Development

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/litlfred/notebooks.git
   cd notebooks
   ```

2. Serve the docs directory locally:
   ```bash
   cd docs
   python -m http.server 8000
   # or use any local web server
   ```

3. Open http://localhost:8000 in your browser

### Project Structure

```
docs/
├── index.html              # Main web interface
├── css/
│   └── style.css          # Styling and responsive design  
├── js/
│   └── weierstrass-app.js # Main application logic & Pyodide integration
└── python/
    └── weierstrass_core.py # Mathematical functions adapted for Pyodide
```

### Architecture

- **Frontend**: Vanilla HTML/CSS/JavaScript with Pyodide integration
- **Python Backend**: Runs in browser via WebAssembly (Pyodide)
- **Dependencies**: NumPy, Matplotlib loaded dynamically via CDN
- **Visualization**: Matplotlib figures converted to base64 PNG for web display

### Deployment to GitHub Pages

The application is designed to deploy seamlessly to GitHub Pages:

1. Ensure all files are in the `docs/` directory
2. Push to GitHub repository
3. Enable GitHub Pages in repository settings
4. Select "Deploy from a branch" → `main` → `/docs`
5. The site will be available at `https://username.github.io/repository-name/`

## 🔧 Customization

### Adding New Visualization Modes

Edit `docs/python/weierstrass_core.py`:

1. Modify `create_figure_with_plots()` function
2. Add new mode handling in the conditional logic
3. Update HTML select options in `index.html`

### Modifying UI Controls

Edit `docs/index.html` and `docs/js/weierstrass-app.js`:

1. Add HTML form controls in `index.html`
2. Update `getParameters()` method in JavaScript
3. Pass new parameters to Python functions

### Styling Changes

Edit `docs/css/style.css`:
- Modify CSS custom properties (`:root` variables) for color themes
- Adjust responsive breakpoints in media queries
- Update component styling as needed

## 📦 Dependencies

### Runtime (automatically loaded)
- [Pyodide](https://pyodide.org/) v0.24.1 - Python in WebAssembly
- NumPy - Numerical computations
- Matplotlib - Plotting and visualization

### Development
- Modern web browser with WebAssembly support
- Local web server for development (Python http.server, Node.js serve, etc.)

## 🧪 Browser Compatibility

- **Chrome/Edge**: Full support
- **Firefox**: Full support  
- **Safari**: Full support (requires recent version for WebAssembly)
- **Mobile browsers**: Responsive design with touch-friendly controls

## 🐛 Troubleshooting

### Slow Initial Loading
- First load requires downloading ~50MB of WebAssembly packages
- Subsequent visits use browser cache and load much faster
- Use browser developer tools to monitor loading progress

### Memory Issues
- Reduce grid resolution and particle count for resource-constrained devices
- Browser may pause computation on background tabs
- Close other browser tabs if experiencing performance issues

### Complex Number Input
- Use format: `5+2j`, `3-1j`, `5`, `2j`
- Spaces are automatically removed
- Invalid formats fall back to `0+0j`

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Pyodide](https://pyodide.org/) team for Python-in-browser technology
- Original Jupyter notebook implementation (PR #2)
- Mathematical foundations from Weierstrass function theory

## 🔗 Links

- **Live Demo**: https://litlfred.github.io/notebooks/
- **Source Code**: https://github.com/litlfred/notebooks
- **Pyodide Documentation**: https://pyodide.org/en/stable/
- **Weierstrass Function**: https://en.wikipedia.org/wiki/Weierstrass_elliptic_function