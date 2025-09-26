# Widget Framework JSON Schema Specification

## Overview

The Widget Framework uses **named JSON Schema references with proper URLs** to define widget interfaces, providing type safety, automatic validation, dynamic UI generation, and **schema reusability**. This system supports **GitHub Pages deployment** with relative URLs and **schema precedence** for complex widget definitions.

## Schema Architecture

### Named Schema System

All schemas are hosted at `https://litlfred.github.io/notebooks/schemas/` and use proper JSON Schema `$id` references:

- **Common schemas**: `common.json` - Reusable definitions for metadata, execution results, etc.
- **Widget definitions**: `widget-definition.json` - Schema for widget configuration structure  
- **Specialized schemas**: `sticky-note.json`, `python-code.json`, `weierstrass.json`, etc.

### Schema Reusability  

Schemas can be composed using:
- **External references**: `"$ref": "https://litlfred.github.io/notebooks/schemas/common.json#/definitions/metadata"`
- **Schema composition**: `"allOf": [{"$ref": "..."}]` to combine multiple schemas
- **Schema inheritance**: Base schemas extended by specialized widgets

### Schema Precedence Order

Widgets can specify **multiple schemas** for inputs/outputs with **precedence order**:

```json
{
  "input_schemas": [
    "https://litlfred.github.io/notebooks/schemas/weierstrass.json#/definitions/weierstrass_input",
    {
      "type": "object",
      "properties": {
        "additional_param": {"type": "string"}
      }
    }
  ]
}
```

**First schema has precedence** - properties from later schemas are merged if not conflicting.

## Widget Schema Root Structure

```json
{
  "$schema": "https://litlfred.github.io/notebooks/schemas/widget-definition.json",
  "widget-schemas": {
    "widget-id": {
      // Widget definition
    }
  }
}
```

## Common Schema Definitions

### Base Metadata Schema
**URL**: `https://litlfred.github.io/notebooks/schemas/common.json#/definitions/metadata`

```json
{
  "type": "object",
  "properties": {
    "execution_time": {"type": "number"},
    "timestamp": {"type": "string", "format": "date-time"},
    "widget_id": {"type": "string"},
    "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"}
  }
}
```

### Execution Result Schema
**URL**: `https://litlfred.github.io/notebooks/schemas/common.json#/definitions/execution_result`

```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "error": {"type": "string"},
    "metadata": {"$ref": "#/definitions/metadata"}
  },
  "required": ["success"]
}
```

### Markdown Content Schema
**URL**: `https://litlfred.github.io/notebooks/schemas/common.json#/definitions/markdown_content`

```json
{
  "type": "object",
  "properties": {
    "content": {"type": "string", "default": ""},
    "render_latex": {"type": "boolean", "default": true},
    "variables": {
      "type": "object",
      "patternProperties": {
        "^[a-zA-Z_][a-zA-Z0-9_]*$": {
          "type": ["string", "number", "boolean"]
        }
      }
    }
  },
  "required": ["content"]
}
```

### Visualization Output Schema
**URL**: `https://litlfred.github.io/notebooks/schemas/common.json#/definitions/visualization_output`

```json
{
  "type": "object",
  "properties": {
    "image_base64": {
      "type": "string",
      "pattern": "^data:image/[a-zA-Z]+;base64,"
    },
    "width": {"type": "integer", "minimum": 1},
    "height": {"type": "integer", "minimum": 1},
    "mime_type": {"enum": ["image/png", "image/jpeg", "image/svg+xml"]},
    "alt_text": {"type": "string"}
  },
  "required": ["image_base64", "width", "height"]
}
```

## Widget Definition Schema

**URL**: `https://litlfred.github.io/notebooks/schemas/widget-definition.json`

### Widget Structure

```json
{
  "id": "widget-id",
  "name": "Widget Name",
  "description": "Widget description",
  "category": "content|computation|visualization|data|utility",
  "icon": "📝",
  "input_schemas": [
    "https://litlfred.github.io/notebooks/schemas/schema-name.json#/definitions/input",
    { /* inline schema */ }
  ],
  "output_schemas": [
    "https://litlfred.github.io/notebooks/schemas/schema-name.json#/definitions/output"
  ],
  "python_script": "widgets/widget_script.py",
  "version": "1.0.0",
  "author": "Author Name",
  "tags": ["tag1", "tag2"]
}
```

### Schema References

Schema references can be:
1. **External URL**: `"https://litlfred.github.io/notebooks/schemas/common.json#/definitions/metadata"`
2. **Inline object**: `{"type": "object", "properties": {...}}`

### Multiple Schema Support

**Input/Output Schema Arrays** allow composition:

```json
{
  "input_schemas": [
    "https://litlfred.github.io/notebooks/schemas/weierstrass.json#/definitions/weierstrass_input",
    "https://litlfred.github.io/notebooks/schemas/common.json#/definitions/ui_configuration", 
    {
      "type": "object",
      "properties": {
        "custom_param": {"type": "string"}
      }
    }
  ]
}
```

**Precedence Order**: First schema takes precedence for conflicting properties.

## Specialized Widget Schemas

### Sticky Note Widget
**URL**: `https://litlfred.github.io/notebooks/schemas/sticky-note.json`

Input combines markdown content with UI configuration:
```json
{
  "allOf": [
    {"$ref": "https://litlfred.github.io/notebooks/schemas/common.json#/definitions/markdown_content"},
    {"$ref": "https://litlfred.github.io/notebooks/schemas/common.json#/definitions/ui_configuration"}
  ],
  "properties": {
    "show_note": {"type": "boolean", "default": true}
  }
}
```

### Python Code Widget  
**URL**: `https://litlfred.github.io/notebooks/schemas/python-code.json`

Specialized for code execution:
```json
{
  "input": {
    "properties": {
      "code": {"type": "string"},
      "imports": {"type": "array", "items": {"type": "string"}},
      "variables": {"type": "object"}
    }
  },
  "output": {
    "allOf": [{"$ref": "common.json#/definitions/execution_result"}],
    "properties": {
      "result": {"description": "Execution result"},
      "stdout": {"type": "string"},
      "stderr": {"type": "string"}
    }
  }
}
```

### Weierstrass Function Widgets
**URL**: `https://litlfred.github.io/notebooks/schemas/weierstrass.json`

Mathematical function parameters:
```json
{
  "weierstrass_input": {
    "properties": {
      "p": {"type": "number", "minimum": 0.1, "maximum": 20},
      "q": {"type": "number", "minimum": 0.1, "maximum": 20}, 
      "N": {"type": "integer", "minimum": 0, "maximum": 6},
      "grid_size": {
        "type": "object",
        "properties": {
          "x": {"type": "integer", "minimum": 50, "maximum": 300},
          "y": {"type": "integer", "minimum": 50, "maximum": 300}
        }
      }
    }
  }
}
```

## GitHub Pages Deployment

### URL Structure
- **Base URL**: `https://litlfred.github.io/notebooks/schemas/`
- **Schema files**: `common.json`, `widget-definition.json`, `sticky-note.json`, etc.
- **Fragment references**: `#/definitions/metadata`

### Relative References
Schemas can use relative references when deployed together:
```json
{
  "$ref": "./common.json#/definitions/metadata"
}
```

### CORS Support
GitHub Pages automatically serves JSON files with proper CORS headers for cross-origin requests.

## Widget Definition Schema

### Complete Widget Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "widget-schemas": {
      "type": "object",
      "patternProperties": {
        "^[a-z][a-z0-9-]*[a-z0-9]$": {
          "$ref": "#/definitions/Widget"
        }
      },
      "additionalProperties": false
    }
  },
  "definitions": {
    "Widget": {
      "type": "object",
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9-]*[a-z0-9]$",
          "description": "Unique widget identifier matching key"
        },
        "name": {
          "type": "string",
          "minLength": 1,
          "maxLength": 100,
          "description": "Human-readable widget name"
        },
        "description": {
          "type": "string",
          "minLength": 1,
          "maxLength": 500,
          "description": "Widget description for user interface"
        },
        "category": {
          "type": "string",
          "enum": ["content", "computation", "visualization", "data", "utility"],
          "description": "Widget category for organization"
        },
        "icon": {
          "type": "string",
          "pattern": "^(\\p{Emoji}|[a-zA-Z0-9_-]+)$",
          "description": "Unicode emoji or icon identifier"
        },
        "input_schema": {
          "$ref": "#/definitions/JSONSchema",
          "description": "JSON Schema for widget input parameters"
        },
        "output_schema": {
          "$ref": "#/definitions/JSONSchema", 
          "description": "JSON Schema for widget output data"
        },
        "python_script": {
          "type": "string",
          "pattern": "^widgets/[a-zA-Z0-9_/-]+\\.py$",
          "description": "Path to Python execution script"
        },
        "version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$",
          "description": "Semantic version number",
          "default": "1.0.0"
        },
        "author": {
          "type": "string",
          "description": "Widget author information"
        },
        "tags": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Searchable tags"
        },
        "experimental": {
          "type": "boolean",
          "default": false,
          "description": "Mark as experimental feature"
        }
      },
      "required": ["id", "name", "description", "category", "icon", "input_schema", "output_schema", "python_script"],
      "additionalProperties": false
    },
    "JSONSchema": {
      "type": "object",
      "properties": {
        "type": {
          "enum": ["object", "array", "string", "number", "integer", "boolean", "null"]
        },
        "properties": {
          "type": "object",
          "additionalProperties": {"$ref": "#/definitions/JSONSchemaProperty"}
        },
        "required": {
          "type": "array",
          "items": {"type": "string"}
        },
        "additionalProperties": {"type": "boolean"},
        "items": {"$ref": "#/definitions/JSONSchemaProperty"},
        "minItems": {"type": "integer", "minimum": 0},
        "maxItems": {"type": "integer", "minimum": 0},
        "patternProperties": {
          "type": "object",
          "additionalProperties": {"$ref": "#/definitions/JSONSchemaProperty"}
        }
      },
      "additionalProperties": true
    },
    "JSONSchemaProperty": {
      "type": "object", 
      "properties": {
        "type": {
          "anyOf": [
            {"enum": ["string", "number", "integer", "boolean", "array", "object", "null", "any"]},
            {"type": "array", "items": {"enum": ["string", "number", "integer", "boolean", "array", "object", "null"]}}
          ]
        },
        "description": {"type": "string"},
        "default": true,
        "minimum": {"type": "number"},
        "maximum": {"type": "number"},
        "minLength": {"type": "integer", "minimum": 0},
        "maxLength": {"type": "integer", "minimum": 0},
        "pattern": {"type": "string"},
        "enum": {"type": "array"},
        "format": {"type": "string"},
        "items": {"$ref": "#/definitions/JSONSchemaProperty"},
        "properties": {
          "type": "object",
          "additionalProperties": {"$ref": "#/definitions/JSONSchemaProperty"}
        },
        "required": {
          "type": "array", 
          "items": {"type": "string"}
        },
        "ui:widget": {
          "enum": ["textarea", "color", "date", "datetime", "email", "password", "range", "select", "radio", "checkbox", "file", "hidden"],
          "description": "UI widget type hint"
        },
        "ui:placeholder": {
          "type": "string",
          "description": "Placeholder text for input fields"
        },
        "ui:help": {
          "type": "string", 
          "description": "Help text displayed with field"
        },
        "ui:order": {
          "type": "integer",
          "description": "Display order in forms"
        }
      },
      "additionalProperties": true
    }
  }
}
```

## Input Schema Guidelines

### Standard Property Types

#### String Properties
```json
{
  "property_name": {
    "type": "string",
    "description": "Property description",
    "default": "default_value",
    "minLength": 1,
    "maxLength": 1000,
    "pattern": "^[a-zA-Z0-9_-]+$",
    "format": "email|uri|date|datetime|color",
    "enum": ["option1", "option2", "option3"],
    "ui:widget": "textarea|color|date|password",
    "ui:placeholder": "Enter value here...",
    "ui:help": "Additional guidance for users"
  }
}
```

#### Numeric Properties
```json
{
  "property_name": {
    "type": "number", // or "integer"
    "description": "Numeric parameter", 
    "default": 1.0,
    "minimum": 0,
    "maximum": 100,
    "multipleOf": 0.1,
    "ui:widget": "range",
    "ui:help": "Slider for numeric input"
  }
}
```

#### Boolean Properties
```json
{
  "property_name": {
    "type": "boolean",
    "description": "Toggle option",
    "default": true,
    "ui:widget": "checkbox|radio"
  }
}
```

#### Array Properties
```json
{
  "property_name": {
    "type": "array",
    "description": "List of values",
    "items": {
      "type": "string" // or any other type
    },
    "minItems": 1,
    "maxItems": 10,
    "uniqueItems": true,
    "default": []
  }
}
```

#### Object Properties
```json
{
  "property_name": {
    "type": "object",
    "description": "Nested configuration",
    "properties": {
      "nested_prop": {
        "type": "string",
        "default": "value"
      }
    },
    "required": ["nested_prop"],
    "additionalProperties": false
  }
}
```

### Special Property Patterns

#### Variables Object
For dynamic key-value pairs:
```json
{
  "variables": {
    "type": "object",
    "description": "Dynamic variables",
    "patternProperties": {
      "^[a-zA-Z_][a-zA-Z0-9_]*$": {
        "type": ["string", "number", "boolean"]
      }
    },
    "additionalProperties": false,
    "default": {}
  }
}
```

#### Complex Data Structures
```json
{
  "data": {
    "type": "object", 
    "properties": {
      "x": {
        "type": "array",
        "items": {"type": "number"},
        "description": "X coordinates"
      },
      "y": {
        "type": "array", 
        "items": {"type": "number"},
        "description": "Y coordinates"
      }
    },
    "required": ["x", "y"]
  }
}
```

## Output Schema Guidelines

### Standard Output Structure

```json
{
  "output_schema": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean",
        "description": "Execution success indicator"
      },
      "result": {
        "type": "any",
        "description": "Primary result data"
      },
      "error": {
        "type": "string",
        "description": "Error message if execution failed"
      },
      "metadata": {
        "type": "object",
        "properties": {
          "execution_time": {"type": "number"},
          "timestamp": {"type": "string"},
          "version": {"type": "string"}
        },
        "description": "Execution metadata"
      },
      "visualization": {
        "type": "object",
        "properties": {
          "image_base64": {"type": "string"},
          "width": {"type": "integer"},
          "height": {"type": "integer"},
          "mime_type": {"type": "string"}
        },
        "description": "Visualization output"
      },
      "data": {
        "type": "object|array",
        "description": "Structured data output"
      }
    }
  }
}
```

### Output Type Specifications

#### Image Output
```json
{
  "plot_data": {
    "type": "object",
    "properties": {
      "image_base64": {
        "type": "string",
        "pattern": "^data:image/[a-zA-Z]+;base64,",
        "description": "Base64 encoded image with data URI prefix"
      },
      "width": {
        "type": "integer",
        "minimum": 1,
        "description": "Image width in pixels"
      },
      "height": {
        "type": "integer", 
        "minimum": 1,
        "description": "Image height in pixels"
      },
      "mime_type": {
        "enum": ["image/png", "image/jpeg", "image/svg+xml"],
        "description": "Image MIME type"
      }
    },
    "required": ["image_base64", "width", "height"]
  }
}
```

#### Data Table Output
```json
{
  "table_data": {
    "type": "object",
    "properties": {
      "columns": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Column names"
      },
      "rows": {
        "type": "array", 
        "items": {
          "type": "array",
          "items": {"type": ["string", "number", "boolean", "null"]}
        },
        "description": "Row data"
      },
      "types": {
        "type": "array",
        "items": {"enum": ["string", "number", "boolean", "date"]},
        "description": "Column data types"
      }
    },
    "required": ["columns", "rows"]
  }
}
```

## UI Widget Type Extensions

The framework supports custom UI widget types through the `ui:widget` property:

### Standard UI Widgets

| Widget Type | Use Case | Properties |
|-------------|----------|------------|
| `text` | Single-line text input | `minLength`, `maxLength`, `pattern` |
| `textarea` | Multi-line text input | `minLength`, `maxLength` |
| `number` | Numeric input | `minimum`, `maximum`, `step` |
| `range` | Slider input | `minimum`, `maximum`, `step` |
| `select` | Dropdown selection | `enum` values |
| `radio` | Radio button group | `enum` values |
| `checkbox` | Single checkbox | Boolean type |
| `color` | Color picker | String type with `format: "color"` |
| `date` | Date picker | String type with `format: "date"` |
| `datetime` | Date-time picker | String type with `format: "datetime"` |
| `file` | File upload | String type for file path |
| `hidden` | Hidden field | Any type, not displayed |

### Custom Widget Properties

```json
{
  "advanced_config": {
    "type": "object",
    "ui:widget": "object-editor",
    "ui:options": {
      "expandable": true,
      "addable": true,
      "removable": true
    }
  }
}
```

## Validation Rules

### Widget ID Constraints
- Must be lowercase alphanumeric with hyphens
- Start and end with alphanumeric character
- Pattern: `^[a-z][a-z0-9-]*[a-z0-9]$`
- Examples: `sticky-note`, `data-plot`, `wp-two-panel`

### Schema Validation
- All schemas must be valid JSON Schema Draft 7
- Input schemas must be of type "object" 
- Output schemas should include success/error handling
- Required properties must be specified

### File Path Constraints
- Python scripts must be in `widgets/` directory
- Path pattern: `^widgets/[a-zA-Z0-9_/-]+\\.py$`
- Example: `widgets/sticky_note.py`

## Migration and Versioning

### Schema Evolution
```json
{
  "version": "2.1.0",
  "deprecated": {
    "old_property": {
      "replacement": "new_property",
      "removal_version": "3.0.0"
    }
  },
  "changes": [
    {
      "version": "2.1.0",
      "type": "addition",
      "property": "new_feature",
      "description": "Added new configuration option"
    }
  ]
}
```

### Backward Compatibility
- Maintain support for previous schema versions
- Provide automatic migration for deprecated properties
- Clear deprecation warnings with migration paths
- Semantic versioning for breaking changes

## Best Practices

### Schema Design
1. **Clear Descriptions**: Every property needs helpful documentation
2. **Sensible Defaults**: Provide reasonable default values
3. **Appropriate Constraints**: Use min/max, patterns for validation
4. **Consistent Naming**: Use snake_case for properties
5. **Logical Grouping**: Group related properties in objects

### Property Organization
```json
{
  "input_schema": {
    "type": "object",
    "properties": {
      // Core functionality parameters first
      "data": { /* primary data input */ },
      
      // Configuration options
      "settings": {
        "type": "object",
        "properties": {
          "advanced_option": { /* grouped settings */ }
        }
      },
      
      // UI and display options last
      "display": {
        "type": "object", 
        "properties": {
          "show_legend": { /* display options */ }
        }
      }
    }
  }
}
```

### Error Handling
```json
{
  "output_schema": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "result": {"type": "any"},
      "error": {
        "type": "object",
        "properties": {
          "type": {"enum": ["validation", "execution", "timeout", "system"]},
          "message": {"type": "string"},
          "details": {"type": "object"},
          "recoverable": {"type": "boolean"}
        }
      }
    }
  }
}
```

This JSON Schema specification ensures consistent, validated widget definitions that enable automatic UI generation and robust error handling throughout the framework.