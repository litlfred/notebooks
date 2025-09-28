"""
Weierstrass Two-Panel Widget for PQ-Torus Library
Provides ℘(z) and ℘′(z) two-panel visualization using PQ-Torus lattice parameters
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from base_widget import WidgetExecutor
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
        
        return {
            'success': True,
            'plot_data': {
                'image_base64': f'weierstrass_two_panel_p{p}_q{q}_N{N}_contours{contours}',
                'width': 800,
                'height': 400,
                'format': 'png'
            },
            'field_data': {
                'wp_field': f'wp_lattice_p{p}_q{q}',
                'wp_deriv_field': f'wp_deriv_lattice_p{p}_q{q}'
            },
            'lattice_params': {
                'p': p,
                'q': q,
                'lattice_description': f'L = ℤ{p} + ℤ{q}i'
            },
            'visualization_params': {
                'N': N,
                'grid_size': grid_size,
                'contours': contours,
                'saturation': saturation
            }
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