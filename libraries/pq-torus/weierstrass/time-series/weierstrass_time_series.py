"""
Weierstrass Time-Series Widget for PQ-Torus Library
Provides ℘(z(t)) and ℘′(z(t)) time-series visualization using PQ-Torus lattice parameters
"""

import sys
import os
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Add parent directories to path for imports  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core'))

from base_widget import WidgetExecutor
from weierstrass_playground import core, visualization, integration
from typing import Dict, Any
from datetime import datetime

class PQTorusWeierstrassTimeSeriesWidget(WidgetExecutor):
    """Time-series ℘(z(t)) and ℘′(z(t)) visualization using PQ-Torus lattice"""
    
    # Override input/output variable declarations
    input_variables = {
        'p': 11,
        'q': 5,
        'N': 3,
        'initial_conditions': {
            'z0_real': 2.5,
            'z0_imag': 1.5,
            'v0_real': 0.0,
            'v0_imag': 1.0
        },
        'integration_params': {
            'dt': 0.01,
            'T': 2.0,
            'blow_thresh': 10.0
        },
        'visualization_params': {
            'figure_size': 8,
            'line_width': 1.5,
            'grid': True
        }
    }
    
    output_variables = {
        'success': True,
        'plot_data': {},
        'trajectory_data': {},
        'metadata': {}
    }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        start_time = datetime.now()
        
        # Extract input parameters
        p = validated_input.get('p', 11)
        q = validated_input.get('q', 5)
        N = validated_input.get('N', 3)
        
        initial_conditions = validated_input.get('initial_conditions', {})
        z0_real = initial_conditions.get('z0_real', 2.5)
        z0_imag = initial_conditions.get('z0_imag', 1.5)
        v0_real = initial_conditions.get('v0_real', 0.0)
        v0_imag = initial_conditions.get('v0_imag', 1.0)
        
        integration_params = validated_input.get('integration_params', {})
        dt = integration_params.get('dt', 0.01)
        T = integration_params.get('T', 2.0)
        blow_thresh = integration_params.get('blow_thresh', 10.0)
        
        visualization_params = validated_input.get('visualization_params', {})
        figure_size = visualization_params.get('figure_size', 8)
        line_width = visualization_params.get('line_width', 1.5)
        grid = visualization_params.get('grid', True)
        
        try:
            # Validate lattice parameters
            core.validate_parameters(p, q, N)
            
            # Set up initial conditions
            z0 = complex(z0_real, z0_imag)
            v0 = complex(v0_real, v0_imag)
            
            # Integrate trajectory
            trajectory, blowup_point = integration.integrate_second_order_with_blowup(
                z0, v0, dt, T, p, q, N, blow_thresh
            )
            
            if len(trajectory) < 10:
                raise ValueError("Trajectory too short for meaningful time-series visualization")
            
            # Create time-series visualization
            fig = visualization.create_time_series_visualization(trajectory, dt, p, q, N, figure_size)
            
            # Convert plot to base64 string
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            buffer.close()
            
            # Get image dimensions
            width = int(fig.get_figwidth() * fig.dpi)
            height = int(fig.get_figheight() * fig.dpi)
            
            plt.close(fig)  # Free memory
            
            # Compute function values along trajectory for statistics
            wp_values = np.array([core.wp_rect(z, p, q, N) for z in trajectory])
            wp_deriv_values = np.array([core.wp_deriv(z, p, q, N) for z in trajectory])
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
            
            return {
                'success': True,
                'execution_time': execution_time,
                'timestamp': end_time.isoformat(),
                'plot_data': {
                    'image_base64': image_base64,
                    'width': width,
                    'height': height,
                    'mime_type': 'image/png'
                },
                'trajectory_data': {
                    'trajectory_length': len(trajectory),
                    'time_range': {
                        'start': 0.0,
                        'end': T,
                        'dt': dt
                    },
                    'function_statistics': {
                        'wp_values': {
                            'real_range': [float(np.min(np.real(wp_values))), float(np.max(np.real(wp_values)))],
                            'imag_range': [float(np.min(np.imag(wp_values))), float(np.max(np.imag(wp_values)))],
                            'magnitude_max': float(np.max(np.abs(wp_values)))
                        },
                        'wp_deriv_values': {
                            'real_range': [float(np.min(np.real(wp_deriv_values))), float(np.max(np.real(wp_deriv_values)))],
                            'imag_range': [float(np.min(np.imag(wp_deriv_values))), float(np.max(np.imag(wp_deriv_values)))],
                            'magnitude_max': float(np.max(np.abs(wp_deriv_values)))
                        }
                    },
                    'blow_up_detected': blowup_point is not None
                },
                'metadata': {
                    'lattice_params': {
                        'p': p,
                        'q': q,
                        'N': N,
                        'lattice_description': f'L = ℤ{p} + ℤ{q}i'
                    },
                    'initial_conditions': {
                        'z0': f'{z0_real} + {z0_imag}i',
                        'v0': f'{v0_real} + {v0_imag}i'
                    },
                    'computation_method': 'runge_kutta_4',
                    'widget_instance': f'time_series_p{p}_q{q}_N{N}'
                }
            }
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                'success': False,
                'execution_time': execution_time,
                'timestamp': end_time.isoformat(),
                'error': str(e),
                'error_type': type(e).__name__,
                'plot_data': {
                    'image_base64': '',
                    'width': 0,
                    'height': 0,
                    'mime_type': 'image/png'
                },
                'trajectory_data': {
                    'trajectory_length': 0,
                    'time_range': {'start': 0.0, 'end': 0.0, 'dt': dt},
                    'blow_up_detected': False
                },
                'metadata': {
                    'lattice_params': {'p': p, 'q': q, 'N': N},
                    'computation_method': 'runge_kutta_4',
                    'widget_instance': f'time_series_error_p{p}_q{q}_N{N}'
                }
            }

def create_weierstrass_time_series_widget(widget_schema: Dict[str, Any]) -> PQTorusWeierstrassTimeSeriesWidget:
    """Factory function to create weierstrass time-series widget instance"""
    return PQTorusWeierstrassTimeSeriesWidget(widget_schema)