"""
Core Mathematical Functions for Weierstrass ℘ Function

This module contains the fundamental mathematical computations:
- Weierstrass ℘ function evaluation
- Derivative computation
- Field sampling on grids
- Pole detection and masking
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')


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


def wp_and_deriv(z, p, q, N):
    """
    Compute both ℘(z) and ℘'(z) efficiently.
    
    Args:
        z: complex number or array
        p, q: real lattice parameters  
        N: truncation parameter
    
    Returns:
        (wp_val, wp_deriv_val): tuple of ℘(z) and ℘'(z) values
    """
    return wp_rect(z, p, q, N), wp_deriv(z, p, q, N)


def field_grid(p, q, which, N, nx, ny, pole_eps=1e-6):
    """
    Sample field on grid with pole detection.
    
    Args:
        p, q: lattice parameters
        which: 'wp' for ℘(z) or 'wp_deriv' for ℘'(z)
        N: lattice truncation
        nx, ny: grid resolution
        pole_eps: pole detection threshold
    
    Returns:
        X, Y, F, M where F is field values and M is valid mask
    """
    x = np.linspace(0, p, nx)
    y = np.linspace(0, q, ny)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    # Check for poles (lattice points)
    mask = np.ones_like(Z, dtype=bool)
    for m in range(-N, N+1):
        for n in range(-N, N+1):
            omega = m * p + n * 1j * q
            # Wrap omega to fundamental cell
            omega_wrapped = (omega.real % p) + 1j * (omega.imag % q)
            dist = np.abs(Z - omega_wrapped)
            mask &= (dist > pole_eps)
    
    # Compute field
    if which == 'wp':
        F = wp_rect(Z, p, q, N)
    elif which == 'wp_deriv':
        F = wp_deriv(Z, p, q, N)
    else:
        raise ValueError("which must be 'wp' or 'wp_deriv'")
    
    # Apply mask
    F = np.where(mask, F, np.nan)
    
    # Additional validation
    finite_mask = np.isfinite(F)
    mask &= finite_mask
    
    return X, Y, F, mask


# Utility functions for lattice operations
def wrap_point(z, p, q):
    """
    Wrap a point to the fundamental cell [0,p] × [0,q].
    
    Args:
        z: complex number
        p, q: lattice parameters
        
    Returns:
        wrapped complex number
    """
    return (z.real % p) + 1j * (z.imag % q)


def generate_lattice_points(p, q, N):
    """
    Generate lattice points within truncation bound N.
    
    Args:
        p, q: lattice parameters
        N: truncation bound
        
    Returns:
        list of lattice points (complex numbers)
    """
    points = []
    for m in range(-N, N+1):
        for n in range(-N, N+1):
            if m == 0 and n == 0:
                continue
            omega = m * p + n * 1j * q
            points.append(omega)
    return points


def validate_parameters(p, q, N):
    """
    Validate lattice parameters.
    
    Args:
        p, q: lattice parameters (should be positive)
        N: truncation parameter (should be non-negative integer)
        
    Raises:
        ValueError: if parameters are invalid
    """
    if not (isinstance(p, (int, float)) and p > 0):
        raise ValueError(f"p must be positive number, got {p}")
    if not (isinstance(q, (int, float)) and q > 0):
        raise ValueError(f"q must be positive number, got {q}")
    if not (isinstance(N, int) and N >= 0):
        raise ValueError(f"N must be non-negative integer, got {N}")
    if N > 10:
        warnings.warn(f"Large truncation N={N} may be slow", UserWarning)