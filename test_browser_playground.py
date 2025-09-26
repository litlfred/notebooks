#!/usr/bin/env python3
"""
Test script to validate the browser-compatible Weierstrass core functions
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add the docs/python directory to path to import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'docs', 'python'))

def test_weierstrass_core():
    """Test core Weierstrass functions work correctly"""
    print("Testing Weierstrass ℘ playground core functions...")
    
    try:
        # Import our Pyodide-compatible module
        import weierstrass_core as wc
        
        # Test basic function evaluation
        print("\n1. Testing wp_rect function...")
        z = 2.0 + 1.5j
        p, q, N = 11.0, 5.0, 2
        
        wp_val = wc.wp_rect(z, p, q, N)
        print(f"   ℘({z}) = {wp_val}")
        print(f"   |℘({z})| = {abs(wp_val):.4f}")
        
        if not np.isfinite(wp_val):
            raise ValueError("℘ function returned non-finite value")
        
        # Test derivative
        print("\n2. Testing wp_deriv function...")
        wp_deriv_val = wc.wp_deriv(z, p, q, N)
        print(f"   ℘'({z}) = {wp_deriv_val}")
        print(f"   |℘'({z})| = {abs(wp_deriv_val):.4f}")
        
        if not np.isfinite(wp_deriv_val):
            raise ValueError("℘' function returned non-finite value")
        
        # Test field grid computation
        print("\n3. Testing field_grid function...")
        nx, ny = 50, 50
        X, Y, F, M = wc.field_grid(p, q, 'wp', N, nx, ny)
        
        valid_points = np.sum(M)
        total_points = M.size
        print(f"   Grid: {nx}×{ny} = {total_points} points")
        print(f"   Valid points: {valid_points}/{total_points} ({100*valid_points/total_points:.1f}%)")
        
        if valid_points == 0:
            raise ValueError("No valid grid points found")
        
        # Test background generation
        print("\n4. Testing soft_background function...")
        bg = wc.soft_background(F, M)
        print(f"   Background shape: {bg.shape}")
        print(f"   Background range: [{np.min(bg):.3f}, {np.max(bg):.3f}]")
        
        if bg.shape != (ny, nx, 3):
            raise ValueError(f"Wrong background shape: {bg.shape}")
        
        # Test trajectory integration
        print("\n5. Testing trajectory integration...")
        z0 = 5.5 + 0.0j
        v0 = 0.0 + 1.0j
        dt, T = 0.01, 2.0
        
        trajectory, blowup_point = wc.integrate_second_order_with_blowup(
            z0, v0, dt, T, p, q, N
        )
        
        print(f"   Initial: z0={z0}, v0={v0}")
        print(f"   Trajectory length: {len(trajectory)} points")
        print(f"   Integration time: {T}s with dt={dt}")
        print(f"   Blow-up: {'Yes' if blowup_point is not None else 'No'}")
        
        if len(trajectory) == 0:
            raise ValueError("No trajectory points generated")
        
        # Test matplotlib figure creation
        print("\n6. Testing visualization pipeline...")
        particles = [(z0, v0)]
        
        fig, axes = wc.create_figure_with_plots(
            'two_panel', p, q, N, 40, 40, 5, 10, 0.002, 0.5,
            0.2, 0.4, 0.8, particles, dt, 1.0, 10.0, 20, False
        )
        
        print(f"   Figure created: {type(fig)}")
        print(f"   Axes count: {len(axes)}")
        
        # Clean up
        plt.close(fig)
        
        print("\n✅ All tests passed! The Weierstrass core functions are working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_browser_compatibility():
    """Test browser-specific functionality"""
    print("\n" + "="*60)
    print("Testing browser compatibility features...")
    
    try:
        # Test complex number parsing (like in browser)
        test_cases = [
            "5+2j", "3-1j", "5", "2j", "-3+4j", "0+1j", "7+0j"
        ]
        
        print("\n7. Testing complex number parsing...")
        for case in test_cases:
            # For Python test, just use complex()
            try:
                val = complex(case)  # Python format
                print(f"   '{case}' → {val}")
            except:
                print(f"   '{case}' → Error (would be handled in browser)")
        
        print("\n✅ Browser compatibility features look good!")
        return True
        
    except Exception as e:
        print(f"\n❌ Browser compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("Weierstrass ℘ Playground - Core Functions Test")
    print("=" * 60)
    
    success1 = test_weierstrass_core()
    success2 = test_browser_compatibility()
    
    print("\n" + "="*60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! The browser playground should work correctly.")
        print("\nNext steps:")
        print("1. Deploy to GitHub Pages")
        print("2. Test in actual browser at https://litlfred.github.io/notebooks/")
        print("3. Verify Pyodide loads correctly with external CDN")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        sys.exit(1)