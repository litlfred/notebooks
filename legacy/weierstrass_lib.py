"""
Weierstrass ℘ Function Library

This module contains the core mathematical functions for the Weierstrass ℘ playground,
separated from the notebook UI code for better reusability and maintainability.
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


def wp_and_deriv(z, p, q, N):
    """
    Compute both ℘(z) and ℘'(z) efficiently.
    
    Returns:
        (wp_val, wp_deriv_val)
    """
    return wp_rect(z, p, q, N), wp_deriv(z, p, q, N)


# Field Sampling and Visualization Functions
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


def soft_background(F, M, sat=0.3, mag_scale=1.0, value_floor=0.3):
    """
    Create soft color palette RGB image.
    
    Args:
        F: complex field values
        M: valid mask
        sat: saturation level
        mag_scale: magnitude scaling
        value_floor: minimum brightness
    
    Returns:
        RGB image array
    """
    # Hue from argument
    H = np.angle(F) / (2 * np.pi) + 0.5  # Map to [0, 1]
    H = H % 1.0
    
    # Brightness from magnitude with compression
    mag = np.abs(F) * mag_scale
    V = np.arctan(mag) / (np.pi / 2)  # Compress to [0, 1]
    V = value_floor + (1 - value_floor) * V  # Raise floor
    
    # Constant saturation
    S = np.full_like(H, sat)
    
    # Convert HSV to RGB
    HSV = np.stack([H, S, V], axis=-1)
    RGB = mcolors.hsv_to_rgb(HSV)
    
    # Apply mask (set invalid regions to white)
    RGB = np.where(M[..., np.newaxis], RGB, 1.0)
    
    return np.clip(RGB, 0, 1)


def grayscale_background(F, M, value_floor=0.1):
    """
    Create grayscale background for real or imaginary parts.
    
    Args:
        F: real field values (e.g., Re(℘'(z)) or Im(℘'(z)))
        M: valid mask
        value_floor: minimum brightness
    
    Returns:
        RGB grayscale image array
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
    Add topographic contours of |F|.
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
    Add vector field overlay with magnitude compression and length clipping.
    """
    if density <= 0:
        return
    
    # Subsample grid
    ny, nx = X.shape
    step_x = max(1, nx // density)
    step_y = max(1, ny // density)
    
    X_sub = X[::step_y, ::step_x]
    Y_sub = Y[::step_y, ::step_x]
    F_sub = F[::step_y, ::step_x]
    M_sub = M[::step_y, ::step_x]
    
    # Vector components with compression
    mag = np.abs(F_sub)
    # Compress magnitude
    compressed_mag = np.tanh(mag / np.nanmax(mag) * 2) if np.nanmax(mag) > 0 else mag
    
    U = np.real(F_sub / mag * compressed_mag)
    V = np.imag(F_sub / mag * compressed_mag)
    
    # Apply mask and length filter
    arrow_len = np.sqrt(U**2 + V**2)
    valid = M_sub & np.isfinite(U) & np.isfinite(V) & (arrow_len <= max_len)
    
    if np.any(valid):
        ax.quiver(X_sub[valid], Y_sub[valid], U[valid], V[valid], 
                 scale_units='xy', scale=1, width=width, alpha=0.7, color='darkblue')


# Trajectory Integration Functions
def wrap_point(z, p, q):
    """
    Wrap a point to the fundamental cell [0,p] × [0,q].
    """
    return (z.real % p) + 1j * (z.imag % q)


def wrap_with_breaks(zs, p, q, wrap_threshold=0.5):
    """
    Wrap trajectory to fundamental cell and insert breaks at wrap jumps.
    
    Args:
        zs: array of complex trajectory points
        p, q: lattice parameters
        wrap_threshold: fraction of cell size to detect wraps
    
    Returns:
        wrapped_zs with NaN breaks where wrapping occurs
    """
    if len(zs) == 0:
        return np.array([])
    
    wrapped = np.array([wrap_point(z, p, q) for z in zs])
    result = [wrapped[0]]
    
    for i in range(1, len(wrapped)):
        dz = wrapped[i] - wrapped[i-1]
        
        # Check for wrap in x or y direction
        if (abs(dz.real) > wrap_threshold * p or 
            abs(dz.imag) > wrap_threshold * q):
            result.append(np.nan + 1j * np.nan)  # Break
        
        result.append(wrapped[i])
    
    return np.array(result)


def integrate_second_order_with_blowup(z0, v0, dt, T, p, q, N, blow_thresh=10.0, pole_eps=1e-6):
    """
    Integrate second-order ODE: z''(t) = -℘(z(t)) * z(t)
    using RK4 with blow-up detection.
    
    Args:
        z0, v0: initial position and velocity (complex)
        dt: time step
        T: total time
        p, q, N: lattice parameters
        blow_thresh: blow-up threshold for |Δz|
        pole_eps: pole proximity threshold
    
    Returns:
        (trajectory, blow_up_point) where blow_up_point is None if no blow-up
    """
    def force(z):
        """Compute force: -℘(z) * z"""
        wp_val = wp_rect(z, p, q, N)
        return -wp_val * z
    
    # Convert to system of first-order ODEs
    def rhs(t, state):
        """Right-hand side: [z', v'] = [v, force(z)]"""
        z, v = state[0], state[1]
        return np.array([v, force(z)])
    
    # RK4 integration
    steps = int(T / dt)
    trajectory = []
    
    state = np.array([z0, v0])
    t = 0
    
    trajectory.append(state[0])  # Store position
    
    for step in range(steps):
        # Check for pole proximity
        z_wrapped = wrap_point(state[0], p, q)
        too_close_to_pole = False
        
        for m in range(-N, N+1):
            for n in range(-N, N+1):
                omega = m * p + n * 1j * q
                omega_wrapped = wrap_point(omega, p, q)
                if abs(z_wrapped - omega_wrapped) < pole_eps:
                    too_close_to_pole = True
                    break
            if too_close_to_pole:
                break
        
        if too_close_to_pole:
            return np.array(trajectory), state[0]  # Blow-up at pole
        
        # RK4 step
        try:
            k1 = dt * rhs(t, state)
            k2 = dt * rhs(t + dt/2, state + k1/2)
            k3 = dt * rhs(t + dt/2, state + k2/2)
            k4 = dt * rhs(t + dt, state + k3)
            
            new_state = state + (k1 + 2*k2 + 2*k3 + k4) / 6
            
            # Check for blow-up
            dz = new_state[0] - state[0]
            if (abs(dz) > blow_thresh or 
                not np.isfinite(new_state[0]) or 
                not np.isfinite(new_state[1])):
                return np.array(trajectory), state[0]  # Blow-up detected
            
            state = new_state
            t += dt
            trajectory.append(state[0])
            
        except Exception:
            return np.array(trajectory), state[0]  # Integration error
    
    return np.array(trajectory), None  # No blow-up


# Visualization Setup Functions
def create_two_panel_figure(p, q):
    """Create a two-panel figure for ℘(z) and ℘'(z)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.subplots_adjust(wspace=0.0)
    
    # Set labels and limits
    ax1.set_title('℘(z)', fontsize=16)
    ax2.set_title("℘'(z)", fontsize=16)
    ax1.set_xlabel('Re(z)')
    ax1.set_ylabel('Im(z)')
    ax2.set_xlabel('Re(z)')
    ax2.set_ylabel('')
    
    ax1.set_xlim(0, p)
    ax1.set_ylim(0, q)
    ax2.set_xlim(0, p)
    ax2.set_ylim(0, q)
    
    ax2.set_yticks([])
    
    return fig, (ax1, ax2)


def create_three_panel_figure(p, q):
    """Create a three-panel figure for ℘(z), Re(℘'(z)), and Im(℘'(z))."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 8))
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


def create_five_panel_figure(p, q):
    """Create a five-panel figure: ℘(z), ℘'(z), complex plane, Re(℘(z)), Im(℘(z))."""
    fig = plt.figure(figsize=(30, 12))
    
    # Create 2x3 subplot grid, use 5 panels
    ax1 = plt.subplot(2, 3, 1)  # Top left: ℘(z)
    ax2 = plt.subplot(2, 3, 2)  # Top middle: ℘'(z)  
    ax3 = plt.subplot(2, 3, 3)  # Top right: complex plane grid
    ax4 = plt.subplot(2, 3, 4)  # Bottom left: Re(℘(z))
    ax5 = plt.subplot(2, 3, 5)  # Bottom middle: Im(℘(z))
    # Leave subplot (2,3,6) empty
    
    fig.subplots_adjust(wspace=0.05, hspace=0.3)
    
    # Set titles
    ax1.set_title('℘(z)', fontsize=16)
    ax2.set_title("℘'(z)", fontsize=16)
    ax3.set_title('Complex Plane', fontsize=16)
    ax4.set_title('Re(℘(z))', fontsize=16)
    ax5.set_title('Im(℘(z))', fontsize=16)
    
    # Set labels and limits for all panels
    for ax in [ax1, ax2, ax3, ax4, ax5]:
        ax.set_xlim(0, p)
        ax.set_ylim(0, q)
        ax.set_xlabel('Re(z)')
        
    ax1.set_ylabel('Im(z)')
    ax4.set_ylabel('Im(z)')
    
    # Remove y-tick labels for middle and right panels
    for ax in [ax2, ax3, ax5]:
        ax.set_yticks([])
    
    return fig, (ax1, ax2, ax3, ax4, ax5)


def plot_trajectories_on_axes(axes, trajectories, colors, p, q, emoji_size=20):
    """Plot trajectories on given axes with blow-up markers."""
    for i, (trajectory, blowup_point) in enumerate(trajectories):
        if len(trajectory) > 1:
            # Wrap trajectory with breaks
            wrapped_traj = wrap_with_breaks(trajectory, p, q)
            
            # Split trajectory at NaN breaks
            segments = []
            current_segment = []
            
            for z in wrapped_traj:
                if np.isnan(z):
                    if current_segment:
                        segments.append(np.array(current_segment))
                        current_segment = []
                else:
                    current_segment.append(z)
            
            if current_segment:
                segments.append(np.array(current_segment))
            
            # Plot segments on all axes
            for segment in segments:
                if len(segment) > 1:
                    for ax in axes:
                        ax.plot(segment.real, segment.imag, color=colors[i], linewidth=2, alpha=0.8)
            
            # Mark starting point
            z0_wrapped = wrap_point(trajectory[0], p, q)
            for ax in axes:
                ax.plot(z0_wrapped.real, z0_wrapped.imag, 'o', color=colors[i], 
                       markersize=8, markeredgecolor='white')
            
            # Mark blow-up point if exists
            if blowup_point is not None:
                bp_wrapped = wrap_point(blowup_point, p, q)
                for ax in axes:
                    ax.text(bp_wrapped.real, bp_wrapped.imag, '💥', fontsize=emoji_size, 
                           ha='center', va='center')


def plot_lattice_trajectories_on_axes(axes, trajectories, p, q):
    """Plot lattice trajectories on given axes as dotted grey lines."""
    for trajectory, blowup_point in trajectories:
        if len(trajectory) > 1:
            # Wrap trajectory with breaks
            wrapped_traj = wrap_with_breaks(trajectory, p, q)
            
            # Split trajectory at NaN breaks
            segments = []
            current_segment = []
            
            for z in wrapped_traj:
                if np.isnan(z):
                    if current_segment:
                        segments.append(np.array(current_segment))
                        current_segment = []
                else:
                    current_segment.append(z)
            
            if current_segment:
                segments.append(np.array(current_segment))
            
            # Plot segments on all axes as dotted grey lines
            for segment in segments:
                if len(segment) > 1:
                    for ax in axes:
                        ax.plot(segment.real, segment.imag, color='grey', 
                               linewidth=1, alpha=0.6, linestyle=':', zorder=0)


def save_high_resolution_figure(fig, filename='weierstrass_high_res.png', dpi=300):
    """Save figure at high resolution and return the filename."""
    fig.savefig(filename, dpi=dpi, bbox_inches='tight', facecolor='white')
    return filename


def create_time_series_figure():
    """Create a two-panel figure for time series visualization of ℘(z(t))."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.subplots_adjust(wspace=0.3)
    
    # Set labels and titles
    ax1.set_title('Re(℘(z(t))) vs Time', fontsize=16)
    ax2.set_title('Im(℘(z(t))) vs Time', fontsize=16)
    ax1.set_xlabel('Time t')
    ax1.set_ylabel('Re(℘(z(t)))')
    ax2.set_xlabel('Time t')
    ax2.set_ylabel('Im(℘(z(t)))')
    
    # Add grid for better readability
    ax1.grid(True, alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    return fig, (ax1, ax2)


def integrate_and_evaluate_wp(z0, v0, dt, T, p, q, N, blow_thresh=10.0, pole_eps=1e-6):
    """
    Integrate trajectory and evaluate ℘(z(t)) along the path.
    
    Returns:
        (times, trajectory, wp_values, blowup_point)
        where wp_values contains ℘(z(t)) at each time step
    """
    # Get trajectory
    trajectory, blowup_point = integrate_second_order_with_blowup(
        z0, v0, dt, T, p, q, N, blow_thresh, pole_eps
    )
    
    # Create time array
    times = np.arange(len(trajectory)) * dt
    
    # Evaluate ℘(z(t)) for each point in trajectory
    wp_values = []
    for z in trajectory:
        try:
            wp_val = wp_rect(z, p, q, N)
            if np.isfinite(wp_val):
                wp_values.append(wp_val)
            else:
                wp_values.append(np.nan + 1j*np.nan)
        except:
            wp_values.append(np.nan + 1j*np.nan)
    
    wp_values = np.array(wp_values)
    
    return times, trajectory, wp_values, blowup_point


def plot_time_series_on_axes(axes, trajectories_data, colors, T):
    """Plot time series data on the given axes."""
    ax1, ax2 = axes
    
    for i, (times, trajectory, wp_values, blowup_point) in enumerate(trajectories_data):
        if len(wp_values) > 0:
            color = colors[i % len(colors)]
            
            # Plot real part
            ax1.plot(times, np.real(wp_values), color=color, alpha=0.8, linewidth=1.5)
            
            # Plot imaginary part  
            ax2.plot(times, np.imag(wp_values), color=color, alpha=0.8, linewidth=1.5)
            
            # Mark blow-up point if it exists
            if blowup_point is not None and len(times) > 1:
                ax1.plot(times[-1], np.real(wp_values[-1]), 'x', color=color, markersize=10, markeredgewidth=2)
                ax2.plot(times[-1], np.imag(wp_values[-1]), 'x', color=color, markersize=10, markeredgewidth=2)
    
    # Set time axis limits
    ax1.set_xlim(0, T)
    ax2.set_xlim(0, T)