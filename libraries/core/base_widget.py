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
    
    # Default empty input/output variable declarations - can be overridden by subclasses
    input_variables: Dict[str, Any] = {}
    output_variables: Dict[str, Any] = {}
    
    # Hard-coded class name to JSON-LD ID mapping
    _class_name_to_jsonld_id = {
        'WidgetExecutor': 'base-widget',
        'StickyNoteWidget': 'sticky-note',
        'PythonCodeWidget': 'python-code', 
        'DataVisualizationWidget': 'data-visualization',
        'ArrowWidget': 'arrow',
        'PQTorusWidget': 'pq-torus',
        'PQTorusWeierstrassTwoPanelWidget': 'pq-torus.weierstrass.two-panel',
        'PQTorusWeierstrassThreePanelWidget': 'pq-torus.weierstrass.three-panel',
        'PQTorusWeierstrassFivePanelWidget': 'pq-torus.weierstrass.five-panel',
        'PQTorusWeierstrassTrajectoriesWidget': 'pq-torus.weierstrass.trajectories',
        'PQTorusWeierstrassContoursWidget': 'pq-torus.weierstrass.contours',
        # Jupyter widgets
        'JupyterMarkdownWidget': 'jupyter.markdown-cell',
        'JupyterCodeWidget': 'jupyter.code-cell',
        'JupyterRawWidget': 'jupyter.raw-cell'
    }
    
    # Reverse mapping for JSON-LD ID to class name
    _jsonld_id_to_class_name = {v: k for k, v in _class_name_to_jsonld_id.items()}
    
    def __init__(self, widget_schema: Dict[str, Any]):
        self.schema = widget_schema
        self.id = widget_schema['id']
        self.name = widget_schema['name']
        self.actions = widget_schema.get('actions', {})
        
        # Initialize parameter flow tracking
        self.incoming_arrows = []
        self.outgoing_arrows = []
        self.parameter_flow_processed = False
        
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
        class_name = self.__class__.__name__
        
        # Convert PythonCamelCase to kebab-case for JSON-LD
        kebab_case = re.sub('([a-z0-9])([A-Z])', r'\1-\2', class_name).lower()
        
        # Remove common suffixes
        kebab_case = kebab_case.replace('-widget', '').replace('-executor', '')
        
        return {
            "python_class": class_name,
            "json_ld_id": kebab_case,
            "schema_reference": f"{kebab_case}.schema.json"
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
    
    @classmethod
    def get_jsonld_id(cls) -> str:
        """Get the JSON-LD identifier for this widget class"""
        class_name = cls.__name__
        return cls._class_name_to_jsonld_id.get(class_name, class_name.lower())
    
    @classmethod
    def get_class_for_jsonld_id(cls, jsonld_id: str) -> str:
        """Get the class name for a JSON-LD identifier"""
        return cls._jsonld_id_to_class_name.get(jsonld_id, jsonld_id)
    
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
def create_widget(widget_type: str, widget_schema: Dict[str, Any]) -> WidgetExecutor:
    """Factory function to create widgets based on type"""
    # This is the base implementation - specific libraries can override
    return WidgetExecutor(widget_schema)