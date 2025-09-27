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


def soft_background(F, M):
    """
    Generate soft background colors for visualization.
    
    Args:
        F: complex field values (2D array)
        M: mask array (2D boolean array)
        
    Returns:
        RGB background array with shape (ny, nx, 3)
    """
    ny, nx = F.shape
    bg = np.zeros((ny, nx, 3))
    
    # Create a soft gradient background based on the field magnitude
    magnitude = np.abs(F)
    magnitude = np.where(M, magnitude, 0)
    
    if np.max(magnitude) > 0:
        normalized = magnitude / np.max(magnitude)
        
        # Generate RGB values based on magnitude and phase
        phase = np.angle(F)
        
        # Soft color scheme: red/green based on phase, blue based on magnitude
        bg[:, :, 0] = 0.2 + 0.3 * np.sin(phase) ** 2  # Red component
        bg[:, :, 1] = 0.2 + 0.3 * np.cos(phase) ** 2  # Green component 
        bg[:, :, 2] = 0.3 + 0.4 * normalized           # Blue component
    else:
        # Default soft blue background
        bg[:, :, :] = [0.2, 0.2, 0.5]
    
    return bg


def integrate_second_order_with_blowup(z0, v0, dt, T, p, q, N):
    """
    Integrate particle trajectory with blow-up detection.
    
    Args:
        z0: initial position (complex)
        v0: initial velocity (complex)  
        dt: time step
        T: total time
        p, q: lattice parameters
        N: truncation parameter
        
    Returns:
        trajectory: array of complex positions
        blowup_point: index where blow-up occurred, or None
    """
    nsteps = int(T / dt)
    trajectory = np.zeros(nsteps + 1, dtype=complex)
    
    z, v = z0, v0
    trajectory[0] = z
    blowup_point = None
    
    for i in range(nsteps):
        # Check for blow-up (large values or NaN)
        if abs(z) > 100 or not np.isfinite(z):
            blowup_point = i
            break
            
        # Simple Euler integration
        wp_val = wp_rect(z, p, q, N)
        if not np.isfinite(wp_val):
            blowup_point = i
            break
            
        # Second-order dynamics with damping
        acceleration = -0.1 * wp_val - 0.05 * v
        v += acceleration * dt
        z += v * dt
        trajectory[i + 1] = z
        
    return trajectory[:i+2], blowup_point


def create_figure_with_plots(plot_type, p, q, N, nx, ny, x_range, y_range, pole_threshold, pole_mask_radius,
                           bg_opacity, traj_opacity, traj_width, particles, dt, T, blowup_threshold, 
                           max_steps, use_adaptive_step):
    """
    Create matplotlib figure with field and trajectory plots.
    
    Args:
        plot_type: type of plot ('two_panel', 'three_panel', etc.)
        p, q: lattice parameters
        N: truncation parameter
        nx, ny: grid dimensions
        x_range, y_range: plot ranges
        pole_threshold: threshold for pole detection
        pole_mask_radius: radius for pole masking
        bg_opacity: background opacity
        traj_opacity: trajectory opacity
        traj_width: trajectory line width
        particles: list of (z0, v0) initial conditions
        dt: time step
        T: total integration time
        blowup_threshold: threshold for blowup detection
        max_steps: maximum integration steps
        use_adaptive_step: whether to use adaptive step size
        
    Returns:
        fig: matplotlib figure
        axes: array of matplotlib axes
    """
    import matplotlib.pyplot as plt
    
    # Generate field data
    X, Y, F_grid, M_grid = field_grid(p, q, 'wp', N, nx, ny, pole_threshold)
    
    # Generate trajectories
    trajectories = []
    for z0, v0 in particles:
        traj, _ = integrate_second_order_with_blowup(z0, v0, dt, T, p, q, N)
        trajectories.append(traj)
    
    # Create figure based on plot type
    if plot_type == 'two_panel':
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    elif plot_type == 'three_panel':
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    else:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Ensure axes is always an array
    if not hasattr(axes, '__len__'):
        axes = [axes]
    
    # Plot 1: Field magnitude
    ax1 = axes[0]
    valid_F = np.where(M_grid, F_grid, np.nan)
    magnitude = np.abs(valid_F)
    
    if np.nanmax(magnitude) > 0:
        im1 = ax1.imshow(magnitude, extent=[-x_range, x_range, -y_range, y_range], 
                        cmap='viridis', origin='lower', interpolation='bilinear', alpha=bg_opacity)
        plt.colorbar(im1, ax=ax1, label='|℘(z)|')
    
    ax1.set_title(f'Weierstrass ℘ Field (p={p}, q={q})')
    ax1.set_xlabel('Re(z)')
    ax1.set_ylabel('Im(z)')
    ax1.grid(True, alpha=0.3)
    
    # Plot trajectories on field plot
    for i, trajectory in enumerate(trajectories):
        if len(trajectory) > 0:
            real_parts = np.real(trajectory)
            imag_parts = np.imag(trajectory)
            ax1.plot(real_parts, imag_parts, 'o-', markersize=2, linewidth=traj_width, 
                    alpha=traj_opacity, label=f'Particle {i+1}')
    
    # Plot 2: Trajectory detail (if there are multiple axes)
    if len(axes) > 1:
        ax2 = axes[1] 
        for i, trajectory in enumerate(trajectories):
            if len(trajectory) > 0:
                real_parts = np.real(trajectory)
                imag_parts = np.imag(trajectory)
                ax2.plot(real_parts, imag_parts, 'o-', markersize=2, linewidth=traj_width, 
                        label=f'Particle {i+1}')
                
                # Mark start and end points
                if len(trajectory) > 1:
                    ax2.plot(real_parts[0], imag_parts[0], 'go', markersize=8, label=f'Start {i+1}')
                    ax2.plot(real_parts[-1], imag_parts[-1], 'ro', markersize=8, label=f'End {i+1}')
        
        ax2.set_title('Particle Trajectories')
        ax2.set_xlabel('Re(z)')
        ax2.set_ylabel('Im(z)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    return fig, axes