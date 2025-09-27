# Widget Framework JSON Schemas

This directory contains the named JSON schemas for the widget framework, designed for GitHub Pages deployment with proper URLs and schema reusability.

## Schema Files

### Core Schemas

- **`common.json`** - Reusable definitions for metadata, execution results, data structures
- **`widget-definition.json`** - Schema for widget configuration structure with multiple schema support

### Widget-Specific Schemas

- **`sticky-note.json`** - Input/output schemas for sticky note widgets
- **`python-code.json`** - Schemas for Python code execution widgets  
- **`weierstrass.json`** - Schemas for Weierstrass ℘ function mathematical widgets
- **`data-visualization.json`** - Schemas for data plotting and generation widgets

## URL Structure

All schemas are accessible via GitHub Pages at:

```
https://litlfred.github.io/notebooks/schemas/{schema-name}.json
```

### Fragment References

Use fragment notation to reference specific definitions:

```json
{
  "$ref": "https://litlfred.github.io/notebooks/schemas/common.json#/definitions/metadata"
}
```

## Schema Composition

Schemas support composition through:

1. **External References**: Reference definitions from other schemas
2. **allOf Composition**: Combine multiple schemas into one
3. **Schema Arrays**: Multiple schemas with precedence order

### Example: Sticky Note Widget

```json
{
  "input_schemas": [
    "https://litlfred.github.io/notebooks/schemas/sticky-note.json#/definitions/input"
  ],
  "output_schemas": [
    "https://litlfred.github.io/notebooks/schemas/sticky-note.json#/definitions/output"
  ]
}
```

### Example: Complex Widget with Multiple Schemas

```json
{
  "input_schemas": [
    "https://litlfred.github.io/notebooks/schemas/weierstrass.json#/definitions/weierstrass_input",
    {
      "type": "object",
      "properties": {
        "contours": {"type": "integer", "default": 10},
        "saturation": {"type": "number", "default": 0.3}
      }
    }
  ]
}
```

## Schema Precedence

When multiple schemas are specified:
1. **First schema takes precedence** for conflicting properties
2. Properties from later schemas are **merged** if no conflict
3. **Validation** occurs against the combined schema

## Validation

All schemas are valid JSON Schema Draft 7 and can be validated using standard JSON Schema validators.

## Adding New Schemas

1. Create new `.json` file with proper `$id` URL
2. Reference common definitions from `common.json`
3. Update widget definitions in `../weierstrass-playground/widget-schemas.json`
4. Test JSON validity and schema references
5. Update documentation

## GitHub Pages Deployment

These schemas are automatically deployed to GitHub Pages and are available for cross-origin requests with proper CORS headers.