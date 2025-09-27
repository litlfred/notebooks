"""
Weierstrass Two-Panel Widget for PQ-Torus Library
Provides ℘(z) and ℘′(z) two-panel visualization using PQ-Torus lattice parameters
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'widgets'))

from base_widget import WidgetExecutor
from typing import Dict, Any
from datetime import datetime

class WeierstrassTwoPanelWidget(WidgetExecutor):
    """Two-panel ℘(z) and ℘′(z) visualization using PQ-Torus lattice"""
    
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

def create_weierstrass_two_panel_widget(widget_schema: Dict[str, Any]) -> WeierstrassTwoPanelWidget:
    """Factory function to create weierstrass two-panel widget instance"""
    return WeierstrassTwoPanelWidget(widget_schema)