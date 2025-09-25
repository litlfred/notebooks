#!/usr/bin/env python3
"""
Test visualization functionality of the Weierstrass playground.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def wp_rect(z, p, q, N):
    """Weierstrass ℘ function for rectangular lattice."""
    z = np.asarray(z, dtype=complex)
    result = np.zeros_like(z, dtype=complex)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        result += 1.0 / (z**2)
    
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
    """Derivative of Weierstrass ℘ function."""
    z = np.asarray(z, dtype=complex)
    result = np.zeros_like(z, dtype=complex)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        result += -2.0 / (z**3)
    
    for m in range(-N, N+1):
        for n in range(-N, N+1):
            if m == 0 and n == 0:
                continue
            omega = m * p + n * 1j * q
            with np.errstate(divide='ignore', invalid='ignore'):
                term = -2.0 / (z - omega)**3
                result += term
    
    return result

def soft_background(F, M, sat=0.3, mag_scale=1.0, value_floor=0.3):
    """Create soft color palette RGB image."""
    H = np.angle(F) / (2 * np.pi) + 0.5
    H = H % 1.0
    
    mag = np.abs(F) * mag_scale
    V = np.arctan(mag) / (np.pi / 2)
    V = value_floor + (1 - value_floor) * V
    
    S = np.full_like(H, sat)
    
    HSV = np.stack([H, S, V], axis=-1)
    RGB = mcolors.hsv_to_rgb(HSV)
    
    RGB = np.where(M[..., np.newaxis], RGB, 1.0)
    
    return np.clip(RGB, 0, 1)

def create_test_visualization():
    """Create a test visualization of the Weierstrass fields."""
    print("Creating test visualization...")
    
    # Parameters
    p, q, N = 11.0, 5.0, 2
    nx, ny = 100, 100
    
    # Create grid
    x = np.linspace(0.01, p-0.01, nx)
    y = np.linspace(0.01, q-0.01, ny)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    # Compute fields
    print("Computing ℘(z)...")
    F1 = wp_rect(Z, p, q, N)
    print("Computing ℘'(z)...")
    F2 = wp_deriv(Z, p, q, N)
    
    # Create masks
    M1 = np.isfinite(F1)
    M2 = np.isfinite(F2)
    
    print(f"Valid ℘ points: {np.sum(M1)}/{M1.size}")
    print(f"Valid ℘' points: {np.sum(M2)}/{M2.size}")
    
    # Create backgrounds
    print("Creating backgrounds...")
    bg1 = soft_background(F1, M1)
    bg2 = soft_background(F2, M2)
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Weierstrass ℘ Function Visualization Test', fontsize=16)
    
    # Display backgrounds
    ax1.imshow(bg1, extent=[0, p, 0, q], origin='lower', aspect='equal')
    ax2.imshow(bg2, extent=[0, p, 0, q], origin='lower', aspect='equal')
    
    # Add contours
    print("Adding contours...")
    mag1 = np.abs(F1)
    mag2 = np.abs(F2)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        log_mag1 = np.log10(mag1 + 1e-10)
        log_mag2 = np.log10(mag2 + 1e-10)
    
    if np.any(np.isfinite(log_mag1)):
        levels1 = np.linspace(np.nanmin(log_mag1), np.nanmax(log_mag1), 8)
        ax1.contour(X, Y, log_mag1, levels=levels1, colors='black', alpha=0.3, linewidths=0.5)
    
    if np.any(np.isfinite(log_mag2)):
        levels2 = np.linspace(np.nanmin(log_mag2), np.nanmax(log_mag2), 8)
        ax2.contour(X, Y, log_mag2, levels=levels2, colors='black', alpha=0.3, linewidths=0.5)
    
    # Add a simple test trajectory
    print("Adding test trajectory...")
    t = np.linspace(0, 2*np.pi, 100)
    traj_x = p/2 + p/4 * np.cos(t)
    traj_y = q/2 + q/6 * np.sin(t)
    
    ax1.plot(traj_x, traj_y, 'red', linewidth=2, alpha=0.8, label='Test trajectory')
    ax2.plot(traj_x, traj_y, 'red', linewidth=2, alpha=0.8, label='Test trajectory')
    
    # Formatting
    ax1.set_title('℘(z)')
    ax2.set_title("℘'(z)")
    ax1.set_xlabel('Re(z)')
    ax1.set_ylabel('Im(z)')
    ax2.set_xlabel('Re(z)')
    ax2.set_ylabel('')
    
    ax1.set_xlim(0, p)
    ax1.set_ylim(0, q)
    ax2.set_xlim(0, p)
    ax2.set_ylim(0, q)
    
    ax2.set_yticks([])
    
    plt.tight_layout()
    
    # Save the figure
    filename = 'test_visualization.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Test visualization saved as {filename}")
    
    plt.close()
    return True

if __name__ == "__main__":
    success = create_test_visualization()
    if success:
        print("✓ Visualization test completed successfully!")
    else:
        print("✗ Visualization test failed!")