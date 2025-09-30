"""
Browser-Specific Adaptations for Pyodide

This module contains functions specifically adapted for running in the browser
with Pyodide, including web-friendly visualization and interaction utilities.
"""

import numpy as np
from matplotlib import pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from . import core, visualization, integration


def create_complete_visualization(mode, p, q, N, nx, ny, n_contours, vec_density, 
                                vec_width, vec_max_len, saturation, value_floor, 
                                mag_scale, particles, dt, T, blow_thresh, 
                                emoji_size, show_lattice_trajectories):
    """
    Create complete visualization adapted for browser display.
    
    This is the main function called from JavaScript in the browser version.
    Returns matplotlib figure optimized for web display via Pyodide.
    
    Args:
        mode: visualization mode ('two_panel', 'three_panel', 'five_panel', 'time_series')
        p, q, N: lattice parameters
        nx, ny: grid resolution
        n_contours: number of contour lines
        vec_density: vector field density
        vec_width, vec_max_len: vector display parameters
        saturation, value_floor, mag_scale: color parameters
        particles: list of (z0_real, z0_imag, v0_real, v0_imag) tuples
        dt, T: integration parameters
        blow_thresh: blow-up threshold
        emoji_size: size of blow-up markers
        show_lattice_trajectories: whether to show systematic trajectories
        
    Returns:
        matplotlib figure ready for web display
    """
    # Validate parameters
    core.validate_parameters(p, q, N)
    
    # Create figure layout
    fig, axes = visualization.create_figure_layout(mode, p, q, figsize_base=8)
    
    if mode == 'two_panel':
        ax1, ax2 = axes
        
        # Compute fields
        X1, Y1, F1, M1 = core.field_grid(p, q, 'wp', N, nx, ny)
        X2, Y2, F2, M2 = core.field_grid(p, q, 'wp_deriv', N, nx, ny)
        
        # Create backgrounds
        bg1 = visualization.soft_background(F1, M1, saturation, mag_scale, value_floor)
        bg2 = visualization.soft_background(F2, M2, saturation, mag_scale, value_floor)
        
        # Display backgrounds
        ax1.imshow(bg1, extent=[0, p, 0, q], origin='lower', aspect='equal')
        ax2.imshow(bg2, extent=[0, p, 0, q], origin='lower', aspect='equal')
        
        # Add contours
        visualization.add_topo_contours(ax1, X1, Y1, F1, M1, n_contours)
        visualization.add_topo_contours(ax2, X2, Y2, F2, M2, n_contours)
        
        # Add vector fields
        if vec_density > 0:
            visualization.vector_overlay(ax1, X1, Y1, F1, M1, vec_density, vec_width, vec_max_len)
            visualization.vector_overlay(ax2, X2, Y2, F2, M2, vec_density, vec_width, vec_max_len)
    
    elif mode == 'time_series':
        # Time-series visualization mode
        if len(particles) == 0:
            # If no particles specified, use a default one
            particles = [(p/2, q/2, 0.0, 1.0)]
        
        # For time-series, we process only the first particle
        z0_real, z0_imag, v0_real, v0_imag = particles[0]
        z0 = complex(z0_real, z0_imag)
        v0 = complex(v0_real, v0_imag)
        
        try:
            # Integrate trajectory
            trajectory, blowup_point = integration.integrate_second_order_with_blowup(
                z0, v0, dt, T, p, q, N, blow_thresh
            )
            
            if len(trajectory) > 1:
                # Create time-series plots
                fig = visualization.create_time_series_visualization(trajectory, dt, p, q, N)
                return fig
            else:
                raise ValueError("Trajectory too short for time-series visualization")
                
        except Exception as e:
            print(f"Error creating time-series visualization: {e}")
            # Fall back to two-panel mode
            return create_complete_visualization('two_panel', p, q, N, nx, ny, n_contours, 
                                               vec_density, vec_width, vec_max_len, saturation, 
                                               value_floor, mag_scale, particles, dt, T, 
                                               blow_thresh, emoji_size, show_lattice_trajectories)
    
    else:
        # For other modes, default to two-panel for browser compatibility
        return create_complete_visualization('two_panel', p, q, N, nx, ny, n_contours, 
                                           vec_density, vec_width, vec_max_len, saturation, 
                                           value_floor, mag_scale, particles, dt, T, 
                                           blow_thresh, emoji_size, show_lattice_trajectories)
    
    # Integrate and plot particle trajectories (only for non-time-series modes)
    if mode != 'time_series':
        trajectory_colors = plt.cm.tab10(np.linspace(0, 1, len(particles)))
        
        for i, (z0_real, z0_imag, v0_real, v0_imag) in enumerate(particles):
            z0 = complex(z0_real, z0_imag)
            v0 = complex(v0_real, v0_imag)
            
            try:
                trajectory, blowup_point = integration.integrate_second_order_with_blowup(
                    z0, v0, dt, T, p, q, N, blow_thresh
                )
                
                if len(trajectory) > 1:
                    # Wrap trajectory with breaks
                    wrapped_traj = integration.wrap_with_breaks(trajectory, p, q)
                    
                    # Plot trajectory segments
                    plot_trajectory_segments(axes, wrapped_traj, trajectory_colors[i], 
                                           p, q, blowup_point, emoji_size)
            
            except Exception as e:
                print(f"Error integrating particle {i}: {e}")
                # Plot just the starting point
                z0_wrapped = core.wrap_point(z0, p, q)
                for ax in axes:
                    ax.plot(z0_wrapped.real, z0_wrapped.imag, 'o', color=trajectory_colors[i], 
                           markersize=8, markeredgecolor='white')
        
        # Plot lattice trajectories if requested
        if show_lattice_trajectories:
            try:
                lattice_trajectories = integration.generate_lattice_trajectories(
                    p, q, N, dt, T, blow_thresh
                )
                
                for trajectory, blowup_point in lattice_trajectories:
                    if len(trajectory) > 1:
                        wrapped_traj = integration.wrap_with_breaks(trajectory, p, q)
                        plot_lattice_trajectory_segments(axes, wrapped_traj, p, q)
                        
            except Exception as e:
                print(f"Error generating lattice trajectories: {e}")
    
    plt.tight_layout()
    return fig


def plot_trajectory_segments(axes, wrapped_traj, color, p, q, blowup_point=None, emoji_size=20):
    """
    Plot trajectory segments on all axes with proper wrapping.
    
    Args:
        axes: tuple of matplotlib axes
        wrapped_traj: trajectory with NaN breaks
        color: trajectory color
        p, q: lattice parameters
        blowup_point: blow-up location (if any)
        emoji_size: size of blow-up marker
    """
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
                ax.plot(segment.real, segment.imag, color=color, linewidth=2, alpha=0.8)
    
    # Mark starting point
    if len(wrapped_traj) > 0 and not np.isnan(wrapped_traj[0]):
        z0_wrapped = wrapped_traj[0]
        for ax in axes:
            ax.plot(z0_wrapped.real, z0_wrapped.imag, 'o', color=color, 
                   markersize=8, markeredgecolor='white')
    
    # Mark blow-up point if exists
    if blowup_point is not None:
        bp_wrapped = core.wrap_point(blowup_point, p, q)
        for ax in axes:
            ax.text(bp_wrapped.real, bp_wrapped.imag, '💥', fontsize=emoji_size, 
                   ha='center', va='center')


def plot_lattice_trajectory_segments(axes, wrapped_traj, p, q):
    """
    Plot lattice trajectory segments as dotted grey lines.
    
    Args:
        axes: tuple of matplotlib axes  
        wrapped_traj: trajectory with NaN breaks
        p, q: lattice parameters
    """
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
    
    # Plot segments as dotted grey lines
    for segment in segments:
        if len(segment) > 1:
            for ax in axes:
                ax.plot(segment.real, segment.imag, color='grey', 
                       linewidth=1, alpha=0.6, linestyle=':', zorder=0)


def parse_complex_parameter(param_str):
    """
    Parse complex number from string input (browser-friendly).
    
    Handles various formats like "5+2j", "3-1j", "5", "2j", etc.
    
    Args:
        param_str: string representation of complex number
        
    Returns:
        complex number
    """
    param_str = param_str.strip().replace(' ', '')
    
    # Handle formats like "5+2j", "3-1j", "5", "2j", etc.
    real = 0.0
    imag = 0.0
    
    # Extract imaginary part
    import re
    imag_match = re.search(r'([+-]?\d*\.?\d*)j$', param_str)
    if imag_match:
        imag_str = imag_match.group(1)
        if imag_str in ['', '+']:
            imag = 1.0
        elif imag_str == '-':
            imag = -1.0
        else:
            imag = float(imag_str)
        param_str = param_str[:imag_match.start()]
    
    # Extract real part
    if param_str:
        real = float(param_str)
    
    return complex(real, imag)


def validate_browser_parameters(params):
    """
    Validate parameters from browser input.
    
    Args:
        params: dictionary of parameter values from browser
        
    Returns:
        validated_params: dictionary with validated/corrected values
        
    Raises:
        ValueError: if critical parameters are invalid
    """
    validated = {}
    
    # Validate basic parameters
    validated['p'] = max(0.1, min(50.0, float(params.get('p', 11.0))))
    validated['q'] = max(0.1, min(50.0, float(params.get('q', 5.0))))
    validated['N'] = max(0, min(6, int(params.get('N', 3))))
    
    # Validate grid parameters
    validated['nx'] = max(20, min(500, int(params.get('nx', 100))))
    validated['ny'] = max(20, min(500, int(params.get('ny', 100))))
    
    # Validate visualization parameters
    validated['n_contours'] = max(0, min(50, int(params.get('n_contours', 10))))
    validated['vec_density'] = max(0, min(50, int(params.get('vec_density', 15))))
    
    # Validate color parameters
    validated['saturation'] = max(0.0, min(1.0, float(params.get('saturation', 0.2))))
    validated['value_floor'] = max(0.0, min(1.0, float(params.get('value_floor', 0.4))))
    validated['mag_scale'] = max(0.1, min(10.0, float(params.get('mag_scale', 0.8))))
    
    # Validate integration parameters
    validated['dt'] = max(0.001, min(1.0, float(params.get('dt', 0.01))))
    validated['T'] = max(0.1, min(100.0, float(params.get('T', 10.0))))
    validated['blow_thresh'] = max(1.0, min(1000.0, float(params.get('blow_thresh', 10.0))))
    
    return validated


# Browser-specific utility functions
def get_memory_usage():
    """Get approximate memory usage (browser-friendly)."""
    try:
        import gc
        return len(gc.get_objects())
    except:
        return "unknown"


def cleanup_matplotlib():
    """Clean up matplotlib memory (important for browser)."""
    plt.close('all')
    try:
        import gc
        gc.collect()
    except:
        pass