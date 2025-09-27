#!/usr/bin/env python3
"""
SymPy Widget Generator Script

This script uses class introspection to analyze SymPy's class hierarchy
and generates widgets, JSON schemas, JSON-LD, and a completeness report.
"""

import json
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Set
import sympy
import datetime

# Add the src directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class SymPyWidgetGenerator:
    """Main class for generating SymPy widgets and documentation."""
    
    def __init__(self, output_dir: str = "docs/sympy"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track classes and methods for completeness report
        self.classes_analyzed = set()
        self.methods_analyzed = set()
        self.widgets_generated = set()
        
        # Core SymPy modules to analyze (starting with most important ones)
        self.core_modules = [
            'sympy.core',
            'sympy.functions',
            'sympy.matrices',
            'sympy.solvers',
            'sympy.calculus'
        ]
        
    def analyze_class_hierarchy(self) -> Dict[str, Any]:
        """Analyze SymPy class hierarchy using introspection."""
        hierarchy = {}
        
        print("🔍 Analyzing SymPy class hierarchy...")
        
        for module_name in self.core_modules:
            try:
                module = __import__(module_name, fromlist=[''])
                hierarchy[module_name] = self._analyze_module(module, module_name)
                print(f"   ✓ Analyzed {module_name}")
            except ImportError as e:
                print(f"   ⚠️  Could not import {module_name}: {e}")
                continue
                
        return hierarchy
    
    def _analyze_module(self, module, module_name: str) -> Dict[str, Any]:
        """Analyze a specific module for classes and methods."""
        module_info = {
            'classes': {},
            'functions': {},
            'constants': {}
        }
        
        # Limit analysis to avoid overwhelming output
        class_count = 0
        max_classes = 20  # Limit to first 20 classes per module
        
        for name, obj in inspect.getmembers(module):
            if name.startswith('_'):
                continue
            
            if class_count >= max_classes:
                break
                
            if inspect.isclass(obj) and obj.__module__.startswith(module_name):
                self.classes_analyzed.add(f"{module_name}.{name}")
                module_info['classes'][name] = self._analyze_class(obj, f"{module_name}.{name}")
                class_count += 1
            elif inspect.isfunction(obj) and obj.__module__.startswith(module_name):
                module_info['functions'][name] = self._analyze_function(obj)
                
        return module_info
    
    def _analyze_class(self, cls, full_name: str) -> Dict[str, Any]:
        """Analyze a class for methods and properties."""
        class_info = {
            'full_name': full_name,
            'bases': [base.__name__ for base in cls.__bases__],
            'doc': inspect.getdoc(cls) or "",
            'methods': {},
            'properties': {}
        }
        
        # Limit methods to avoid overwhelming output
        method_count = 0
        max_methods = 10  # Limit to first 10 methods per class
        
        for name, method in inspect.getmembers(cls):
            if name.startswith('_') or method_count >= max_methods:
                continue
                
            if inspect.ismethod(method) or inspect.isfunction(method):
                self.methods_analyzed.add(f"{full_name}.{name}")
                class_info['methods'][name] = self._analyze_method(method, f"{full_name}.{name}")
                method_count += 1
                
        return class_info
    
    def _analyze_method(self, method, full_name: str) -> Dict[str, Any]:
        """Analyze a method for signature and documentation."""
        try:
            signature = inspect.signature(method)
            parameters = {}
            
            for param_name, param in signature.parameters.items():
                parameters[param_name] = {
                    'kind': param.kind.name,
                    'default': str(param.default) if param.default != param.empty else None,
                    'annotation': str(param.annotation) if param.annotation != param.empty else None
                }
            
            return {
                'doc': inspect.getdoc(method) or "",
                'signature': str(signature),
                'parameters': parameters,
                'return_annotation': str(signature.return_annotation) if signature.return_annotation != signature.empty else None
            }
        except Exception as e:
            return {
                'doc': inspect.getdoc(method) or "",
                'signature': "Could not analyze",
                'error': str(e)
            }
    
    def _analyze_function(self, func) -> Dict[str, Any]:
        """Analyze a standalone function."""
        return self._analyze_method(func, func.__name__)
    
    def generate_widget_schemas(self, hierarchy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON schemas for widgets based on class hierarchy."""
        print("🔧 Generating widget schemas...")
        
        widget_schemas = {
            "widget-schemas": {}
        }
        
        for module_name, module_info in hierarchy.items():
            module_short = module_name.split('.')[-1]
            
            for class_name, class_info in module_info['classes'].items():
                # Generate widget schema for each class
                widget_id = f"sympy-{module_short}-{class_name.lower()}"
                self.widgets_generated.add(widget_id)
                
                widget_schemas["widget-schemas"][widget_id] = self._create_class_widget_schema(
                    widget_id, class_name, class_info, module_name
                )
                
                # Generate widget schema for each method (first 5 methods)
                method_count = 0
                for method_name, method_info in class_info['methods'].items():
                    if method_count >= 5:  # Limit to first 5 methods
                        break
                    method_widget_id = f"sympy-{module_short}-{class_name.lower()}-{method_name}"
                    self.widgets_generated.add(method_widget_id)
                    
                    widget_schemas["widget-schemas"][method_widget_id] = self._create_method_widget_schema(
                        method_widget_id, method_name, method_info, class_name, module_name
                    )
                    method_count += 1
        
        return widget_schemas
    
    def _create_class_widget_schema(self, widget_id: str, class_name: str, class_info: Dict[str, Any], module_name: str) -> Dict[str, Any]:
        """Create a widget schema for a SymPy class."""
        return {
            "id": widget_id,
            "name": f"SymPy {class_name}",
            "description": class_info['doc'][:200] + "..." if len(class_info['doc']) > 200 else class_info['doc'],
            "category": "sympy",
            "icon": "🧮",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": f"SymPy expression for {class_name}",
                        "default": "x + 1"
                    },
                    "variables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Variables in the expression",
                        "default": ["x"]
                    }
                },
                "required": ["expression"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "description": f"Result from {class_name} operation"
                    },
                    "latex": {
                        "type": "string", 
                        "description": "LaTeX representation of result"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata about the operation"
                    }
                }
            },
            "python_script": f"widgets/sympy_{widget_id.replace('-', '_')}.py",
            "module_name": module_name,
            "class_name": class_name
        }
    
    def _create_method_widget_schema(self, widget_id: str, method_name: str, method_info: Dict[str, Any], class_name: str, module_name: str) -> Dict[str, Any]:
        """Create a widget schema for a SymPy method."""
        # Build input schema from method parameters
        input_properties = {}
        required_params = []
        
        for param_name, param_info in method_info.get('parameters', {}).items():
            if param_name in ['self', 'cls']:
                continue
                
            param_schema = {
                "type": "string",
                "description": f"Parameter {param_name} for {method_name}"
            }
            
            if param_info['default'] is None and param_info['kind'] != 'VAR_POSITIONAL':
                required_params.append(param_name)
            elif param_info['default'] is not None:
                param_schema["default"] = param_info['default']
                
            input_properties[param_name] = param_schema
        
        return {
            "id": widget_id,
            "name": f"SymPy {class_name}.{method_name}",
            "description": method_info['doc'][:200] + "..." if len(method_info['doc']) > 200 else method_info['doc'],
            "category": "sympy",
            "icon": "⚙️",
            "input_schema": {
                "type": "object",
                "properties": input_properties,
                "required": required_params
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "description": f"Result from {class_name}.{method_name}"
                    },
                    "latex": {
                        "type": "string",
                        "description": "LaTeX representation of result"
                    }
                }
            },
            "python_script": f"widgets/sympy_{widget_id.replace('-', '_')}.py",
            "module_name": module_name,
            "class_name": class_name,
            "method_name": method_name
        }
    
    def generate_json_ld(self, hierarchy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD context for SymPy widgets."""
        print("📝 Generating JSON-LD context...")
        
        context = {
            "@context": {
                "@vocab": "https://schema.org/",
                "sympy": "https://sympy.org/",
                "widget": "https://widgets.sympy.org/",
                "SoftwareApplication": "https://schema.org/SoftwareApplication",
                "ComputationalWidget": "widget:ComputationalWidget",
                "MathematicalFunction": "widget:MathematicalFunction"
            },
            "@graph": []
        }
        
        for module_name, module_info in hierarchy.items():
            module_entry = {
                "@type": "SoftwareApplication",
                "@id": f"sympy:{module_name}",
                "name": module_name,
                "applicationCategory": "Mathematical Software",
                "classes": []
            }
            
            for class_name, class_info in module_info['classes'].items():
                class_entry = {
                    "@type": "ComputationalWidget",
                    "@id": f"sympy:{module_name}.{class_name}",
                    "name": class_name,
                    "description": class_info['doc'],
                    "methods": []
                }
                
                for method_name in class_info['methods'].keys():
                    class_entry["methods"].append({
                        "@type": "MathematicalFunction",
                        "@id": f"sympy:{module_name}.{class_name}.{method_name}",
                        "name": method_name
                    })
                
                module_entry["classes"].append(class_entry)
            
            context["@graph"].append(module_entry)
        
        return context
    
    def generate_completeness_report(self, hierarchy: Dict[str, Any]) -> str:
        """Generate a markdown completeness report."""
        print("📊 Generating completeness report...")
        
        report = ["# SymPy Widgets Completeness Report"]
        report.append("")
        report.append(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        total_classes = len(self.classes_analyzed)
        total_methods = len(self.methods_analyzed)
        total_widgets = len(self.widgets_generated)
        
        report.extend([
            "## Summary Statistics",
            "",
            f"- **Total Classes Analyzed:** {total_classes}",
            f"- **Total Methods Analyzed:** {total_methods}",
            f"- **Total Widgets Generated:** {total_widgets}",
            f"- **Coverage:** {(total_widgets / max(total_classes + total_methods, 1)) * 100:.1f}%",
            ""
        ])
        
        # Progress checklist
        report.extend([
            "## Progress Checklist",
            "",
            "- [x] Install SymPy package",
            "- [x] Create class introspection script",
            "- [x] Analyze SymPy class hierarchy",
            "- [x] Generate JSON schemas for widgets",
            "- [x] Generate JSON-LD context",
            "- [x] Create completeness report template",
            "- [ ] Generate widget Python scripts",
            "- [ ] Create widget executor implementations", 
            "- [ ] Add widgets to main widget schema",
            "- [ ] Test widget functionality",
            "- [ ] Update documentation",
            ""
        ])
        
        # Detailed hierarchy
        report.extend([
            "## Class Hierarchy Analysis",
            ""
        ])
        
        for module_name, module_info in hierarchy.items():
            if not module_info['classes']:
                continue
                
            report.append(f"### {module_name}")
            report.append("")
            
            for class_name, class_info in module_info['classes'].items():
                widget_status = "✅" if any(w.endswith(class_name.lower()) for w in self.widgets_generated) else "❌"
                report.append(f"- **{class_name}** {widget_status}")
                
                if class_info['doc']:
                    doc_preview = class_info['doc'][:100].replace('\n', ' ')
                    report.append(f"  - *Description:* {doc_preview}...")
                
                if class_info['methods']:
                    report.append("  - **Methods:**")
                    for method_name in class_info['methods'].keys():
                        method_widget_status = "✅" if any(method_name in w for w in self.widgets_generated) else "❌"
                        report.append(f"    - `{method_name}()` {method_widget_status}")
                
                report.append("")
        
        # Widget generation status
        report.extend([
            "## Widget Generation Status",
            ""
        ])
        
        for widget_id in sorted(self.widgets_generated):
            report.append(f"- `{widget_id}` ✅")
        
        report.append("")
        
        return "\n".join(report)
    
    def save_outputs(self, hierarchy: Dict[str, Any], schemas: Dict[str, Any], json_ld: Dict[str, Any], report: str):
        """Save all generated outputs to files."""
        print("💾 Saving outputs...")
        
        # Save hierarchy analysis
        with open(self.output_dir / "hierarchy_analysis.json", "w") as f:
            json.dump(hierarchy, f, indent=2, default=str)
        
        # Save widget schemas
        with open(self.output_dir / "widget_schemas.json", "w") as f:
            json.dump(schemas, f, indent=2)
        
        # Save JSON-LD
        with open(self.output_dir / "sympy_context.jsonld", "w") as f:
            json.dump(json_ld, f, indent=2)
        
        # Save completeness report
        with open(self.output_dir / "COMPLETENESS_REPORT.md", "w") as f:
            f.write(report)
        
        print(f"✅ Outputs saved to {self.output_dir}")
    
    def run(self):
        """Main execution method."""
        print("🚀 Starting SymPy Widget Generation...")
        print("")
        
        # Step 1: Analyze class hierarchy
        hierarchy = self.analyze_class_hierarchy()
        
        # Step 2: Generate widget schemas
        schemas = self.generate_widget_schemas(hierarchy)
        
        # Step 3: Generate JSON-LD
        json_ld = self.generate_json_ld(hierarchy)
        
        # Step 4: Generate completeness report
        report = self.generate_completeness_report(hierarchy)
        
        # Step 5: Save all outputs
        self.save_outputs(hierarchy, schemas, json_ld, report)
        
        print("")
        print("🎉 SymPy widget generation completed!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Generated {len(self.widgets_generated)} widgets for {len(self.classes_analyzed)} classes")


if __name__ == "__main__":
    generator = SymPyWidgetGenerator()
    generator.run()