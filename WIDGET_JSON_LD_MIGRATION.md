# Widget JSON-LD Migration Guide

This document describes the major refactoring that removes hard-coded class name to JSON-LD ID mappings and implements proper JSON-LD schema initialization for widgets.

## Key Changes

### 1. Python Widget System (`libraries/core/base_widget.py`)

**Before:**
- Hard-coded `_class_name_to_jsonld_id` dictionary mapping Python class names to JSON-LD identifiers
- Widget initialization with only widget schema parameter
- No schema alignment validation

**After:**
- JSON-LD schema passed as initialization parameter
- Dynamic JSON-LD ID and type extraction from schema
- Schema alignment validation with warning system
- Configurable warning display for mismatched schemas

**New Constructor:**
```python
def __init__(self, widget_schema: Dict[str, Any], jsonld_schema: Optional[Dict[str, Any]] = None):
    # JSON-LD schema initialization
    self.jsonld_schema = jsonld_schema or {}
    self.jsonld_id = self._extract_jsonld_id()
    self.jsonld_type = self._extract_jsonld_type()
    
    # Schema validation
    self.schema_warnings = []
    self._validate_schema_alignment()
```

### 2. JavaScript Board Application (`docs/weierstrass-playground/board-app.js`)

**Enhanced Widget Creation:**
- JSON-LD schema generation from widget schemas
- Schema alignment validation
- Warning display in widget UI
- Enhanced hamburger menu with warnings section

**New Library Organization:**
- Umbrella library display (Core Widgets, PQ-Torus, etc.)
- Pull-out tray for >4 libraries
- Library metadata support from notebooks

### 3. Notebook JSON-LD Enhancement

**Notebooks now include library metadata:**
```json
{
  "notebook:libraries": [
    {
      "@id": "https://litlfred.github.io/notebooks/libraries/core/core.jsonld",
      "name": "core",
      "displayName": "Core Widgets", 
      "icon": "🧩",
      "description": "Essential widgets for notebook functionality"
    }
  ]
}
```

## UI Enhancements

### Warning System
- ⚠️ Warning icons appear on widgets with schema mismatches
- Hamburger menu shows warnings section with details
- Warnings include parameter mismatches between JSON-LD and Python signatures

### Library Organization
- Widgets grouped by umbrella library (Core, PQ-Torus, etc.)
- Pull-out tray automatically appears when >4 libraries present
- Library icons and display names from notebook metadata

## Breaking Changes

### Removed Features
- `_class_name_to_jsonld_id` mapping dictionary
- `_jsonld_id_to_class_name` reverse mapping 
- Class-based `get_jsonld_id()` method
- `get_class_for_jsonld_id()` method

### Migration Required For
- Custom widget implementations extending `WidgetExecutor`
- Code using hard-coded JSON-LD ID mappings
- Widget creation code not passing JSON-LD schemas

## Example Usage

### Creating Widget with JSON-LD Schema
```python
from libraries.core.base_widget import create_widget

widget_schema = {
    'id': 'my-widget',
    'name': 'My Widget',
    'actions': {...}
}

jsonld_schema = {
    '@id': 'my:widget',
    '@type': ['prov:Entity', 'my:widget'],
    'input': {
        'properties': {
            'param1': {'type': 'string'},
            'param2': {'type': 'number'}
        }
    }
}

widget = create_widget('my-widget', widget_schema, jsonld_schema)
```

### JavaScript Widget Creation
```javascript
// JSON-LD schema automatically generated from widget schema
const widget = this.boardApp.createWidget(widgetType, x, y, config, jsonldSchema);

// Check for warnings
if (widget.warnings.length > 0) {
    console.log('Schema warnings detected:', widget.warnings);
}
```

## Testing

The migration includes comprehensive validation:
- Python unit tests for JSON-LD initialization
- Schema alignment warning detection
- UI functionality for warning display
- Library organization and tray functionality

All existing functionality is preserved while adding the new JSON-LD capabilities.