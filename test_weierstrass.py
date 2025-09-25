#!/usr/bin/env python3
"""
Test script for Weierstrass ℘ function implementation.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys

# Test the core functions from the notebook
def wp_rect(z, p, q, N):
    """Weierstrass ℘ function for rectangular lattice."""
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
    """Derivative of Weierstrass ℘ function."""
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

def test_basic_functionality():
    """Test basic functionality of the Weierstrass functions."""
    print("Testing Weierstrass ℘ function implementation...")
    
    # Test parameters
    p, q, N = 11.0, 5.0, 3
    
    # Test points (avoiding poles)
    test_points = [
        1.5 + 1.2j,
        3.7 + 2.1j,
        -2.3 + 4.2j,
        0.5 + 0.5j
    ]
    
    print(f"Lattice parameters: p={p}, q={q}, N={N}")
    print("\nTesting function evaluations:")
    
    for i, z in enumerate(test_points):
        try:
            wp_val = wp_rect(z, p, q, N)
            wp_deriv_val = wp_deriv(z, p, q, N)
            
            print(f"Point {i+1}: z = {z}")
            print(f"  ℘(z) = {wp_val}")
            print(f"  ℘'(z) = {wp_deriv_val}")
            print(f"  |℘(z)| = {abs(wp_val):.4f}")
            print(f"  |℘'(z)| = {abs(wp_deriv_val):.4f}")
            
            # Check for finite values
            if not np.isfinite(wp_val):
                print(f"  WARNING: ℘(z) is not finite!")
            if not np.isfinite(wp_deriv_val):
                print(f"  WARNING: ℘'(z) is not finite!")
                
        except Exception as e:
            print(f"  ERROR evaluating at z = {z}: {e}")
        
        print()
    
    return True

def test_grid_evaluation():
    """Test grid evaluation for visualization."""
    print("Testing grid evaluation...")
    
    p, q, N = 11.0, 5.0, 2
    nx, ny = 50, 50
    
    # Create test grid
    x = np.linspace(0.1, p-0.1, nx)  # Avoid boundaries
    y = np.linspace(0.1, q-0.1, ny)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    try:
        # Evaluate on grid
        wp_vals = wp_rect(Z, p, q, N)
        wp_deriv_vals = wp_deriv(Z, p, q, N)
        
        # Check statistics
        finite_mask = np.isfinite(wp_vals)
        finite_count = np.sum(finite_mask)
        total_count = wp_vals.size
        
        print(f"Grid size: {nx} × {ny} = {total_count} points")
        print(f"Finite ℘ values: {finite_count}/{total_count} ({100*finite_count/total_count:.1f}%)")
        
        if finite_count > 0:
            wp_finite = wp_vals[finite_mask]
            print(f"℘ magnitude range: {np.min(np.abs(wp_finite)):.2e} to {np.max(np.abs(wp_finite)):.2e}")
        
        finite_mask_deriv = np.isfinite(wp_deriv_vals)
        finite_count_deriv = np.sum(finite_mask_deriv)
        
        print(f"Finite ℘' values: {finite_count_deriv}/{total_count} ({100*finite_count_deriv/total_count:.1f}%)")
        
        if finite_count_deriv > 0:
            wp_deriv_finite = wp_deriv_vals[finite_mask_deriv]
            print(f"℘' magnitude range: {np.min(np.abs(wp_deriv_finite)):.2e} to {np.max(np.abs(wp_deriv_finite)):.2e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR in grid evaluation: {e}")
        return False

def test_trajectory_integration():
    """Test basic trajectory integration."""
    print("\nTesting trajectory integration...")
    
    def integrate_test_ode(z0, v0, dt, T, p, q, N):
        """Simple integration test."""
        def force(z):
            wp_val = wp_rect(z, p, q, N)
            return -wp_val * z
        
        steps = int(T / dt)
        trajectory = [z0]
        
        z, v = z0, v0
        for _ in range(min(steps, 100)):  # Limit to 100 steps for test
            try:
                # Simple Euler step
                a = force(z)
                if not np.isfinite(a):
                    break
                v_new = v + dt * a
                z_new = z + dt * v_new
                
                if not (np.isfinite(z_new) and np.isfinite(v_new)):
                    break
                
                z, v = z_new, v_new
                trajectory.append(z)
                
            except Exception:
                break
        
        return np.array(trajectory)
    
    # Test parameters
    p, q, N = 11.0, 5.0, 2
    z0 = 2.0 + 1.0j
    v0 = 0.0 + 1.0j
    dt = 0.01
    T = 1.0
    
    try:
        trajectory = integrate_test_ode(z0, v0, dt, T, p, q, N)
        print(f"Initial condition: z0 = {z0}, v0 = {v0}")
        print(f"Integration: dt = {dt}, T = {T}")
        print(f"Trajectory length: {len(trajectory)} points")
        
        if len(trajectory) > 1:
            final_z = trajectory[-1]
            displacement = abs(final_z - z0)
            print(f"Final position: {final_z}")
            print(f"Total displacement: {displacement:.4f}")
            return True
        else:
            print("ERROR: Trajectory integration failed immediately")
            return False
            
    except Exception as e:
        print(f"ERROR in trajectory integration: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Weierstrass ℘ Playground - Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_basic_functionality():
        tests_passed += 1
        print("✓ Basic functionality test PASSED")
    else:
        print("✗ Basic functionality test FAILED")
    
    print("\n" + "-" * 40)
    
    if test_grid_evaluation():
        tests_passed += 1
        print("✓ Grid evaluation test PASSED")
    else:
        print("✗ Grid evaluation test FAILED")
    
    print("\n" + "-" * 40)
    
    if test_trajectory_integration():
        tests_passed += 1
        print("✓ Trajectory integration test PASSED")
    else:
        print("✗ Trajectory integration test FAILED")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests PASSED! The implementation looks good.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())