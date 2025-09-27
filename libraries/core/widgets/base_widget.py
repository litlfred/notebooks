"""
Widget Execution Engine for Mathematical Board
Base widget executor functionality for the core widget library
"""

import json
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class WidgetExecutor:
    """Base class for executing schema-based widgets with multi-action support"""
    
    def __init__(self, widget_schema: Dict[str, Any]):
        self.schema = widget_schema
        self.id = widget_schema['id']
        self.name = widget_schema['name']
        self.actions = widget_schema.get('actions', {})
        
        # Handle both old and new schema formats
        if 'input_schemas' in widget_schema:
            # New format with multiple schemas
            self.input_schemas = widget_schema['input_schemas']
            self.output_schemas = widget_schema['output_schemas']
            # For backward compatibility, use first schema as primary
            self.input_schema = self._resolve_schema_reference(self.input_schemas[0]) if self.input_schemas else {}
            self.output_schema = self._resolve_schema_reference(self.output_schemas[0]) if self.output_schemas else {}
        else:
            # Old format with single schema
            self.input_schema = widget_schema.get('input_schema', {})
            self.output_schema = widget_schema.get('output_schema', {})
            self.input_schemas = [self.input_schema] if self.input_schema else []
            self.output_schemas = [self.output_schema] if self.output_schema else []
    
    def _resolve_schema_reference(self, schema_ref):
        """Resolve schema reference to actual schema object"""
        if isinstance(schema_ref, str):
            # For now, return a basic schema structure for URL references
            # In a full implementation, this would fetch and resolve the URL
            if 'sticky-note' in schema_ref:
                return {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "default": "# New Sticky Note\n\nClick edit to add your **markdown** content...\n\n- Use lists\n- Add `code`\n- Format *text*"
                        },
                        "show_note": {
                            "type": "boolean",
                            "default": True
                        }
                    },
                    "required": ["content"]
                }
            else:
                # Default empty schema for unknown references
                return {"type": "object", "properties": {}}
        else:
            # Inline schema object
            return schema_ref
        
    def validate_input_for_action(self, input_data: Dict[str, Any], action_slug: str) -> Dict[str, Any]:
        """Validate input data against schema for a specific action"""
        # Get action configuration
        action_config = self.actions.get(action_slug, {})
        validation_required = action_config.get('validation_required', True)
        
        if not validation_required:
            return input_data
            
        return self.validate_input(input_data)
    
    def execute_action(self, input_data: Dict[str, Any], action_slug: str) -> Dict[str, Any]:
        """Execute specific widget action with validation"""
        # Validate action exists
        if action_slug not in self.actions:
            raise ValueError(f"Action '{action_slug}' not found in widget '{self.id}'")
        
        action_config = self.actions[action_slug]
        
        # Validate input data if required
        validated_input = self.validate_input_for_action(input_data, action_slug)
        
        # Record execution time
        start_time = time.time()
        
        try:
            # Execute action-specific implementation
            result = self._execute_action_impl(validated_input, action_slug, action_config)
            result.update({
                'execution_time': (time.time() - start_time) * 1000,
                'widget_id': self.id,
                'action_slug': action_slug,
                'output_format': action_config.get('output_format', 'json'),
                'success': True,
                'timestamp': datetime.now().isoformat()
            })
            return result
            
        except Exception as e:
            return {
                'widget_id': self.id,
                'action_slug': action_slug,
                'success': False,
                'error': str(e),
                'execution_time': (time.time() - start_time) * 1000,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_action_menu(self, locale: str = 'en') -> Dict[str, Any]:
        """Get hierarchical action menu for widget interface"""
        menu = {}
        
        for action_slug, action_config in self.actions.items():
            category = action_config.get('menu_category', 'actions')
            action_name = action_config.get('names', {}).get(locale, action_config.get('names', {}).get('en', action_slug))
            
            if category not in menu:
                menu[category] = []
            
            menu[category].append({
                'slug': action_slug,
                'name': action_name,
                'icon': action_config.get('icon', '⚙️'),
                'description': action_config.get('description', {}).get(locale, action_config.get('description', {}).get('en', ''))
            })
        
        return menu
    
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data against schema with comprehensive checking"""
        validated = {}
        
        # Apply defaults for missing values
        if 'properties' in self.input_schema:
            for prop, prop_schema in self.input_schema['properties'].items():
                if prop in input_data:
                    # Basic type validation
                    expected_type = prop_schema.get('type')
                    if expected_type == 'integer' and not isinstance(input_data[prop], int):
                        try:
                            validated[prop] = int(input_data[prop])
                        except (ValueError, TypeError):
                            raise ValueError(f"Property '{prop}' must be an integer")
                    elif expected_type == 'number' and not isinstance(input_data[prop], (int, float)):
                        try:
                            validated[prop] = float(input_data[prop])
                        except (ValueError, TypeError):
                            raise ValueError(f"Property '{prop}' must be a number")
                    elif expected_type == 'boolean' and not isinstance(input_data[prop], bool):
                        # Convert string boolean values
                        if isinstance(input_data[prop], str):
                            validated[prop] = input_data[prop].lower() in ('true', '1', 'yes', 'on')
                        else:
                            validated[prop] = bool(input_data[prop])
                    else:
                        validated[prop] = input_data[prop]
                        
                    # Range validation for numbers
                    if expected_type in ('integer', 'number'):
                        if 'minimum' in prop_schema and validated[prop] < prop_schema['minimum']:
                            raise ValueError(f"Property '{prop}' must be >= {prop_schema['minimum']}")
                        if 'maximum' in prop_schema and validated[prop] > prop_schema['maximum']:
                            raise ValueError(f"Property '{prop}' must be <= {prop_schema['maximum']}")
                            
                elif 'default' in prop_schema:
                    validated[prop] = prop_schema['default']
                elif prop in self.input_schema.get('required', []):
                    raise ValueError(f"Required property '{prop}' missing")
        
        return validated

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute widget with input validation and error handling"""
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            # Validate input
            validated_input = self.validate_input(input_data)
            
            # Execute widget logic
            result = self._execute_impl(validated_input)
            
            # Add execution metadata
            result.update({
                'execution_time': (time.time() - start_time) * 1000,
                'timestamp': timestamp,
                'widget_id': self.id,
                'success': result.get('success', True)
            })
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': (time.time() - start_time) * 1000,
                'timestamp': timestamp,
                'widget_id': self.id
            }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method for widget-specific execution logic.
        Subclasses must implement this method.
        """
        return {
            'success': True,
            'message': f'Base widget {self.id} executed successfully',
            'input_received': validated_input
        }
    
    def _execute_action_impl(self, validated_input: Dict[str, Any], action_slug: str, action_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method for action-specific execution logic.
        Subclasses can override this method for custom action handling.
        """
        # Default implementation calls the main execute method
        result = self._execute_impl(validated_input)
        result['action'] = action_slug
        return result

# Widget factory function
def create_widget(widget_type: str, widget_schema: Dict[str, Any]) -> WidgetExecutor:
    """Factory function to create widgets based on type"""
    # This is the base implementation - specific libraries can override
    return WidgetExecutor(widget_schema)