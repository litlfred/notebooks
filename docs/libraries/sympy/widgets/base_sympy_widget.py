"""
Base SymPy Widget class to handle common functionality and avoid repetitive code.
Uses introspection to automatically handle parameter conversion and execution.
Enhanced for new widget framework from PR #31.
"""

from typing import Dict, Any, Callable, Optional, List
import sympy as sp
import inspect
import json
import re
import time
from datetime import datetime
from abc import ABC, abstractmethod

# Import WidgetExecutor from the new framework
try:
    from ..core.base_widget import WidgetExecutor
except ImportError:
    try:
        from ...core.base_widget import WidgetExecutor
    except ImportError:
        # Fallback minimal WidgetExecutor implementation
        class WidgetExecutor:
            def __init__(self, widget_schema: Dict[str, Any]):
                self.schema = widget_schema
                self.id = widget_schema.get('id', 'unknown')
                self.name = widget_schema.get('name', 'Unknown Widget')


class BaseSymPyWidget(WidgetExecutor, ABC):
    """Base class for all SymPy widgets using introspection to minimize repetitive code.
    Enhanced for new widget framework from PR #31.
    """
    
    # Framework-compliant variable declarations
    input_variables: Dict[str, Any] = {
        'expr': 'x + x',  # Default symbolic expression
        'variables': 'x'   # Default variables
    }
    
    output_variables: Dict[str, Any] = {
        'result': None,
        'latex': None, 
        'metadata': None
    }
    
    # Action mapping to class methods (framework requirement)
    actions: Dict[str, str] = {
        'execute': 'execute_sympy_function',
        'validate': 'validate_input',
        'simplify': 'simplify_result'
    }
    
    def __init__(self, schema: Dict[str, Any]):
        # Initialize WidgetExecutor first
        super().__init__(schema)
        
        # SymPy-specific initialization
        self.function = self.get_sympy_function()
        self.function_signature = inspect.signature(self.function)
    
    def _get_sympy_parameter_names(self) -> List[str]:
        """Get parameter names that should be treated as SymPy expressions."""
        return ['expr', 'L', 'equation', 'expression', 'f', 'g', 'h', 'args', 'funcs', 'vars']
    
    def process_parameter_flow(self, arrows: List[Dict[str, Any]], source_widgets: Dict[str, Any]):
        """Process incoming parameter flow with SymPy-specific transformations."""
        super().process_parameter_flow(arrows, source_widgets)
        
        # SymPy-specific parameter transformations
        for param_name, value in self.__dict__.items():
            if isinstance(value, str) and param_name in self.sympy_parameters:
                try:
                    setattr(self, param_name, sp.sympify(value))
                except:
                    pass  # Keep original value if conversion fails
    
    @abstractmethod
    def get_sympy_function(self) -> Callable:
        """Return the SymPy function this widget wraps."""
        pass
    
    @abstractmethod
    def get_function_info(self) -> Dict[str, str]:
        """Return function metadata (name, module)."""
        pass
    
    def convert_parameter(self, key: str, value: Any, param_info: inspect.Parameter) -> Any:
        """Convert input parameter to appropriate SymPy type using introspection."""
        if value is None:
            return param_info.default if param_info.default != inspect.Parameter.empty else None
        
        # Handle string inputs that should be converted to SymPy objects
        if isinstance(value, str):
            # Skip empty strings or special default values
            if value == '' or 'function' in value or 'object' in value:
                return value
            
            # For expressions, try sympify
            if key in ['expr', 'L', 'equation', 'expression', 'f', 'g', 'h']:
                try:
                    import sympy as sp
                    # Define some common symbols for parsing
                    x, y, z, t = sp.symbols('x y z t')
                    f = sp.Function('f')
                    # Create a safer eval environment
                    safe_dict = {
                        'x': x, 'y': y, 'z': z, 't': t, 'f': f,
                        'sin': sp.sin, 'cos': sp.cos, 'exp': sp.exp,
                        'log': sp.log, 'sqrt': sp.sqrt, 'pi': sp.pi
                    }
                    
                    # First try sympify
                    try:
                        return sp.sympify(value, locals=safe_dict)
                    except:
                        # If that fails, try eval with safe environment
                        return eval(value, {"__builtins__": {}}, safe_dict)
                except:
                    return value
            
            # For boolean parameters
            if param_info.annotation == bool or 'bool' in str(param_info.annotation):
                return value.lower() in ('true', '1', 'yes', 'on')
            
            # For numeric parameters
            if param_info.annotation in [int, float] or 'int' in str(param_info.annotation) or 'float' in str(param_info.annotation):
                try:
                    return float(value) if '.' in value else int(value)
                except:
                    return value
            
            # For lists/tuples of functions or symbols
            if key in ['funcs', 'vars', 'symbols']:
                try:
                    import sympy as sp
                    if value.startswith('[') or value.startswith('('):
                        return sp.sympify(value)
                    else:
                        # Single symbol/function
                        return sp.sympify(value)
                except:
                    return value
        
        return value
    
    def prepare_parameters(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Convert input parameters using function signature introspection."""
        prepared = {}
        
        for param_name, param_info in self.function_signature.parameters.items():
            if param_name in validated_input:
                prepared[param_name] = self.convert_parameter(
                    param_name, 
                    validated_input[param_name], 
                    param_info
                )
            elif param_info.default != inspect.Parameter.empty:
                prepared[param_name] = param_info.default
        
        return prepared
    
    def format_result(self, result: Any) -> Dict[str, str]:
        """Format the result for output."""
        result_str = str(result)
        
        try:
            # Try to generate LaTeX if possible
            if hasattr(result, '_latex') or hasattr(sp, 'latex'):
                latex_str = sp.latex(result)
            else:
                latex_str = result_str
        except:
            latex_str = result_str
        
        return {
            'result': result_str,
            'latex': latex_str
        }
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the SymPy function with framework-compliant input/output."""
        return self.execute_sympy_function(validated_input)
    
    def execute_sympy_function(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the SymPy function with automatic parameter handling."""
        function_info = self.get_function_info()
        
        try:
            # Prepare parameters using introspection
            parameters = self.prepare_parameters(validated_input)
            
            # Call the SymPy function
            result = self.function(**parameters)
            
            # Format output
            formatted_result = self.format_result(result)
            
            # Set output variables for framework compatibility
            self.result = formatted_result.get('result')
            self.latex = formatted_result.get('latex')
            self.metadata = {
                'function': function_info['name'],
                'module': function_info['module'],
                'result_type': type(result).__name__,
                'parameters_used': parameters
            }
            
            return {
                **formatted_result,
                'metadata': self.metadata
            }
            
        except Exception as e:
            return {
                'result': f"Error: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'function': function_info['name'],
                    'module': function_info['module']
                }
            }
    
    def validate_input(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters for the SymPy function."""
        function_info = self.get_function_info()
        errors = []
        warnings = []
        
        try:
            # Check required parameters
            for param_name, param_info in self.function_signature.parameters.items():
                if param_info.default == inspect.Parameter.empty and param_name not in validated_input:
                    errors.append(f"Required parameter '{param_name}' is missing")
            
            # Validate parameter types
            for param_name, value in validated_input.items():
                if param_name in self.function_signature.parameters:
                    # Try to convert and validate
                    try:
                        self.convert_parameter(param_name, value, self.function_signature.parameters[param_name])
                    except Exception as e:
                        warnings.append(f"Parameter '{param_name}' may have conversion issues: {str(e)}")
                        
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'metadata': {
                    'function': function_info['name'],
                    'module': function_info['module']
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': warnings
            }
    
    def simplify_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify the result if it's a SymPy expression."""
        try:
            if 'result' in result_data:
                result_str = result_data['result']
                # Try to parse and simplify
                try:
                    expr = sp.sympify(result_str)
                    simplified = sp.simplify(expr)
                    simplified_str = str(simplified)
                    simplified_latex = sp.latex(simplified)
                    
                    return {
                        'result': simplified_str,
                        'latex': simplified_latex,
                        'original_result': result_str,
                        'simplified': True,
                        'metadata': {
                            'simplification_applied': True,
                            'original_complexity': len(result_str),
                            'simplified_complexity': len(simplified_str)
                        }
                    }
                except:
                    # If can't simplify, return original
                    return {
                        **result_data,
                        'simplified': False,
                        'metadata': {
                            'simplification_applied': False,
                            'reason': 'Could not parse result as SymPy expression'
                        }
                    }
            else:
                return {
                    'error': 'No result to simplify',
                    'simplified': False
                }
                
        except Exception as e:
            return {
                'error': f"Simplification error: {str(e)}",
                'simplified': False
            }


class SymPyFunctionWidget(BaseSymPyWidget):
    """Generic SymPy function widget that can wrap any SymPy function."""
    
    def __init__(self, schema: Dict[str, Any], sympy_function: Callable, function_name: str, module_name: str):
        self.sympy_function = sympy_function
        self.function_name = function_name
        self.module_name = module_name
        super().__init__(schema)
    
    def get_sympy_function(self) -> Callable:
        return self.sympy_function
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': self.function_name,
            'module': self.module_name
        }