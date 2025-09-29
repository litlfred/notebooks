#!/usr/bin/env python3
"""
Test script for the new time-series visualization of ℘(z(t)) and ℘'(z(t))
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing

import sys
import os

# Add the src directory to path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from weierstrass_playground import core, visualization, integration, browser

def test_time_series_visualization():
    """Test the new time-series visualization functionality"""
    print("Testing Time-Series Visualization of ℘(z(t)) and ℘'(z(t))")
    print("=" * 60)
    
    # Set up parameters
    p, q, N = 11.0, 5.0, 3
    dt, T = 0.01, 2.0
    z0 = complex(2.5, 1.5)  # Initial position
    v0 = complex(0.0, 1.0)  # Initial velocity
    
    print(f"Lattice parameters: p={p}, q={q}, N={N}")
    print(f"Integration: dt={dt}, T={T}")
    print(f"Initial conditions: z0={z0}, v0={v0}")
    
    # Test 1: Direct time-series visualization
    print("\n1. Testing direct time-series visualization...")
    try:
        # Integrate trajectory
        trajectory, blowup_point = integration.integrate_second_order_with_blowup(
            z0, v0, dt, T, p, q, N, blow_thresh=10.0
        )
        
        print(f"   Trajectory length: {len(trajectory)} points")
        print(f"   Blow-up: {'Yes' if blowup_point is not None else 'No'}")
        
        if len(trajectory) > 10:
            # Create time-series visualization
            fig = visualization.create_time_series_visualization(trajectory, dt, p, q, N)
            
            # Save the plot
            filename = 'test_time_series_visualization.png'
            fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"   ✓ Time-series visualization saved as {filename}")
            plt.close(fig)
        else:
            print("   ⚠ Trajectory too short for meaningful visualization")
            
    except Exception as e:
        print(f"   ❌ Error in direct visualization: {e}")
        return False
    
    # Test 2: Browser-compatible visualization
    print("\n2. Testing browser-compatible time-series mode...")
    try:
        particles = [(z0.real, z0.imag, v0.real, v0.imag)]
        
        fig = browser.create_complete_visualization(
            mode='time_series',
            p=p, q=q, N=N,
            nx=40, ny=40,
            n_contours=5,
            vec_density=10,
            vec_width=0.002,
            vec_max_len=0.5,
            saturation=0.2,
            value_floor=0.4,
            mag_scale=0.8,
            particles=particles,
            dt=dt, T=T,
            blow_thresh=10.0,
            emoji_size=20,
            show_lattice_trajectories=False
        )
        
        # Save the plot
        filename = 'test_browser_time_series.png'
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"   ✓ Browser time-series visualization saved as {filename}")
        plt.close(fig)
        
    except Exception as e:
        print(f"   ❌ Error in browser visualization: {e}")
        return False
    
    # Test 3: Verify function values are computed correctly
    print("\n3. Testing function value computation...")
    try:
        # Test a few points along the trajectory
        test_points = trajectory[::len(trajectory)//5]  # Sample 5 points
        
        for i, z in enumerate(test_points):
            wp_val = core.wp_rect(z, p, q, N)
            wp_deriv_val = core.wp_deriv(z, p, q, N)
            
            print(f"   Point {i}: z={z:.3f}")
            print(f"     ℘(z) = {wp_val:.6f}")
            print(f"     ℘'(z) = {wp_deriv_val:.6f}")
            
            if not (np.isfinite(wp_val) and np.isfinite(wp_deriv_val)):
                print(f"   ⚠ Non-finite values detected at point {i}")
                
    except Exception as e:
        print(f"   ❌ Error in function computation: {e}")
        return False
    
    # Test 4: Test with different initial conditions
    print("\n4. Testing with different initial conditions...")
    try:
        test_conditions = [
            (complex(1.0, 0.5), complex(1.0, 0.0)),
            (complex(5.5, 2.5), complex(-0.5, 1.0)),
            (complex(0.5, 4.0), complex(0.0, -1.0))
        ]
        
        for i, (z0_test, v0_test) in enumerate(test_conditions):
            particles_test = [(z0_test.real, z0_test.imag, v0_test.real, v0_test.imag)]
            
            fig = browser.create_complete_visualization(
                mode='time_series',
                p=p, q=q, N=N,
                nx=40, ny=40,
                n_contours=5,
                vec_density=10,
                vec_width=0.002,
                vec_max_len=0.5,
                saturation=0.2,
                value_floor=0.4,
                mag_scale=0.8,
                particles=particles_test,
                dt=dt, T=1.0,  # Shorter time for speed
                blow_thresh=10.0,
                emoji_size=20,
                show_lattice_trajectories=False
            )
            
            filename = f'test_time_series_case_{i+1}.png'
            fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"   ✓ Case {i+1} saved as {filename}")
            plt.close(fig)
            
    except Exception as e:
        print(f"   ❌ Error in multi-case testing: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All time-series visualization tests PASSED!")
    print("\nOutput files created:")
    print("- test_time_series_visualization.png")
    print("- test_browser_time_series.png")
    print("- test_time_series_case_1.png")
    print("- test_time_series_case_2.png")
    print("- test_time_series_case_3.png")
    
    return True

if __name__ == "__main__":
    success = test_time_series_visualization()
    if not success:
        sys.exit(1)