# Widget Framework Development Guide

## Creating Compliant Widget Libraries

This guide provides step-by-step instructions for creating compliant widget libraries that follow all framework requirements.

## 📋 Widget Library Requirements

### 1. Directory Structure

Each widget library must follow this structure:

```
libraries/{library-name}/
├── {library-name}.jsonld          # Library definition with JSON-LD context
├── {umbrella-widget}.py           # Main umbrella widget implementation
├── {widget-name}/                 # Individual widget directories
│   ├── {widget-name}.py           # Widget Python implementation
│   ├── input.schema.json          # Input validation schema
│   ├── output.schema.json         # Output validation schema
│   ├── widget.schema.json         # Widget instance schema
│   ├── input.jsonld               # Input JSON-LD context
│   ├── output.jsonld              # Output JSON-LD context
│   └── widget.jsonld              # Widget JSON-LD context
└── common/                        # Shared schemas (optional)
    ├── metadata.schema.json
    └── execution-result.schema.json
```

### 2. Python Widget Implementation Requirements

#### Base Class Inheritance
All widgets MUST inherit from `WidgetExecutor`:

```python
from base_widget import WidgetExecutor

class YourWidget(WidgetExecutor):
    """Widget description"""
    pass
```

#### Class Naming Convention
Widget class names MUST follow the hierarchical umbrella pattern:

- **Umbrella Widget**: `{LibraryName}Widget` (e.g., `PQTorusWidget`)
- **Sub-Widget**: `{LibraryName}{SubCategory}Widget` (e.g., `PQTorusWeierstrassWidget`) 
- **Specific Widget**: `{LibraryName}{SubCategory}{Specific}Widget` (e.g., `PQTorusWeierstrassTwoPanelWidget`)

#### Variable Declarations
Each widget MUST declare its input/output variables:

```python
class YourWidget(WidgetExecutor):
    # Override input/output variable declarations
    input_variables = {
        'param1': 'default_value',
        'param2': 42,
        'param3': {'nested': 'object'}
    }
    
    output_variables = {
        'success': True,
        'result': {},
        'metadata': {}
    }
```

#### Required Methods

**Main Execution Method** (Required):
```python
def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
    """Main widget execution logic"""
    # Your implementation here
    return {
        'success': True,
        'result': 'your_result'
    }
```

**Action Methods** (Optional):
Action methods MUST be named `action_{action_slug}` with hyphens replaced by underscores:
```python
def action_render_plot(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
    """Action method for 'render-plot' action"""
    # Do action-specific validation here
    if not self._validate_plot_params(validated_input):
        return {'success': False, 'error': 'Invalid parameters'}
    
    # Execute action logic
    return self._execute_impl(validated_input)
```

### 3. JSON Schema Requirements

#### Schema URLs
All schemas MUST use GitHub Pages URLs:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://litlfred.github.io/notebooks/libraries/{library-name}/{widget-name}/input.schema.json"
}
```

#### Schema Structure
- `input.schema.json`: Validates widget input parameters
- `output.schema.json`: Validates widget output structure  
- `widget.schema.json`: Validates widget instance configuration

### 4. JSON-LD Requirements

#### Context URLs
All JSON-LD files MUST reference the library's main context:
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld",
    "https://litlfred.github.io/notebooks/libraries/{library-name}/{library-name}.jsonld"
  ]
}
```

#### Type Naming
Types MUST use library-consistent prefixes:
```json
{
  "@type": ["prov:Entity", "{library-prefix}:{widget-type}"]
}
```

### 5. Widget Registry Integration

Each widget MUST be registered in `docs/weierstrass-playground/widget-schemas.json`:

```json
{
  "widget-id": {
    "id": "widget-id",
    "name": "Widget Name",
    "description": "Widget description",
    "category": "computation|visualization|content|data|utility",
    "icon": "🔧",
    "input_schemas": [
      "https://litlfred.github.io/notebooks/libraries/{library}/{widget}/input.schema.json"
    ],
    "output_schemas": [
      "https://litlfred.github.io/notebooks/libraries/{library}/{widget}/output.schema.json"
    ],
    "python_script": "{widget-directory}/{widget}.py",
    "actions": {
      "action-slug": {
        "slug": "action-slug",
        "names": {"en": "Action Name"},
        "icon": "⚙️",
        "description": {"en": "Action description"}
      }
    }
  }
}
```

## 🛠️ Step-by-Step Widget Creation

### Step 1: Create Library Structure
```bash
mkdir -p libraries/my-library/my-widget
```

### Step 2: Create Library Definition
Create `libraries/my-library/my-library.jsonld`:
```json
{
  "@context": {
    "@vocab": "https://litlfred.github.io/notebooks/ontology/",
    "mylib": "https://litlfred.github.io/notebooks/ontology/mylib#",
    "prov": "http://www.w3.org/ns/prov#",
    "dct": "http://purl.org/dc/terms/"
  },
  "@id": "https://litlfred.github.io/notebooks/libraries/my-library/",
  "@type": ["prov:Collection", "library:WidgetLibrary"],
  "dct:title": "My Widget Library",
  "widgets": {
    "my-widget": {
      "@id": "my-widget",
      "@type": "library:WidgetDefinition"
    }
  }
}
```

### Step 3: Create Schema Files
Create the six required schema files in the widget directory:
- `input.schema.json` 
- `output.schema.json`
- `widget.schema.json`
- `input.jsonld`
- `output.jsonld` 
- `widget.jsonld`

### Step 4: Implement Widget Class
Create `libraries/my-library/my-widget/my_widget.py`:
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from base_widget import WidgetExecutor
from typing import Dict, Any

class MyLibraryMyWidget(WidgetExecutor):
    """My widget implementation"""
    
    input_variables = {
        'input_param': 'default_value'
    }
    
    output_variables = {
        'success': True,
        'result': {}
    }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'success': True,
            'result': validated_input.get('input_param', 'processed')
        }
    
    def action_my_action(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action method for 'my-action' action"""
        # Validation specific to this action
        return self._execute_impl(validated_input)

def create_my_widget(widget_schema: Dict[str, Any]) -> MyLibraryMyWidget:
    """Factory function"""
    return MyLibraryMyWidget(widget_schema)
```

### Step 5: Register Widget
Add widget entry to `docs/weierstrass-playground/widget-schemas.json`

### Step 6: Validate Implementation
```bash
python3 -m py_compile libraries/my-library/my-widget/my_widget.py
python3 -m json.tool libraries/my-library/my-widget/input.schema.json
```

## ✅ Validation Checklist

Before submitting a new widget library:

- [ ] Directory structure follows requirements
- [ ] Widget class inherits from `WidgetExecutor`
- [ ] Class name follows umbrella widget hierarchy
- [ ] Input/output variables declared
- [ ] `_execute_impl` method implemented
- [ ] Action methods follow naming convention (`action_{slug}`)
- [ ] All 6 schema files created
- [ ] Schema URLs use GitHub Pages format
- [ ] JSON-LD contexts reference library definition
- [ ] Widget registered in widget-schemas.json
- [ ] Python files compile without errors
- [ ] JSON files validate successfully
- [ ] Widget executes and returns expected output

## 🔄 Library Updates

When updating existing libraries:

1. **Adding new widgets**: Follow creation steps for new widget directory
2. **Modifying existing widgets**: Update both Python implementation and schemas
3. **Changing library structure**: Update library JSON-LD definition
4. **URL changes**: Update all schema `$id` references consistently

## 📖 Examples

See existing libraries for complete examples:

- **Core Library**: `libraries/core/` - Basic widgets and shared functionality
- **PQ-Torus Library**: `libraries/pq-torus/` - Mathematical widgets with umbrella structure

## 🚀 Deployment

After development:

1. All files validate successfully
2. Widget-schemas.json includes new widgets  
3. GitHub Pages URLs resolve correctly
4. Interactive blackboard loads widgets properly

This completes the widget framework development guide. Follow these requirements to ensure your widget libraries are fully compliant and integrate seamlessly with the framework.