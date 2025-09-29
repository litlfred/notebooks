"""
Notebook Widget Implementation
Renders notebooks as interactive boards with full-screen and windowed modes
"""

import sys
import os
import json
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from base_widget import WidgetExecutor


class NotebookWidget(WidgetExecutor):
    """Notebook widget that can render notebooks as interactive boards"""
    
    # Override input/output variable declarations
    input_variables = {
        'notebook_data': {},
        'render_mode': 'windowed',  # 'windowed' or 'fullscreen'
        'show_panels': True,
        'panel_config': {
            'show_library': True,
            'show_controls': True,
            'library_collapsed': False
        }
    }
    
    output_variables = {
        'success': True,
        'widget_instances': {},  # Dictionary mapping widget IDs to their data IRIs
        'board_state': {},
        'rendered_mode': 'windowed'
    }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notebook rendering"""
        notebook_data = validated_input.get('notebook_data', {})
        render_mode = validated_input.get('render_mode', 'windowed')
        show_panels = validated_input.get('show_panels', True)
        panel_config = validated_input.get('panel_config', {})
        
        try:
            # Extract widgets from notebook @graph
            graph = notebook_data.get('@graph', [])
            widgets = [item for item in graph if self._is_widget_entity(item)]
            
            # Create widget instance mapping (widget ID -> data IRI)
            widget_instances = {}
            for widget in widgets:
                widget_id = widget.get('widget_id', widget.get('@id', ''))
                widget_instances[widget_id] = {
                    'input_iri': widget.get('input', {}).get('@id', ''),
                    'output_iri': widget.get('output', {}).get('@id', ''),
                    'widget_type': widget.get('widget_type', ''),
                    'layout': widget.get('layout', {})
                }
            
            # Prepare board state
            board_state = {
                'notebook_id': notebook_data.get('@id', ''),
                'title': notebook_data.get('dct:title', 'Untitled Notebook'),
                'widgets': widgets,
                'connections': self._extract_connections(graph),
                'layout': notebook_data.get('notebook:layout', {}),
                'libraries': notebook_data.get('notebook:libraries', [])
            }
            
            return {
                'success': True,
                'widget_instances': widget_instances,
                'board_state': board_state,
                'rendered_mode': render_mode,
                'render_config': {
                    'show_panels': show_panels,
                    'panel_config': panel_config
                },
                'total_widgets': len(widgets),
                'notebook_title': board_state['title']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Notebook rendering failed: {str(e)}',
                'widget_instances': {},
                'board_state': {}
            }
    
    def _is_widget_entity(self, item: Dict[str, Any]) -> bool:
        """Check if an item is a widget entity"""
        types = item.get('@type', [])
        if isinstance(types, str):
            types = [types]
        
        return any('widget' in t.lower() for t in types)
    
    def _extract_connections(self, graph: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract connections from notebook graph"""
        connections = []
        for item in graph:
            types = item.get('@type', [])
            if isinstance(types, str):
                types = [types]
            
            if 'Connection' in types or any('connection' in t.lower() for t in types):
                connections.append(item)
        
        return connections
    
    def action_render_board_fullscreen(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to render notebook as fullscreen interactive board"""
        validated_input['render_mode'] = 'fullscreen'
        validated_input['show_panels'] = True
        
        result = self._execute_impl(validated_input)
        result['action'] = 'render-board-fullscreen'
        result['fullscreen_config'] = {
            'enable_exit': True,
            'show_toolbar': True,
            'allow_editing': True,
            'theme': 'dark'
        }
        return result
    
    def action_render_board_windowed(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to render notebook as windowed board"""
        validated_input['render_mode'] = 'windowed'
        validated_input['show_panels'] = validated_input.get('show_panels', False)
        
        result = self._execute_impl(validated_input)
        result['action'] = 'render-board-windowed'
        result['windowed_config'] = {
            'resizable': True,
            'scrollable': True,
            'movable': True,
            'min_width': '600px',
            'min_height': '400px'
        }
        return result
    
    def action_export_notebook_state(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to export current notebook state as JSON-LD"""
        result = self._execute_impl(validated_input)
        
        if result['success']:
            board_state = result['board_state']
            
            # Create JSON-LD export
            jsonld_export = {
                '@context': [
                    'https://www.w3.org/ns/prov-o.jsonld',
                    'https://litlfred.github.io/notebooks/libraries/core/core.jsonld'
                ],
                '@id': board_state.get('notebook_id', f'urn:notebook:export-{int(datetime.now().timestamp())}'),
                '@type': ['prov:Entity', 'notebook:Notebook', 'widget:NotebookWidget'],
                'dct:title': board_state.get('title', 'Exported Notebook'),
                'dct:created': datetime.now().isoformat(),
                '@graph': board_state.get('widgets', []) + board_state.get('connections', [])
            }
            
            result['action'] = 'export-notebook-state'
            result['jsonld_export'] = jsonld_export
        
        return result


def create_notebook_widget(widget_schema: Dict[str, Any], jsonld_schema: Dict[str, Any] = None) -> NotebookWidget:
    """Factory function to create notebook widget instance"""
    return NotebookWidget(widget_schema, jsonld_schema)