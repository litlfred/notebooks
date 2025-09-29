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
    """Base class for executing schema-based widgets with multi-action support and threading"""
    
    # Default empty input/output variable declarations - can be overridden by subclasses
    input_variables: Dict[str, Any] = {}
    output_variables: Dict[str, Any] = {}
    
    # Threading support flags
    supports_threading: bool = False
    supports_hierarchical_execution: bool = False
    
    def __init__(self, widget_schema: Dict[str, Any], jsonld_schema: Optional[Dict[str, Any]] = None):
        self.schema = widget_schema
        self.jsonld_schema = jsonld_schema or {}
        self.id = widget_schema['id']
        self.name = widget_schema['name']
        self.actions = widget_schema.get('actions', {})
        
        # Extract JSON-LD information from schema
        self.jsonld_id = self._extract_jsonld_id()
        self.jsonld_type = self._extract_jsonld_type()
        
        # Initialize parameter flow tracking
        self.incoming_arrows = []
        self.outgoing_arrows = []
        self.parameter_flow_processed = False
        
        # Schema signature validation warnings
        self.schema_warnings = []
        self._validate_schema_alignment()
        
        # Fullscreen mode support
        self.supports_fullscreen = self._check_fullscreen_support()
        self.fullscreen_config = self._get_fullscreen_config()
        
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
            
        # Initialize input variables with defaults or empty values
        self._initialize_input_variables()
        
    def _initialize_input_variables(self):
        """Initialize input parameters with empty or default values"""
        if hasattr(self, 'input_variables') and isinstance(self.input_variables, dict):
            for param_name, default_value in self.input_variables.items():
                if not hasattr(self, param_name):
                    setattr(self, param_name, default_value)
    
    def _extract_jsonld_id(self) -> str:
        """Extract JSON-LD ID from schema or derive from widget type"""
        if self.jsonld_schema and '@id' in self.jsonld_schema:
            return self.jsonld_schema['@id']
        elif 'id' in self.schema:
            return self.schema['id']
        else:
            # Convert class name to kebab-case as fallback
            class_name = self.__class__.__name__
            return re.sub('([a-z0-9])([A-Z])', r'\1-\2', class_name).lower().replace('-widget', '').replace('-executor', '')
    
    def _extract_jsonld_type(self) -> List[str]:
        """Extract JSON-LD types from schema"""
        if self.jsonld_schema and '@type' in self.jsonld_schema:
            jsonld_type = self.jsonld_schema['@type']
            return jsonld_type if isinstance(jsonld_type, list) else [jsonld_type]
        else:
            return [f"{self.jsonld_id}:widget"]
    
    def _validate_schema_alignment(self):
        """Validate alignment between JSON-LD schema and Python signature"""
        self.schema_warnings = []
        
        # Check if JSON-LD input parameters align with Python signature
        if self.jsonld_schema and 'input' in self.jsonld_schema:
            jsonld_input = self.jsonld_schema['input']
            if isinstance(jsonld_input, dict) and 'properties' in jsonld_input:
                jsonld_params = set(jsonld_input['properties'].keys())
                python_params = set(self.input_variables.keys()) if hasattr(self, 'input_variables') else set()
                
                missing_in_python = jsonld_params - python_params
                missing_in_jsonld = python_params - jsonld_params
                
                if missing_in_python:
                    self.schema_warnings.append({
                        'type': 'parameter_mismatch',
                        'severity': 'warning',
                        'message': f'JSON-LD defines parameters not in Python signature: {", ".join(missing_in_python)}'
                    })
                
                if missing_in_jsonld:
                    self.schema_warnings.append({
                        'type': 'parameter_mismatch', 
                        'severity': 'warning',
                        'message': f'Python signature has parameters not in JSON-LD: {", ".join(missing_in_jsonld)}'
                    })
    
    def has_warnings(self) -> bool:
        """Check if widget has schema warnings"""
        return len(self.schema_warnings) > 0
    
    def get_warnings(self) -> List[Dict[str, str]]:
        """Get list of schema warnings"""
        return self.schema_warnings.copy()
    
    def _check_fullscreen_support(self) -> bool:
        """Check if widget supports fullscreen mode"""
        # Check if widget has fullscreen-related actions
        for action_slug in self.actions.keys():
            if 'fullscreen' in action_slug.lower() or 'board' in action_slug.lower():
                return True
        
        # Check widget category/type for fullscreen capability
        category = self.schema.get('category', '').lower()
        if category in ['notebook', 'visualization', 'analysis']:
            return True
            
        return False
    
    def _get_fullscreen_config(self) -> Dict[str, Any]:
        """Get fullscreen configuration for widget"""
        return {
            'enable_exit': True,
            'show_toolbar': True,
            'allow_editing': True,
            'theme': 'dark',
            'overlay_mode': 'modal',
            'animation': 'fade',
            'close_on_escape': True,
            'show_controls': True
        }
    
    def enter_fullscreen_mode(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enter fullscreen mode with given configuration"""
        if not self.supports_fullscreen:
            return {
                'success': False,
                'error': 'Widget does not support fullscreen mode'
            }
        
        fullscreen_config = {**self.fullscreen_config, **(config or {})}
        
        return {
            'success': True,
            'mode': 'fullscreen',
            'config': fullscreen_config,
            'widget_id': self.id,
            'widget_type': self.schema.get('category', 'unknown')
        }
    
    def exit_fullscreen_mode(self) -> Dict[str, Any]:
        """Exit fullscreen mode and return to normal view"""
        return {
            'success': True,
            'mode': 'windowed',
            'widget_id': self.id,
            'return_to_board': True
        }
    
    def process_parameter_flow(self, arrows: List[Dict[str, Any]], source_widgets: Dict[str, Any]):
        """
        Process parameter flow arrows coming into this widget.
        Loop through arrows and merge data with optional ETL transformations.
        """
        if self.parameter_flow_processed:
            return  # Already processed
            
        for arrow in arrows:
            if arrow.get('target', {}).get('widget') == f'urn:widget:{self.id}':
                source_widget_id = arrow.get('source', {}).get('widget', '').replace('urn:widget:', '')
                source_widget = source_widgets.get(source_widget_id)
                
                if source_widget:
                    # Get source parameters
                    source_params = arrow.get('source', {}).get('parameters', [])
                    target_params = arrow.get('target', {}).get('input_parameters', [])
                    
                    # Optional ETL transformation
                    transform_code = arrow.get('transformation_python')
                    
                    for i, source_param in enumerate(source_params):
                        if i < len(target_params):
                            target_param = target_params[i]
                            
                            # Get value from source widget
                            source_value = getattr(source_widget, source_param, None)
                            
                            if transform_code:
                                # Apply ETL transformation
                                try:
                                    # Create safe execution environment
                                    transform_globals = {
                                        'source_value': source_value,
                                        'source_param': source_param,
                                        'target_param': target_param
                                    }
                                    exec(transform_code, transform_globals)
                                    transformed_value = transform_globals.get('result', source_value)
                                    setattr(self, target_param, transformed_value)
                                except Exception as e:
                                    print(f"ETL transformation error: {e}")
                                    setattr(self, target_param, source_value)
                            else:
                                # Direct parameter flow
                                setattr(self, target_param, source_value)
        
        self.parameter_flow_processed = True
    
    def add_incoming_arrow(self, arrow: 'WorkflowArrow'):
        """Add an incoming parameter flow arrow to this widget"""
        self.incoming_arrows.append(arrow)
    
    def add_outgoing_arrow(self, arrow: 'WorkflowArrow'):
        """Add an outgoing parameter flow arrow from this widget"""
        self.outgoing_arrows.append(arrow)
    
    def process_parameter_flow(self, widget_registry: Dict[str, 'WidgetExecutor']):
        """Process all incoming parameter flow arrows to populate input variables."""
        if self.parameter_flow_processed:
            return
        
        for arrow in self.incoming_arrows:
            try:
                # Find source widget instance
                source_widget = widget_registry.get(arrow.source_widget)
                if not source_widget:
                    print(f"Warning: Source widget {arrow.source_widget} not found in registry")
                    continue
                
                # Execute the arrow connection
                connection_result = arrow.execute_connection(source_widget, self)
                
                if not connection_result['success']:
                    print(f"Warning: Arrow connection failed: {connection_result.get('error_message')}")
                    continue
                    
            except Exception as e:
                print(f"Error processing parameter flow arrow: {e}")
                continue
        
        self.parameter_flow_processed = True
    
    def validate_inputs(self) -> Dict[str, Any]:
        """Validate current input variables against input schema"""
        if not self.input_schema:
            return {"valid": True, "message": "No input schema defined"}
        
        try:
            # Basic validation - in practice would use jsonschema library
            validation_errors = []
            
            if 'required' in self.input_schema:
                for required_field in self.input_schema['required']:
                    if not hasattr(self, required_field) or getattr(self, required_field) is None:
                        validation_errors.append(f"Required field '{required_field}' is missing")
            
            return {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "timestamp": datetime.now().isoformat()
            }
    
    def get_class_name_mapping(self) -> Dict[str, str]:
        """Get mapping between Python class names and JSON-LD identifiers."""
        return {
            "python_class": self.__class__.__name__,
            "json_ld_id": self.jsonld_id,
            "json_ld_type": self.jsonld_type,
            "schema_reference": f"{self.jsonld_id}.schema.json"
        }
    
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
    
    # Default threading action implementations (can be overridden by subclasses)
    def action_run(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Default run action - executes the widget"""
        return self.execute(validated_input)
    
    def action_stop(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Default stop action - base widgets don't support stopping"""
        return {
            'success': True,
            'message': f'Widget {self.id} does not support stopping (not threaded)',
            'widget_id': self.id,
            'supports_threading': self.supports_threading
        }
    
    def action_halt(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Default halt action - base widgets don't support halting"""
        return {
            'success': True,
            'message': f'Widget {self.id} does not support halting (not threaded)',
            'widget_id': self.id,
            'supports_threading': self.supports_threading
        }
    
    def get_jsonld_id(self) -> str:
        """Get the JSON-LD identifier for this widget instance"""
        return self.jsonld_id
    
    def get_jsonld_type(self) -> List[str]:
        """Get the JSON-LD types for this widget instance"""
        return self.jsonld_type
    
    def _execute_action_impl(self, validated_input: Dict[str, Any], action_slug: str, action_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action by calling corresponding class method.
        Action methods should be named 'action_<action_slug>' and take validated_input as parameter.
        Each method is responsible for doing its own validation before executing.
        """
        # Try to find a method named 'action_<action_slug>'
        method_name = f'action_{action_slug.replace("-", "_")}'
        
        if hasattr(self, method_name):
            action_method = getattr(self, method_name)
            if callable(action_method):
                # Call the action method with validated input
                result = action_method(validated_input)
                result['action'] = action_slug
                return result
        
        # Fallback to default implementation if no specific method found
        result = self._execute_impl(validated_input)
        result['action'] = action_slug
        return result

# Widget factory function
def create_widget(widget_type: str, widget_schema: Dict[str, Any], jsonld_schema: Optional[Dict[str, Any]] = None) -> WidgetExecutor:
    """Factory function to create widgets based on type with JSON-LD schema support"""
    # This is the base implementation - specific libraries can override
    return WidgetExecutor(widget_schema, jsonld_schema)