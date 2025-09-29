"""
Weierstrass ℘ Function Mathematical Core
Migrated from legacy weierstrass_lib.py for use in the modern widget system.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# Core Mathematical Functions
def wp_rect(z, p, q, N):
    """
    Weierstrass ℘ function for rectangular lattice Λ = Zp + Ziq
    using truncated symmetric lattice sum.
    
    Args:
        z: complex number or array
        p, q: real lattice parameters
        N: truncation parameter (sum from -N to N)
    
    Returns:
        ℘(z) values
    """
    z = np.asarray(z, dtype=complex)
    result = np.zeros_like(z, dtype=complex)
    
    # Main term: 1/z^2
    with np.errstate(divide='ignore', invalid='ignore'):
        result += 1.0 / (z**2)
    
    # Lattice sum (excluding origin)
    for m in range(-N, N+1):
        for n in range(-N, N+1):
            if m == 0 and n == 0:
                continue
            
            omega = m * p + n * 1j * q
            with np.errstate(divide='ignore', invalid='ignore'):
                term = 1.0 / (z - omega)**2 - 1.0 / omega**2
                result += term
    
    return result


def wp_deriv(z, p, q, N):
    """
    Derivative of Weierstrass ℘ function: ℘'(z) = -2 * sum(1/(z-ω)^3)
    
    Args:
        z: complex number or array
        p, q: real lattice parameters
        N: truncation parameter
    
    Returns:
        ℘'(z) values
    """
    z = np.asarray(z, dtype=complex)
    result = np.zeros_like(z, dtype=complex)
    
    # Main term: -2/z^3
    with np.errstate(divide='ignore', invalid='ignore'):
        result += -2.0 / (z**3)
    
    # Lattice sum (excluding origin)
    for m in range(-N, N+1):
        for n in range(-N, N+1):
            if m == 0 and n == 0:
                continue
            
            omega = m * p + n * 1j * q
            with np.errstate(divide='ignore', invalid='ignore'):
                term = -2.0 / (z - omega)**3
                result += term
    
    return result


def field_grid(p, q, function_type, N, nx, ny):
    """
    Compute Weierstrass function on a grid
    
    Args:
        p, q: lattice parameters
        function_type: 'wp' or 'wp_deriv'
        N: truncation parameter
        nx, ny: grid dimensions
    
    Returns:
        X, Y: meshgrid coordinates
        F: function values
        M: magnitude array for masking
    """
    # Create coordinate grid
    x = np.linspace(0.01, p - 0.01, nx)
    y = np.linspace(0.01, q - 0.01, ny)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    # Compute function
    if function_type == 'wp':
        F = wp_rect(Z, p, q, N)
    elif function_type == 'wp_deriv':
        F = wp_deriv(Z, p, q, N)
    else:
        raise ValueError(f"Unknown function type: {function_type}")
    
    # Compute magnitude for masking
    M = np.abs(F)
    
    return X, Y, F, M


def soft_background(F, M, saturation, mag_scale, value_floor):
    """
    Create soft colored background from complex function values
    
    Args:
        F: complex function values
        M: magnitude values
        saturation: color saturation level
        mag_scale: magnitude scaling factor
        value_floor: minimum value level
    
    Returns:
        RGB array for display
    """
    # Phase to hue mapping
    phase = np.angle(F)
    hue = (phase + np.pi) / (2 * np.pi)
    
    # Magnitude to value/saturation
    normalized_mag = np.tanh(M / mag_scale)
    value = value_floor + (1 - value_floor) * normalized_mag
    sat = saturation * np.ones_like(hue)
    
    # Convert HSV to RGB
    hsv = np.stack([hue, sat, value], axis=-1)
    rgb = mcolors.hsv_to_rgb(hsv)
    
    return rgb


def grayscale_background(values, M, value_floor):
    """
    Create grayscale background from real values
    
    Args:
        values: real-valued array
        M: magnitude for normalization
        value_floor: minimum value level
    
    Returns:
        Grayscale array for display
    """
    # Normalize values
    max_val = np.nanmax(np.abs(values))
    if max_val > 0:
        normalized = values / max_val
    else:
        normalized = values
    
    # Map to grayscale
    gray = 0.5 + 0.5 * normalized
    gray = np.clip(gray, value_floor, 1.0)
    
    return gray


def add_topo_contours(ax, X, Y, F, M, n_contours):
    """
    Add topographic contours to plot
    
    Args:
        ax: matplotlib axis
        X, Y: coordinate grids
        F: function values
        M: magnitude values for masking
        n_contours: number of contour levels
    """
    if n_contours <= 0:
        return
    
    # Mask extreme values
    mask_threshold = np.percentile(M[np.isfinite(M)], 95)
    F_masked = np.where(M > mask_threshold, np.nan, F)
    
    # Real part contours
    real_levels = np.linspace(np.nanmin(np.real(F_masked)), 
                             np.nanmax(np.real(F_masked)), 
                             n_contours)
    ax.contour(X, Y, np.real(F_masked), levels=real_levels, 
               colors='white', alpha=0.3, linewidths=0.5)
    
    # Imaginary part contours  
    imag_levels = np.linspace(np.nanmin(np.imag(F_masked)), 
                             np.nanmax(np.imag(F_masked)), 
                             n_contours)
    ax.contour(X, Y, np.imag(F_masked), levels=imag_levels, 
               colors='yellow', alpha=0.3, linewidths=0.5, linestyles='--')


def create_two_panel_figure(p, q):
    """Create two-panel figure layout"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.set_title('℘(z)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Re(z)')
    ax1.set_ylabel('Im(z)')
    ax1.set_xlim(0, p)
    ax1.set_ylim(0, q)
    ax1.set_aspect('equal')
    
    ax2.set_title('℘′(z)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Re(z)')
    ax2.set_ylabel('Im(z)')
    ax2.set_xlim(0, p)
    ax2.set_ylim(0, q)
    ax2.set_aspect('equal')
    
    plt.tight_layout()
    return fig, (ax1, ax2)


def create_three_panel_figure(p, q):
    """Create three-panel figure layout"""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
    
    ax1.set_title('℘(z)', fontsize=14, fontweight='bold')
    ax2.set_title('Re(℘′(z))', fontsize=14, fontweight='bold')
    ax3.set_title('Im(℘′(z))', fontsize=14, fontweight='bold')
    
    for ax in (ax1, ax2, ax3):
        ax.set_xlabel('Re(z)')
        ax.set_ylabel('Im(z)')
        ax.set_xlim(0, p)
        ax.set_ylim(0, q)
        ax.set_aspect('equal')
    
    plt.tight_layout()
    return fig, (ax1, ax2, ax3)


def create_five_panel_figure(p, q):
    """Create five-panel figure layout"""
    fig = plt.figure(figsize=(20, 12))
    
    # Main ℘(z) plot (larger, top left)
    ax1 = plt.subplot2grid((3, 4), (0, 0), rowspan=2, colspan=2)
    ax1.set_title('℘(z) - Weierstrass Function', fontsize=16, fontweight='bold')
    
    # ℘'(z) (top right)
    ax2 = plt.subplot2grid((3, 4), (0, 2), rowspan=1, colspan=2)
    ax2.set_title('℘′(z) - Derivative', fontsize=14, fontweight='bold')
    
    # Real and imaginary parts (middle row)
    ax3 = plt.subplot2grid((3, 4), (1, 2))
    ax3.set_title('Re(℘(z))', fontsize=12, fontweight='bold')
    
    ax4 = plt.subplot2grid((3, 4), (1, 3))
    ax4.set_title('Im(℘(z))', fontsize=12, fontweight='bold')
    
    # Analysis panel (bottom)
    ax5 = plt.subplot2grid((3, 4), (2, 0), colspan=4)
    ax5.set_title('Mathematical Properties Analysis', fontsize=14, fontweight='bold')
    
    # Set common properties
    for ax in (ax1, ax2, ax3, ax4):
        ax.set_xlabel('Re(z)')
        ax.set_ylabel('Im(z)')
        ax.set_xlim(0, p)
        ax.set_ylim(0, q)
        ax.set_aspect('equal')
    
    plt.tight_layout()
    return fig, (ax1, ax2, ax3, ax4, ax5)