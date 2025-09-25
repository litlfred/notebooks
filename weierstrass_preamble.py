"""
Weierstrass ℘ Playground — Interactive Trajectory Visualization

This module provides setup information and documentation for the Weierstrass playground notebook.

## Overview

This notebook visualizes complex fields derived from the Weierstrass ℘ function on a rectangular 
lattice and overlays shared second-order trajectories. 

## Features

- **Two-panel mode**: ℘(z) and ℘′(z) with color mapping
- **Three-panel mode**: ℘(z), Re(℘′(z)), and Im(℘′(z)) with grayscale backgrounds  
- **Five-panel mode**: ℘(z), ℘′(z), complex plane, Re(℘(z)), and Im(℘(z))
- **Interactive trajectories**: Follow the second-order ODE z''(t) = -℘(z(t)) z(t)
- **Arbitrary precision**: dt can be any positive number (e.g., 1e-5)
- **High-resolution export**: 600 DPI PNG output
- **Blow-up detection**: Automatic termination with 💥 markers near poles

## Architecture

The implementation uses a clean three-file modular architecture:
- `weierstrass_playground.ipynb` - Minimal notebook with UI display
- `weierstrass_lib.py` - All mathematical computations and visualization functions  
- `weierstrass_ui.py` - All UI widgets, layouts, and event handling
- `weierstrass_preamble.py` - Setup information and documentation (this file)

## Mathematical Background

The Weierstrass ℘ function is implemented using a truncated symmetric lattice sum:
℘(z) = 1/z² + Σ[1/(z-ω)² - 1/ω²] for ω ∈ Λ\\{0}

where Λ = ℤp + ℤiq is the rectangular lattice.

Trajectories follow the second-order differential equation:
z''(t) = -℘(z(t)) * z(t)

with user-specified initial conditions z(0) and z'(0).

## Usage Instructions

1. Run all cells in order (Cell → Run All) or use Shift+Enter for each cell
2. Use the interactive controls to:
   - Select visualization mode (two-panel, three-panel, or five-panel)  
   - Adjust lattice parameters (p, q, N)
   - Set integration parameters (dt, T, blow-up threshold)
   - Add/remove particles with custom initial conditions
   - Configure rendering options (grid resolution, contours, vectors, palette)
3. Click "Render" to generate visualizations
4. Use "Save High-Res PNG" for publication-quality output

## Default Particles

The notebook initializes with three particles designed for interesting trajectories:
- Particle 1: z = 5.5, z' = i
- Particle 2: z = 5.0, z' = i  
- Particle 3: z = 7.0, z' = 0

## Dependencies

- numpy: Numerical computations
- matplotlib: Plotting and visualization
- ipywidgets: Interactive controls (requires: jupyter nbextension enable --py widgetsnbextension)
"""

def setup_environment():
    """Configure the matplotlib environment for optimal display."""
    try:
        import warnings
        import numpy as np
        import matplotlib.pyplot as plt
        
        warnings.filterwarnings('ignore')
        
        # Set matplotlib to inline mode (in notebook context)
        try:
            from IPython import get_ipython
            ipython = get_ipython()
            if ipython:
                ipython.run_line_magic('matplotlib', 'inline')
        except ImportError:
            pass
        
        # Configure matplotlib for high quality plots
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        
        print("Weierstrass ℘ Playground initialized successfully!")
        print("Three visualization modes available: two-panel, three-panel, five-panel")
        print("Run the next cell to display interactive controls.")
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please install required dependencies: pip install numpy matplotlib ipywidgets")

def get_help():
    """Display help information about the playground."""
    help_text = """
    WEIERSTRASS ℘ PLAYGROUND HELP
    
    Visualization Modes:
    • Two-panel: ℘(z) and ℘′(z) with color mapping
    • Three-panel: ℘(z), Re(℘′(z)), Im(℘′(z)) with grayscale  
    • Five-panel: Comprehensive view with all components
    
    Key Parameters:
    • p, q: Lattice periods (default: 11, 5)
    • N: Truncation level (0-6, higher = more accurate)  
    • dt: Integration step size (can use scientific notation)
    • T: Total simulation time
    
    Tips:
    • Use higher N for more accurate ℘ function (slower)
    • Smaller dt gives more precise trajectories
    • 💥 marks indicate trajectory blow-ups near poles
    • Try different particle initial conditions for varied dynamics
    """
    print(help_text)