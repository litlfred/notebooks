# Weierstrass ℘ Playground

This repository contains an interactive Jupyter notebook that visualizes complex fields derived from the Weierstrass ℘ function on a rectangular lattice and overlays shared second-order trajectories.

## Features

- **Two-panel visualization**:
  - Left panel: ℘(z) field
  - Right panel: ℘′(z) field
- **Interactive trajectories** following the second-order ODE: z''(t) = -℘(z(t)) z(t)
- **Comprehensive controls**:
  - Lattice parameters (p, q, truncation N)
  - Rendering options (grid resolution, contours, vector fields)
  - Color palette customization
  - Integration parameters
  - Dynamic particle management

## Getting Started

1. Install required dependencies:
   ```bash
   pip install numpy matplotlib ipywidgets
   ```

2. Enable Jupyter widgets (for classic Jupyter):
   ```bash
   jupyter nbextension enable --py widgetsnbextension --sys-prefix
   ```

3. Open the notebook:
   ```bash
   jupyter notebook weierstrass_playground.ipynb
   ```

4. Run all cells and interact with the controls at the bottom.

## Usage

1. **Set lattice parameters**: Adjust p, q (lattice periods) and N (truncation level)
2. **Configure rendering**: Set grid resolution, contour levels, and vector field display
3. **Add particles**: Define initial positions (z0) and velocities (v0) for trajectories
4. **Integrate**: Set time step (dt) and duration (T) for trajectory integration
5. **Render**: Click the "Render" button to generate the visualization
6. **Save**: Use "Save PNG" to export the current figure

## Mathematical Background

The Weierstrass ℘ function is implemented using a truncated lattice sum for rectangular lattice Λ = ℤp + ℤiq:

℘(z) = 1/z² + Σ[1/(z-ω)² - 1/ω²]

where the sum runs over non-zero lattice points ω within the truncation bound N.

Trajectories are integrated using RK4 method with blow-up detection near poles and for large step sizes.

## Examples

- Default settings (p=11, q=5, N=3) provide a good starting point
- Try different initial conditions for varied trajectory patterns
- Increase N for higher accuracy (but slower computation)
- Experiment with different lattice aspect ratios

## Dependencies

- `numpy`: Numerical computations
- `matplotlib`: Visualization
- `ipywidgets`: Interactive controls