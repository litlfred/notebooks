"""
Weierstrass Two-Panel Widget for PQ-Torus Library
Provides ℘(z) and ℘′(z) two-panel visualization using PQ-Torus lattice parameters
"""

import sys
import os
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from base_widget import WidgetExecutor
from weierstrass_math import field_grid, soft_background, add_topo_contours, create_two_panel_figure
from typing import Dict, Any
from datetime import datetime

class PQTorusWeierstrassTwoPanelWidget(WidgetExecutor):
    """Two-panel ℘(z) and ℘′(z) visualization using PQ-Torus lattice"""
    
    # Override input/output variable declarations
    input_variables = {
        'p': 11,
        'q': 5,
        'N': 3,
        'grid_size': {'x': 100, 'y': 100},
        'contours': 10,
        'saturation': 0.3
    }
    
    output_variables = {
        'success': True,
        'plot_data': {},
        'field_data': {},
        'lattice_params': {},
        'visualization_params': {}
    }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        p = validated_input.get('p', 11)
        q = validated_input.get('q', 5)
        N = validated_input.get('N', 3)
        grid_size = validated_input.get('grid_size', {'x': 100, 'y': 100})
        contours = validated_input.get('contours', 10)
        saturation = validated_input.get('saturation', 0.3)
        
        try:
            # Create figure
            fig, (ax1, ax2) = create_two_panel_figure(p, q)
            
            # Compute ℘(z) field
            X1, Y1, F1, M1 = field_grid(p, q, 'wp', N, grid_size['x'], grid_size['y'])
            
            # Compute ℘'(z) field
            X2, Y2, F2, M2 = field_grid(p, q, 'wp_deriv', N, grid_size['x'], grid_size['y'])
            
            # Create backgrounds
            mag_scale = 10.0
            value_floor = 0.1
            bg1 = soft_background(F1, M1, saturation, mag_scale, value_floor)
            bg2 = soft_background(F2, M2, saturation, mag_scale, value_floor)
            
            # Display backgrounds
            ax1.imshow(bg1, extent=[0, p, 0, q], origin='lower', aspect='equal')
            ax2.imshow(bg2, extent=[0, p, 0, q], origin='lower', aspect='equal')
            
            # Add contours
            add_topo_contours(ax1, X1, Y1, F1, M1, contours)
            add_topo_contours(ax2, X2, Y2, F2, M2, contours)
            
            # Convert plot to base64 string
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)
            
            return {
                'success': True,
                'plot_data': {
                    'image_base64': image_base64,
                    'width': 1200,
                    'height': 500,
                    'format': 'png'
                },
                'field_data': {
                    'wp_field': 'computed',
                    'wp_deriv_field': 'computed',
                    'grid_size': grid_size
                },
                'lattice_params': {
                    'p': p,
                    'q': q,
                    'N': N,
                    'lattice_description': f'L = ℤ{p} + ℤ{q}i'
                },
                'visualization_params': {
                    'contours': contours,
                    'saturation': saturation,
                    'mag_scale': mag_scale
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Computation failed: {str(e)}',
                'lattice_params': {'p': p, 'q': q, 'N': N}
            }
    
    def action_render_two_panel(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action method for render-two-panel action"""
        # Do action-specific validation
        p = validated_input.get('p', self.input_variables['p'])
        q = validated_input.get('q', self.input_variables['q'])
        
        if not (2 <= p <= 100) or not (2 <= q <= 100):
            return {
                'success': False,
                'error': 'Prime parameters p and q must be between 2 and 100'
            }
        
        # Execute the main rendering logic
        return self._execute_impl(validated_input)

def create_weierstrass_two_panel_widget(widget_schema: Dict[str, Any]) -> PQTorusWeierstrassTwoPanelWidget:
    """Factory function to create weierstrass two-panel widget instance"""
    return PQTorusWeierstrassTwoPanelWidget(widget_schema)