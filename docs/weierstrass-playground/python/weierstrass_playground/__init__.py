"""
Weierstrass ℘ Playground - Python Library Package

A comprehensive library for visualizing and computing the Weierstrass ℘ function
with interactive trajectory integration and field visualization.

Modules:
    - core: Core mathematical functions (Weierstrass ℘ function, derivatives)
    - visualization: Field visualization and background generation  
    - integration: Trajectory integration and ODE solving
    - ui: User interface components and controls
    - browser: Browser-specific adaptations for Pyodide

Usage:
    >>> from weierstrass_playground import core, visualization
    >>> z = 2.0 + 1.5j
    >>> p, q, N = 11.0, 5.0, 3
    >>> wp_val = core.wp_rect(z, p, q, N)
    >>> print(f"℘({z}) = {wp_val}")
"""

__version__ = "1.0.0"
__author__ = "Weierstrass Playground Contributors"

# Import main modules for easy access
from . import core
from . import visualization  
from . import integration
from . import browser

# Common imports for convenience
from .core import wp_rect, wp_deriv, field_grid
from .integration import integrate_second_order_with_blowup
from .visualization import soft_background, add_topo_contours, vector_overlay

__all__ = [
    'core',
    'visualization', 
    'integration',
    'browser',
    'wp_rect',
    'wp_deriv', 
    'field_grid',
    'integrate_second_order_with_blowup',
    'soft_background',
    'add_topo_contours',
    'vector_overlay'
]