"""
Data Visualization Widget Implementation
Plotting and data generation widgets for mathematical analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from base_widget import WidgetExecutor
from typing import Dict, Any
import random
import math

class DataVisualizationWidget(WidgetExecutor):
    """
    Data visualization widget for plotting and data generation.
    
    Supports multiple visualization types and synthetic data generation.
    """
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        # Check if this is a plot request or data generation request
        if 'data' in validated_input:
            return self._handle_plot_request(validated_input)
        elif 'generator_type' in validated_input:
            return self._handle_data_generation(validated_input)
        else:
            return {
                'success': False,
                'error': 'Unknown visualization request type'
            }
    
    def _handle_plot_request(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        data = validated_input.get('data', [])
        plot_type = validated_input.get('plot_type', 'line')
        styling = validated_input.get('styling', {})
        
        return {
            'success': True,
            'plot_data': {
                'image_base64': f'plot_{plot_type}_{len(data)}_points',
                'width': 800,
                'height': 600,
                'format': 'png'
            },
            'plot_config': {
                'plot_type': plot_type,
                'data_points': len(data),
                'styling': styling
            },
            'statistics': {
                'data_series': len(data),
                'total_points': sum(len(series.get('x', [])) for series in data if isinstance(series, dict))
            }
        }
    
    def _handle_data_generation(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        generator_type = validated_input.get('generator_type', 'random')
        sample_size = validated_input.get('sample_size', 100)
        parameters = validated_input.get('parameters', {})
        
        # Generate synthetic data based on type
        if generator_type == 'random':
            data = [{'x': i, 'y': random.random()} for i in range(sample_size)]
        elif generator_type == 'linear':
            slope = parameters.get('slope', 1)
            intercept = parameters.get('intercept', 0)
            data = [{'x': i, 'y': slope * i + intercept + random.random() * 0.1} for i in range(sample_size)]
        elif generator_type == 'sinusoidal':
            amplitude = parameters.get('amplitude', 1)
            frequency = parameters.get('frequency', 0.1)
            data = [{'x': i, 'y': amplitude * math.sin(frequency * i) + random.random() * 0.05} for i in range(sample_size)]
        else:
            data = [{'x': i, 'y': 0} for i in range(sample_size)]
            
        return {
            'success': True,
            'data': data,
            'generator_config': {
                'generator_type': generator_type,
                'sample_size': sample_size,
                'parameters': parameters
            },
            'statistics': {
                'mean_y': sum(point['y'] for point in data) / len(data) if data else 0,
                'min_y': min(point['y'] for point in data) if data else 0,
                'max_y': max(point['y'] for point in data) if data else 0
            }
        }

def create_data_visualization_widget(widget_schema: Dict[str, Any]) -> DataVisualizationWidget:
    """Factory function to create data visualization widget instance"""
    return DataVisualizationWidget(widget_schema)