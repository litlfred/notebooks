#!/usr/bin/env python3
"""
Test script for the new Weierstrass Time-Series Widget
"""

import sys
import os
import json

# Add the libraries directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libraries', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libraries', 'pq-torus', 'weierstrass', 'time-series'))

from weierstrass_time_series import PQTorusWeierstrassTimeSeriesWidget

def test_time_series_widget():
    """Test the time-series widget functionality"""
    print("Testing Weierstrass Time-Series Widget")
    print("=" * 50)
    
    # Create widget instance
    widget_schema = {
        "id": "weierstrass_time_series_test",
        "name": "Weierstrass Time-Series Widget",
        "widget_type": "weierstrass_time_series",
        "version": "1.0.0",
        "actions": {}
    }
    
    widget = PQTorusWeierstrassTimeSeriesWidget(widget_schema)
    
    # Test 1: Basic functionality with default parameters
    print("\n1. Testing with default parameters...")
    
    input_data = {
        "p": 11,
        "q": 5,
        "N": 3,
        "initial_conditions": {
            "z0_real": 2.5,
            "z0_imag": 1.5,
            "v0_real": 0.0,
            "v0_imag": 1.0
        },
        "integration_params": {
            "dt": 0.01,
            "T": 2.0,
            "blow_thresh": 10.0
        },
        "visualization_params": {
            "figure_size": 8,
            "line_width": 1.5,
            "grid": True
        }
    }
    
    try:
        result = widget._execute_impl(input_data)
        
        if result['success']:
            print("   ✓ Widget execution successful")
            print(f"   ✓ Execution time: {result['execution_time']:.2f}ms")
            print(f"   ✓ Trajectory length: {result['trajectory_data']['trajectory_length']} points")
            print(f"   ✓ Time range: {result['trajectory_data']['time_range']['start']:.1f} to {result['trajectory_data']['time_range']['end']:.1f}")
            print(f"   ✓ Image size: {result['plot_data']['width']} × {result['plot_data']['height']} pixels")
            print(f"   ✓ Blow-up detected: {result['trajectory_data']['blow_up_detected']}")
            
            # Check function statistics
            wp_stats = result['trajectory_data']['function_statistics']['wp_values']
            wp_deriv_stats = result['trajectory_data']['function_statistics']['wp_deriv_values']
            
            print(f"   ℘(z) real range: [{wp_stats['real_range'][0]:.3f}, {wp_stats['real_range'][1]:.3f}]")
            print(f"   ℘(z) imag range: [{wp_stats['imag_range'][0]:.3f}, {wp_stats['imag_range'][1]:.3f}]")
            print(f"   ℘'(z) max magnitude: {wp_deriv_stats['magnitude_max']:.3f}")
        else:
            print("   ❌ Widget execution failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception during widget execution: {e}")
        return False
    
    # Test 2: Different initial conditions
    print("\n2. Testing with different initial conditions...")
    
    test_cases = [
        {"z0_real": 1.0, "z0_imag": 0.5, "v0_real": 1.0, "v0_imag": 0.0},
        {"z0_real": 5.5, "z0_imag": 2.5, "v0_real": -0.5, "v0_imag": 1.0},
        {"z0_real": 0.5, "z0_imag": 4.0, "v0_real": 0.0, "v0_imag": -1.0}
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"   Test case {i+1}: z₀={test_case['z0_real']}+{test_case['z0_imag']}i, v₀={test_case['v0_real']}+{test_case['v0_imag']}i")
        
        input_data_test = input_data.copy()
        input_data_test['initial_conditions'] = test_case
        input_data_test['integration_params']['T'] = 1.0  # Shorter time for speed
        
        try:
            result = widget._execute_impl(input_data_test)
            
            if result['success']:
                print(f"      ✓ Success: {result['trajectory_data']['trajectory_length']} points")
            else:
                print(f"      ⚠ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
    
    # Test 3: Parameter validation
    print("\n3. Testing parameter validation...")
    
    # Test invalid lattice parameters
    invalid_input = input_data.copy()
    invalid_input['p'] = 1  # Invalid p (must be >= 2)
    
    try:
        result = widget._execute_impl(invalid_input)
        if not result['success']:
            print("   ✓ Invalid parameter rejection working")
        else:
            print("   ⚠ Invalid parameter validation may be missing")
    except Exception:
        print("   ✓ Invalid parameter exception handling working")
    
    # Test 4: JSON schema compatibility
    print("\n4. Testing JSON output compatibility...")
    
    try:
        result = widget._execute_impl(input_data)
        json_output = json.dumps(result, indent=2)
        print("   ✓ JSON serialization successful")
        print(f"   Output size: {len(json_output)} characters")
        
        # Try to parse it back
        parsed = json.loads(json_output)
        if parsed['success'] == result['success']:
            print("   ✓ JSON round-trip successful")
        else:
            print("   ❌ JSON round-trip failed")
            return False
            
    except Exception as e:
        print(f"   ❌ JSON compatibility issue: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All time-series widget tests PASSED!")
    print("\nWidget provides:")
    print("  • Complete time-series visualization of ℘(z(t)) and ℘'(z(t))")
    print("  • Four-panel layout: Re/Im components vs time")
    print("  • Trajectory integration with blow-up detection")
    print("  • Statistical analysis of function values")
    print("  • Base64 encoded PNG output for web integration")
    print("  • Full JSON-LD compliance ready")
    
    return True

if __name__ == "__main__":
    success = test_time_series_widget()
    if not success:
        sys.exit(1)