#!/usr/bin/env python3
"""
Demo script showing the new time-series visualization for ℘(z(t)) and ℘'(z(t))

This script demonstrates the new visualization where:
- Horizontal axis goes from 0 to T (time)
- Vertical axis shows Re(℘(z(t))) and Im(℘(z(t))) in separate plots
- Also shows Re(℘'(z(t))) and Im(℘'(z(t))) in separate plots
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from weierstrass_playground import browser

def demo_time_series_visualization():
    """Demonstrate the new time-series visualization"""
    print("Demo: Time-Series Visualization of ℘(z(t)) and ℘'(z(t))")
    print("=" * 60)
    
    # Parameters
    p, q, N = 11.0, 5.0, 3  # Lattice parameters
    dt, T = 0.01, 3.0       # Integration parameters
    
    # Initial conditions for particle trajectory
    z0_real, z0_imag = 2.5, 1.5  # Starting position
    v0_real, v0_imag = 0.0, 1.0  # Starting velocity
    
    particles = [(z0_real, z0_imag, v0_real, v0_imag)]
    
    print(f"Lattice: L = ℤ{p} + ℤ{q}i")
    print(f"Initial position: z₀ = {z0_real} + {z0_imag}i")
    print(f"Initial velocity: v₀ = {v0_real} + {v0_imag}i") 
    print(f"Integration time: T = {T}s with dt = {dt}")
    
    # Create the time-series visualization
    print("\nCreating time-series visualization...")
    
    fig = browser.create_complete_visualization(
        mode='time_series',     # NEW MODE: time-series visualization
        p=p, q=q, N=N,
        nx=40, ny=40,          # Not used for time-series mode
        n_contours=5,          # Not used for time-series mode
        vec_density=10,        # Not used for time-series mode
        vec_width=0.002,       # Not used for time-series mode
        vec_max_len=0.5,       # Not used for time-series mode
        saturation=0.2,        # Not used for time-series mode
        value_floor=0.4,       # Not used for time-series mode
        mag_scale=0.8,         # Not used for time-series mode
        particles=particles,   # Initial conditions
        dt=dt, T=T,           # Integration parameters
        blow_thresh=10.0,     # Blow-up threshold
        emoji_size=20,        # Not used for time-series mode
        show_lattice_trajectories=False  # Not used for time-series mode
    )
    
    # Save the visualization
    filename = 'demo_weierstrass_time_series.png'
    fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    
    print(f"✓ Time-series visualization saved as: {filename}")
    print("\nThe visualization shows 4 panels:")
    print("  • Top-left: Re(℘(z(t))) vs t")
    print("  • Top-right: Im(℘(z(t))) vs t") 
    print("  • Bottom-left: Re(℘'(z(t))) vs t")
    print("  • Bottom-right: Im(℘'(z(t))) vs t")
    print("\nThis answers the original request for graphs where:")
    print("  - Horizontal axis goes from 0 to T")
    print("  - Vertical axis shows Re(℘(z(t))) and Im(℘(z(t)))")
    print("  - Plus bonus: ℘'(z(t)) components as well!")

if __name__ == "__main__":
    demo_time_series_visualization()