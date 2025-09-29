"""
Widget Integration Module for Weierstrass Playground

This module provides the integration layer between the Python widget framework
and the notebook/application interface, following the original issue #14 requirements.
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add the libraries path to enable widget imports
libraries_path = Path(__file__).parent.parent.parent / "libraries" / "core"
sys.path.insert(0, str(libraries_path))

# Import base widget functionality
try:
    from base_widget import WidgetExecutor
    
    # Import specific widget modules by file path
    import importlib.util
    
    sticky_note_path = libraries_path / "sticky-note" / "sticky_note.py"
    spec = importlib.util.spec_from_file_location("sticky_note", sticky_note_path)
    sticky_note_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sticky_note_module)
    
    StickyNoteWidget = sticky_note_module.StickyNoteWidget
    STICKY_NOTE_SCHEMA = sticky_note_module.STICKY_NOTE_SCHEMA
    
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import widget modules: {e}")
    WidgetExecutor = None
    StickyNoteWidget = None
    STICKY_NOTE_SCHEMA = None
    IMPORTS_AVAILABLE = False
except Exception as e:
    print(f"Warning: Could not load widget modules: {e}")
    WidgetExecutor = None
    StickyNoteWidget = None  
    STICKY_NOTE_SCHEMA = None
    IMPORTS_AVAILABLE = False


class MockWidget:
    """Mock widget implementation for when full framework isn't available"""
    
    def __init__(self, schema):
        self.schema = schema
        self.id = schema.get('id', 'mock-widget')
        self.name = schema.get('name', 'Mock Widget')
        self.input_schema = schema.get('input_schema', {})
        self.output_schema = schema.get('output_schema', {})
        self.actions = schema.get('actions', {})
        
    def execute(self, input_data):
        return {
            'success': True,
            'message': f'Mock execution of {self.id}',
            'input_received': input_data
        }
    
    def execute_action(self, input_data, action):
        return {
            'success': True,
            'action': action,
            'message': f'Mock action {action} on {self.id}',
            'input_received': input_data
        }
    
    def get_action_menu(self, locale='en'):
        return {'mock': [{'slug': 'test', 'name': 'Test Action', 'icon': '🧪'}]}
    
    def validate_inputs(self):
        return {'valid': True, 'message': 'Mock validation'}
    
    def get_jsonld_id(self):
        return self.id
    
    def process_markdown_variables(self, content):
        # Simple variable substitution
        import re
        variables = {
            'widget_id': self.id,
            'widget_name': self.name,
            'timestamp': self._get_current_timestamp()
        }
        
        def replace_variable(match):
            var_name = match.group(1)
            return str(variables.get(var_name, f'{{undefined:{var_name}}}'))
        
        return re.sub(r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}', replace_variable, content)
    
    def _get_current_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()


class WidgetFramework:
    """
    Main widget framework integration following issue #14 requirements.
    
    Provides:
    - Widget instance management with proper IDs (incremental, not UUID)
    - JSON schema-based input/output validation
    - Python script execution coordination
    - Variable substitution and markdown processing
    - Action menu generation and execution
    """
    
    def __init__(self):
        self.widgets = {}  # Active widget instances
        self.widget_counter = 0  # For incremental IDs
        self.widget_schemas = self._load_widget_schemas()
        self.execution_queue = []
        
    def _load_widget_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load available widget schemas"""
        schemas = {}
        
        if IMPORTS_AVAILABLE and STICKY_NOTE_SCHEMA:
            schemas["sticky-note"] = STICKY_NOTE_SCHEMA
            
        # Fallback schema for when imports aren't available
        if not schemas:
            schemas["sticky-note"] = {
                "id": "sticky-note",
                "name": "Sticky Note", 
                "description": "Simple markdown note widget - the most basic widget example",
                "category": "content",
                "icon": "📝",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Markdown content for the note",
                            "default": "# New Sticky Note\n\nClick edit to add your **markdown** content..."
                        },
                        "show_note": {
                            "type": "boolean",
                            "description": "Show or hide the note content", 
                            "default": True
                        }
                    },
                    "required": ["content"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "rendered_html": {"type": "string"},
                        "error": {"type": "string"}
                    }
                },
                "python_script": "libraries/core/sticky-note/sticky_note.py"
            }
            
        return schemas
    
    def create_widget_instance(self, widget_type: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new widget instance with proper ID management.
        
        Args:
            widget_type: Type of widget (e.g., 'sticky-note')
            config: Optional initial configuration
            
        Returns:
            Widget instance information
        """
        if widget_type not in self.widget_schemas:
            raise ValueError(f"Unknown widget type: {widget_type}")
        
        # Generate incremental ID (not UUID as specified in issue #14)
        self.widget_counter += 1
        widget_id = f"widget-{self.widget_counter}"
        
        # Create widget instance
        schema = self.widget_schemas[widget_type].copy()
        schema['id'] = widget_id
        
        if widget_type == "sticky-note" and IMPORTS_AVAILABLE and StickyNoteWidget:
            widget_instance = StickyNoteWidget(schema)
        else:
            # Fallback to base widget or mock implementation
            if IMPORTS_AVAILABLE and WidgetExecutor:
                widget_instance = WidgetExecutor(schema)
            else:
                # Mock widget when imports are not available
                widget_instance = MockWidget(schema)
        
        # Apply initial configuration
        if config:
            for key, value in config.items():
                if hasattr(widget_instance, key):
                    setattr(widget_instance, key, value)
        
        # Store instance
        self.widgets[widget_id] = widget_instance
        
        return {
            'widget_id': widget_id,
            'widget_type': widget_type,
            'instance': widget_instance,
            'schema': schema,
            'created_at': self._get_current_timestamp()
        }
    
    def execute_widget(self, widget_id: str, input_data: Optional[Dict[str, Any]] = None, action: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a widget with proper error handling and metadata.
        
        Args:
            widget_id: ID of the widget to execute
            input_data: Input data for the widget
            action: Optional specific action to execute
            
        Returns:
            Execution result with metadata
        """
        if widget_id not in self.widgets:
            return {
                'success': False,
                'error': f'Widget {widget_id} not found',
                'widget_id': widget_id
            }
        
        widget = self.widgets[widget_id]
        input_data = input_data or {}
        
        try:
            if action:
                # Execute specific action
                result = widget.execute_action(input_data, action)
            else:
                # Execute default widget behavior
                result = widget.execute(input_data)
            
            # Add framework metadata
            result.update({
                'widget_id': widget_id,
                'framework_version': '1.0.0',
                'execution_context': 'weierstrass_playground'
            })
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'widget_id': widget_id,
                'framework_version': '1.0.0'
            }
    
    def get_widget_action_menu(self, widget_id: str, locale: str = 'en') -> Dict[str, Any]:
        """
        Get hierarchical action menu for a widget as specified in issue #14.
        """
        if widget_id not in self.widgets:
            return {'error': f'Widget {widget_id} not found'}
        
        widget = self.widgets[widget_id]
        return widget.get_action_menu(locale)
    
    def process_markdown_with_variables(self, content: str, widget_id: str) -> str:
        """
        Process markdown content with variable substitution as required.
        
        This implements the {{variable}} syntax mentioned in issue #14 with
        access to widget metadata and execution state.
        """
        if widget_id not in self.widgets:
            return content
        
        widget = self.widgets[widget_id]
        
        # Use the widget's built-in variable processing if available
        if hasattr(widget, 'process_markdown_variables'):
            return widget.process_markdown_variables(content)
        
        # Fallback processing
        variables = {
            'widget_id': widget_id,
            'widget_name': widget.name,
            'timestamp': self._get_current_timestamp()
        }
        
        import re
        def replace_variable(match):
            var_name = match.group(1)
            if var_name in variables:
                return str(variables[var_name])
            else:
                return f'<span style="color: red; text-decoration: underline;">{{undefined:{var_name}}}</span>'
        
        variable_pattern = re.compile(r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}')
        return variable_pattern.sub(replace_variable, content)
    
    def validate_widget_input(self, widget_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against widget schema.
        """
        if widget_id not in self.widgets:
            return {'valid': False, 'error': f'Widget {widget_id} not found'}
        
        widget = self.widgets[widget_id]
        return widget.validate_inputs()
    
    def get_widget_metadata(self, widget_id: str) -> Dict[str, Any]:
        """
        Get widget metadata including schema information and current state.
        """
        if widget_id not in self.widgets:
            return {'error': f'Widget {widget_id} not found'}
        
        widget = self.widgets[widget_id]
        
        return {
            'widget_id': widget_id,
            'widget_type': widget.get_jsonld_id(),
            'name': widget.name,
            'schema': {
                'input': widget.input_schema,
                'output': widget.output_schema
            },
            'actions': list(widget.actions.keys()) if hasattr(widget, 'actions') else [],
            'status': 'active',
            'created_at': getattr(widget, 'created_at', None)
        }
    
    def list_available_widgets(self) -> Dict[str, Any]:
        """
        List all available widget types with their schemas.
        """
        return {
            widget_type: {
                'name': schema.get('name', widget_type),
                'description': schema.get('description', ''),
                'category': schema.get('category', 'general'),
                'icon': schema.get('icon', '🔧'),
                'actions': list(schema.get('actions', {}).keys())
            }
            for widget_type, schema in self.widget_schemas.items()
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()


# Singleton instance for global access
widget_framework = WidgetFramework()


def create_widget(widget_type: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to create a widget and return its ID.
    """
    result = widget_framework.create_widget_instance(widget_type, config)
    return result['widget_id']


def execute_widget(widget_id: str, input_data: Optional[Dict[str, Any]] = None, action: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to execute a widget.
    """
    return widget_framework.execute_widget(widget_id, input_data, action)


if __name__ == "__main__":
    # Test the integration
    print("Testing Widget Framework Integration...")
    
    # Test widget creation
    widget_id = create_widget("sticky-note", {
        'content': '# Test Note\n\nThis is a **test** with {{widget_id}} substitution.\n\n- Feature 1\n- Feature 2'
    })
    print(f"Created widget: {widget_id}")
    
    # Test widget execution
    result = execute_widget(widget_id, {
        'content': '# Integration Test\n\nWidget {{widget_id}} executed at {{timestamp}}.\n\nThe Weierstrass ℘ function.',
        'show_note': True
    })
    print(f"Execution result: {result}")
    
    # Test action execution
    action_result = execute_widget(widget_id, {
        'content': '# Action Test\n\nTesting **action** execution.'
    }, action='render-markdown')
    print(f"Action result: {action_result}")
    
    print("Integration test completed.")