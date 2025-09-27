"""
Base SymPy Widget class to handle common functionality and avoid repetitive code.
Uses introspection to automatically handle parameter conversion and execution.
"""

from typing import Dict, Any, Callable, Optional
import sympy as sp
import inspect
from abc import ABC, abstractmethod


class BaseSymPyWidget(ABC):
    """Base class for all SymPy widgets using introspection to minimize repetitive code."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.function = self.get_sympy_function()
        self.function_signature = inspect.signature(self.function)
    
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
        """Execute the SymPy function with automatic parameter handling."""
        function_info = self.get_function_info()
        
        try:
            # Prepare parameters using introspection
            parameters = self.prepare_parameters(validated_input)
            
            # Call the SymPy function
            result = self.function(**parameters)
            
            # Format output
            formatted_result = self.format_result(result)
            
            return {
                **formatted_result,
                'metadata': {
                    'function': function_info['name'],
                    'module': function_info['module'],
                    'result_type': type(result).__name__,
                    'parameters_used': parameters
                }
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