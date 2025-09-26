"""
Integration and Trajectory Functions for Weierstrass ℘ Function

This module contains functions for:
- Trajectory integration using RK4 method
- Second-order ODE solving with blow-up detection
- Fundamental cell wrapping
- Lattice trajectory generation
"""

import numpy as np
import warnings
from .core import wp_rect, wrap_point


def wrap_with_breaks(zs, p, q, wrap_threshold=0.5):
    """
    Wrap trajectory to fundamental cell and insert breaks at wrap jumps.
    
    Detects when trajectory wraps around fundamental cell boundaries
    and inserts NaN breaks for proper visualization.
    
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
            result.append(np.nan + 1j * np.nan)  # Insert break
        
        result.append(wrapped[i])
    
    return np.array(result)


def integrate_second_order_with_blowup(z0, v0, dt, T, p, q, N, blow_thresh=10.0, pole_eps=1e-6):
    """
    Integrate second-order ODE: z''(t) = -℘(z(t)) * z(t) using RK4 with blow-up detection.
    
    This integrates the equation of motion for a particle in the Weierstrass ℘ potential.
    The integration stops early if:
    - Particle gets too close to a pole
    - Step size becomes too large (blow-up)  
    - Non-finite values are encountered
    
    Args:
        z0, v0: initial position and velocity (complex numbers)
        dt: time step
        T: total integration time
        p, q, N: lattice parameters
        blow_thresh: blow-up threshold for |Δz|
        pole_eps: pole proximity threshold
    
    Returns:
        (trajectory, blow_up_point): 
            trajectory - array of position values
            blow_up_point - complex number where blow-up occurred, or None
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
        
        # Check distance to all lattice points within truncation
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


def generate_lattice_trajectories(p, q, N, dt, T, blow_thresh=10.0):
    """
    Generate systematic trajectories for lattice analysis.
    
    Creates trajectories starting at z = 1, 2, 3, ..., p-1 with z' = i.
    Useful for understanding the periodic structure.
    
    Args:
        p, q, N: lattice parameters
        dt: integration time step
        T: integration time
        blow_thresh: blow-up threshold
        
    Returns:
        list of (trajectory, blowup_point) tuples
    """
    trajectories = []
    
    for k in range(1, int(p)):
        z0 = complex(k, 0)
        v0 = complex(0, 1)  # z' = i
        
        try:
            trajectory, blowup_point = integrate_second_order_with_blowup(
                z0, v0, dt, T, p, q, N, blow_thresh
            )
            trajectories.append((trajectory, blowup_point))
        except Exception as e:
            warnings.warn(f"Error integrating lattice trajectory k={k}: {e}")
            trajectories.append((np.array([z0]), None))
    
    return trajectories


def adaptive_step_integration(z0, v0, T, p, q, N, rtol=1e-6, atol=1e-9, 
                            blow_thresh=10.0, pole_eps=1e-6, max_steps=10000):
    """
    Integrate with adaptive step size control.
    
    Uses embedded RK4/RK5 method for automatic step size adjustment.
    More accurate but slower than fixed-step integration.
    
    Args:
        z0, v0: initial conditions
        T: total time
        p, q, N: lattice parameters
        rtol, atol: relative and absolute tolerance
        blow_thresh: blow-up threshold
        pole_eps: pole proximity threshold
        max_steps: maximum number of steps
        
    Returns:
        (trajectory, times, blow_up_point)
    """
    def force(z):
        """Compute force: -℘(z) * z"""
        wp_val = wp_rect(z, p, q, N)
        return -wp_val * z
    
    def rk45_step(t, state, dt):
        """Single RK4/5 step with error estimate"""
        z, v = state[0], state[1]
        
        # RK4 coefficients
        k1 = dt * np.array([v, force(z)])
        k2 = dt * np.array([v + k1[1]/2, force(z + k1[0]/2)])
        k3 = dt * np.array([v + k2[1]/2, force(z + k2[0]/2)])
        k4 = dt * np.array([v + k3[1], force(z + k3[0])])
        
        # RK4 estimate
        y4 = state + (k1 + 2*k2 + 2*k3 + k4) / 6
        
        # RK5 estimate (simplified)
        k5 = dt * np.array([y4[1], force(y4[0])])
        y5 = state + (7*k1 + 32*k2 + 12*k3 + 32*k4 + 7*k5) / 90
        
        # Error estimate
        err = np.abs(y5 - y4)
        
        return y4, y5, err
    
    # Initialize
    trajectory = [z0]
    times = [0.0]
    state = np.array([z0, v0])
    t = 0.0
    dt = T / 1000  # Initial step size
    step = 0
    
    while t < T and step < max_steps:
        # Check for pole proximity
        z_wrapped = wrap_point(state[0], p, q)
        for m in range(-N, N+1):
            for n in range(-N, N+1):
                omega = m * p + n * 1j * q
                omega_wrapped = wrap_point(omega, p, q)
                if abs(z_wrapped - omega_wrapped) < pole_eps:
                    return np.array(trajectory), np.array(times), state[0]
        
        # Take step
        try:
            y4, y5, err = rk45_step(t, state, dt)
            
            # Error control
            err_norm = np.max([abs(e) for e in err])
            tol = rtol * np.max([abs(s) for s in state]) + atol
            
            if err_norm <= tol:
                # Accept step
                state = y4
                t += dt
                trajectory.append(state[0])
                times.append(t)
                
                # Check for blow-up
                if abs(state[0]) > blow_thresh or not np.isfinite(state[0]):
                    return np.array(trajectory), np.array(times), state[0]
            
            # Adjust step size
            if err_norm > 0:
                dt_new = dt * min(2.0, max(0.5, 0.9 * (tol / err_norm)**0.2))
                dt = min(dt_new, T - t)
            
            step += 1
            
        except Exception:
            return np.array(trajectory), np.array(times), state[0]
    
    return np.array(trajectory), np.array(times), None


def integrate_and_evaluate_wp(z0, v0, dt, T, p, q, N, blow_thresh=10.0, pole_eps=1e-6):
    """
    Integrate trajectory and evaluate ℘(z(t)) along the path for time-series visualization.
    
    This function combines trajectory integration with function evaluation to produce
    time-series data for visualization.
    
    Args:
        z0, v0: initial position and velocity (complex)
        dt: time step
        T: total time
        p, q, N: lattice parameters
        blow_thresh: blow-up threshold for |Δz|
        pole_eps: pole proximity threshold
    
    Returns:
        (times, trajectory, wp_values, blowup_point)
        where wp_values contains ℘(z(t)) at each time step
    """
    # Get trajectory using existing integration function
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