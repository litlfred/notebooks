"""
Visualization Functions for Weierstrass ℘ Function

This module contains functions for creating visual representations:
- Color mapping for complex fields
- Background generation (soft color, grayscale)  
- Contour and vector overlays
- Figure creation and layout
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors
import warnings
warnings.filterwarnings('ignore')


def soft_background(F, M, sat=0.2, mag_scale=0.8, value_floor=0.4):
    """
    Create soft color palette RGB image for complex fields.
    
    Maps complex field values to HSV colors where:
    - Hue represents argument/phase
    - Saturation is constant (soft appearance)
    - Value/brightness represents magnitude with compression
    
    Args:
        F: complex field values (2D array)
        M: valid mask (2D boolean array)
        sat: saturation level (0-1, lower = softer colors)
        mag_scale: magnitude scaling factor
        value_floor: minimum brightness (0-1, higher = brighter)
    
    Returns:
        RGB image array with shape (height, width, 3)
    """
    # Hue from argument/phase
    H = np.angle(F) / (2 * np.pi) + 0.5  # Map to [0, 1]
    H = H % 1.0
    
    # Brightness from magnitude with compression
    mag = np.abs(F) * mag_scale
    V = np.arctan(mag) / (np.pi / 2)  # Compress to [0, 1] using arctan
    V = value_floor + (1 - value_floor) * V  # Raise floor
    
    # Constant saturation for soft appearance
    S = np.full_like(H, sat)
    
    # Convert HSV to RGB
    HSV = np.stack([H, S, V], axis=-1)
    RGB = mcolors.hsv_to_rgb(HSV)
    
    # Apply mask (set invalid regions to white)
    RGB = np.where(M[..., np.newaxis], RGB, 1.0)
    
    return np.clip(RGB, 0, 1)


def grayscale_background(F, M, value_floor=0.1):
    """
    Create grayscale background for real-valued fields.
    
    Useful for visualizing Re(℘'(z)) or Im(℘'(z)) components.
    
    Args:
        F: real field values (2D array)
        M: valid mask (2D boolean array)  
        value_floor: minimum brightness (0-1)
    
    Returns:
        RGB grayscale image array with shape (height, width, 3)
    """
    # Normalize to [value_floor, 1]
    F_finite = F[M & np.isfinite(F)]
    if len(F_finite) > 0:
        vmin, vmax = np.min(F_finite), np.max(F_finite)
        if vmax > vmin:
            V = (F - vmin) / (vmax - vmin)
        else:
            V = np.ones_like(F) * 0.5
    else:
        V = np.ones_like(F) * 0.5
    
    V = value_floor + (1 - value_floor) * V
    
    # Create grayscale RGB
    RGB = np.stack([V, V, V], axis=-1)
    
    # Apply mask (set invalid regions to white)
    RGB = np.where(M[..., np.newaxis], RGB, 1.0)
    
    return np.clip(RGB, 0, 1)


def add_topo_contours(ax, X, Y, F, M, n_contours=10):
    """
    Add topographic contours of |F| to plot.
    
    Creates logarithmically spaced contour lines showing field magnitude.
    
    Args:
        ax: matplotlib axis to add contours to
        X, Y: coordinate grids  
        F: complex field values
        M: valid mask
        n_contours: number of contour levels
    """
    if n_contours <= 0:
        return
    
    mag = np.abs(F)
    mag = np.where(M, mag, np.nan)
    
    if np.all(np.isnan(mag)):
        return
    
    # Use log scale for better contour distribution
    with np.errstate(divide='ignore', invalid='ignore'):
        log_mag = np.log10(mag + 1e-10)
    
    finite_mask = np.isfinite(log_mag)
    if not np.any(finite_mask):
        return
    
    vmin, vmax = np.nanmin(log_mag), np.nanmax(log_mag)
    if vmin == vmax:
        return
    
    levels = np.linspace(vmin, vmax, n_contours)
    ax.contour(X, Y, log_mag, levels=levels, colors='black', alpha=0.3, linewidths=0.5)


def vector_overlay(ax, X, Y, F, M, density=20, width=0.002, max_len=0.5):
    """
    Add vector field overlay with magnitude compression.
    
    Shows field direction as arrows with compressed magnitudes for visibility.
    
    Args:
        ax: matplotlib axis to add vectors to
        X, Y: coordinate grids
        F: complex field values  
        M: valid mask
        density: vector sampling density (higher = more arrows)
        width: arrow width
        max_len: maximum arrow length (clips longer arrows)
    """
    if density <= 0:
        return
    
    # Subsample grid for vector display
    ny, nx = X.shape
    step_x = max(1, nx // density)
    step_y = max(1, ny // density)
    
    X_sub = X[::step_y, ::step_x]
    Y_sub = Y[::step_y, ::step_x]
    F_sub = F[::step_y, ::step_x]
    M_sub = M[::step_y, ::step_x]
    
    # Vector components with magnitude compression
    mag = np.abs(F_sub)
    max_mag = np.nanmax(mag)
    if max_mag > 0:
        # Compress magnitude using tanh for better visibility
        compressed_mag = np.tanh(mag / max_mag * 2)
        
        # Normalize and scale by compressed magnitude
        U = np.real(F_sub / mag * compressed_mag)
        V = np.imag(F_sub / mag * compressed_mag)
    else:
        U = np.real(F_sub)
        V = np.imag(F_sub)
    
    # Apply mask and length filter
    arrow_len = np.sqrt(U**2 + V**2)
    valid = M_sub & np.isfinite(U) & np.isfinite(V) & (arrow_len <= max_len)
    
    if np.any(valid):
        ax.quiver(X_sub[valid], Y_sub[valid], U[valid], V[valid], 
                 scale_units='xy', scale=1, width=width, alpha=0.7, color='darkblue')


def create_figure_layout(mode, p, q, figsize_base=8):
    """
    Create figure and axes layout based on visualization mode.
    
    Args:
        mode: visualization mode ('two_panel', 'three_panel', 'five_panel', 'time_series')
        p, q: lattice parameters for axis limits
        figsize_base: base figure size
        
    Returns:
        fig, axes: matplotlib figure and axes tuple
    """
    if mode == 'two_panel':
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(2*figsize_base, figsize_base))
        fig.subplots_adjust(wspace=0.0)
        
        # Set labels and limits
        ax1.set_title('℘(z)', fontsize=16)
        ax2.set_title("℘'(z)", fontsize=16)
        ax1.set_xlabel('Re(z)')
        ax1.set_ylabel('Im(z)')
        ax2.set_xlabel('Re(z)')
        ax2.set_ylabel('')
        
        for ax in [ax1, ax2]:
            ax.set_xlim(0, p)
            ax.set_ylim(0, q)
        ax2.set_yticks([])
        
        return fig, (ax1, ax2)
        
    elif mode == 'three_panel':
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(3*figsize_base, figsize_base))
        fig.subplots_adjust(wspace=0.0)
        
        # Set labels and limits  
        ax1.set_title('℘(z)', fontsize=16)
        ax2.set_title("Re(℘'(z))", fontsize=16)
        ax3.set_title("Im(℘'(z))", fontsize=16)
        
        ax1.set_xlabel('Re(z)')
        ax1.set_ylabel('Im(z)')
        ax2.set_xlabel('Re(z)')
        ax2.set_ylabel('')
        ax3.set_xlabel('Re(z)')
        ax3.set_ylabel('')
        
        for ax in [ax1, ax2, ax3]:
            ax.set_xlim(0, p)
            ax.set_ylim(0, q)
        ax2.set_yticks([])
        ax3.set_yticks([])
        
        return fig, (ax1, ax2, ax3)
        
    else:  # Default to two_panel
        return create_figure_layout('two_panel', p, q, figsize_base)


def plot_to_base64(fig):
    """
    Convert matplotlib figure to base64 string for web display.
    
    Useful for browser-based applications using Pyodide.
    
    Args:
        fig: matplotlib figure
        
    Returns:
        base64 encoded PNG image string
    """
    import io
    import base64
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white', dpi=150)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)  # Free memory
    return img_str


def save_high_resolution(fig, filename='weierstrass_viz.png', dpi=300):
    """
    Save figure at high resolution.
    
    Args:
        fig: matplotlib figure
        filename: output filename  
        dpi: resolution in dots per inch
        
    Returns:
        filename: the saved filename
    """
    fig.savefig(filename, dpi=dpi, bbox_inches='tight', facecolor='white')
    return filename