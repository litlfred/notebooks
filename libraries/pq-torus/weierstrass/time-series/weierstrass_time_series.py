"""
Weierstrass Time-Series Widget for PQ-Torus Library
Provides time evolution visualization of ℘(z(t)) along particle trajectories
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core'))

from base_widget import WidgetExecutor
from typing import Dict, Any, List, Tuple
from datetime import datetime
import numpy as np
import json

class PQTorusWeierstrassTimeSeriesWidget(WidgetExecutor):
    """Time-series visualization of ℘(z(t)) evolution using PQ-Torus lattice"""
    
    # Override input/output variable declarations
    input_variables = {
        'p': 11,
        'q': 5,
        'N': 3,
        'particles': [
            {'z0': {'real': 2.0, 'imag': 1.0}, 'v0': {'real': 0.0, 'imag': 1.0}},
            {'z0': {'real': 3.0, 'imag': 2.0}, 'v0': {'real': 1.0, 'imag': 0.0}}
        ],
        'dt': 0.01,
        'T': 10.0,
        'blow_thresh': 10.0,
        'show_real': True,
        'show_imaginary': True,
        'grid': True,
        'legend': True
    }
    
    output_variables = {
        'success': True,
        'plot_data': {},
        'time_series_data': {},
        'trajectory_stats': {},
        'lattice_params': {},
        'visualization_params': {}
    }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute time-series visualization with trajectory integration"""
        
        # Extract parameters
        p = validated_input.get('p', 11)
        q = validated_input.get('q', 5) 
        N = validated_input.get('N', 3)
        particles = validated_input.get('particles', [])
        dt = validated_input.get('dt', 0.01)
        T = validated_input.get('T', 10.0)
        blow_thresh = validated_input.get('blow_thresh', 10.0)
        show_real = validated_input.get('show_real', True)
        show_imaginary = validated_input.get('show_imaginary', True)
        grid = validated_input.get('grid', True)
        legend = validated_input.get('legend', True)
        
        try:
            # Integrate trajectories and evaluate ℘(z(t))
            time_series_results = []
            trajectory_stats = []
            
            for i, particle in enumerate(particles):
                z0_complex = complex(particle['z0']['real'], particle['z0']['imag'])
                v0_complex = complex(particle['v0']['real'], particle['v0']['imag'])
                
                # Simulate trajectory integration and ℘ evaluation
                times, trajectory, wp_values, blowup_point = self._integrate_and_evaluate_wp(
                    z0_complex, v0_complex, dt, T, p, q, N, blow_thresh
                )
                
                time_series_results.append({
                    'particle_id': i,
                    'times': times.tolist() if hasattr(times, 'tolist') else times,
                    'trajectory': [{'real': z.real, 'imag': z.imag} for z in trajectory],
                    'wp_real': [wp.real for wp in wp_values],
                    'wp_imag': [wp.imag for wp in wp_values],
                    'blowup_point': blowup_point
                })
                
                # Compute trajectory statistics
                trajectory_stats.append({
                    'particle_id': i,
                    'initial_z': {'real': z0_complex.real, 'imag': z0_complex.imag},
                    'initial_v': {'real': v0_complex.real, 'imag': v0_complex.imag},
                    'final_time': times[-1] if len(times) > 0 else 0,
                    'steps_computed': len(times),
                    'blowup_detected': blowup_point is not None,
                    'max_wp_magnitude': max(abs(wp) for wp in wp_values) if wp_values else 0
                })
            
            return {
                'success': True,
                'plot_data': {
                    'image_base64': f'weierstrass_time_series_p{p}_q{q}_N{N}_T{T}_particles{len(particles)}',
                    'width': 1200,
                    'height': 600,
                    'format': 'png',
                    'panels': 2 if show_real and show_imaginary else 1
                },
                'time_series_data': time_series_results,
                'trajectory_stats': trajectory_stats,
                'lattice_params': {
                    'p': p,
                    'q': q,
                    'N': N,
                    'lattice_type': 'rectangular'
                },
                'visualization_params': {
                    'dt': dt,
                    'T': T,
                    'blow_thresh': blow_thresh,
                    'show_real': show_real,
                    'show_imaginary': show_imaginary,
                    'grid': grid,
                    'legend': legend,
                    'particle_count': len(particles)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'lattice_params': {'p': p, 'q': q, 'N': N}
            }
    
    def _integrate_and_evaluate_wp(self, z0: complex, v0: complex, dt: float, T: float, 
                                   p: float, q: float, N: int, blow_thresh: float = 10.0) -> Tuple[np.ndarray, List[complex], List[complex], Any]:
        """
        Integrate trajectory and evaluate ℘(z(t)) along the path.
        
        This is a simplified simulation for the widget framework.
        In a full implementation, this would use the actual Weierstrass function computation.
        """
        steps = int(T / dt)
        times = np.linspace(0, T, steps)
        
        # Simulate trajectory (simplified)
        trajectory = []
        wp_values = []
        blowup_point = None
        
        z, v = z0, v0
        
        for i, t in enumerate(times):
            trajectory.append(z)
            
            # Simulate ℘(z) evaluation (simplified for demonstration)
            # In real implementation, this would call the actual Weierstrass function
            wp_val = self._mock_weierstrass_p(z, p, q, N)
            wp_values.append(wp_val)
            
            # Simple integration step (Euler method for demo)
            # In real implementation: z''(t) = -℘(z(t)) * z(t)
            a = -wp_val * z  # Force from Weierstrass potential
            v_new = v + dt * a
            z_new = z + dt * v_new
            
            # Check for blow-up
            if abs(z_new - z) > blow_thresh:
                blowup_point = {'time': t, 'position': z_new}
                break
                
            z, v = z_new, v_new
            
            # Limit steps for demonstration
            if i > 1000:
                break
        
        return times[:len(trajectory)], trajectory, wp_values, blowup_point
    
    def _mock_weierstrass_p(self, z: complex, p: float, q: float, N: int) -> complex:
        """
        Mock Weierstrass ℘ function for demonstration.
        In real implementation, this would be the actual mathematical computation.
        """
        # Simple approximation for demonstration
        # Real implementation would use the proper lattice sum
        if abs(z) < 1e-6:
            return complex(1e6, 0)  # Simulate pole
        
        # Simplified approximation
        result = 1.0 / (z * z)
        
        # Add some lattice effects
        for m in range(-N, N+1):
            for n in range(-N, N+1):
                if m == 0 and n == 0:
                    continue
                omega = m * p + n * q * 1j
                if abs(z - omega) > 1e-6:
                    result += 1.0 / ((z - omega) ** 2) - 1.0 / (omega ** 2)
        
        return result