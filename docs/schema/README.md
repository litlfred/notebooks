# Widget Schema & JSON-LD Framework

This directory contains the complete schema and JSON-LD framework for the widget system, supporting PROV-O-based notebook graphs and GitHub Pages deployment.

## Directory Structure

Each widget has its own directory with standardized naming:

```
notebooks/schema/
├── ontology/
│   └── context.jsonld           # Shared JSON-LD context
├── common/
│   ├── execution-result.schema.json  # Shared execution result schema
│   └── metadata.schema.json          # Shared metadata schema
├── weierstrass/
│   ├── input.schema.json        # Weierstrass input schema
│   ├── input.jsonld            # Weierstrass input JSON-LD
│   ├── output.schema.json      # Weierstrass output schema
│   ├── output.jsonld           # Weierstrass output JSON-LD
│   ├── widget.schema.json      # Weierstrass widget schema
│   └── widget.jsonld           # Weierstrass widget JSON-LD
├── pq-torus/
│   ├── input.schema.json       # PQ-Torus input schema
│   ├── input.jsonld           # PQ-Torus input JSON-LD
│   ├── output.schema.json     # PQ-Torus output schema
│   ├── output.jsonld          # PQ-Torus output JSON-LD
│   ├── widget.schema.json     # PQ-Torus widget schema
│   └── widget.jsonld          # PQ-Torus widget JSON-LD
├── sticky-note/
│   ├── input.schema.json      # Sticky note input schema
│   ├── input.jsonld          # Sticky note input JSON-LD
│   ├── output.schema.json    # Sticky note output schema
│   ├── output.jsonld         # Sticky note output JSON-LD
│   ├── widget.schema.json    # Sticky note widget schema
│   └── widget.jsonld         # Sticky note widget JSON-LD
└── example-notebook-graph.jsonld # Example PROV-O notebook graph
```

## File Naming Convention

Each widget directory contains exactly 6 files:
- `input.schema.json` - JSON Schema for input validation
- `input.jsonld` - JSON-LD context for input data
- `output.schema.json` - JSON Schema for output validation  
- `output.jsonld` - JSON-LD context for output data
- `widget.schema.json` - JSON Schema for widget instances
- `widget.jsonld` - JSON-LD context for widget instances

## Type Naming

Types use flat, human-readable names with prefixes:
- **Weierstrass**: `weier:input`, `weier:output`, `weier:widget`
- **PQ-Torus**: `pqt:input`, `pqt:output`, `pqt:widget`  
- **Sticky Note**: `sticky:input`, `sticky:output`, `sticky:widget`

All types include `prov:Entity` for PROV-O compatibility:
```json
"@type": ["prov:Entity", "weier:input"]
```

## Schema & JSON-LD Linking

Every JSON-LD file references its corresponding schema using `dct:conformsTo`:
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld",
    "https://litlfred.github.io/notebooks/schema/ontology/context.jsonld"
  ],
  "@type": ["prov:Entity", "weier:input"],
  "dct:conformsTo": "./input.schema.json"
}
```

## Contexts

All JSON-LD files use two contexts:
1. **PROV-O**: `https://www.w3.org/ns/prov-o.jsonld`
2. **Widget Ontology**: `https://litlfred.github.io/notebooks/schema/ontology/context.jsonld`

The widget context defines prefixes and common terms:
```json
{
  "@context": {
    "weier": "https://litlfred.github.io/notebooks/ontology/weier#",
    "pqt": "https://litlfred.github.io/notebooks/ontology/pqt#",
    "sticky": "https://litlfred.github.io/notebooks/ontology/sticky#",
    "prov": "http://www.w3.org/ns/prov#",
    "dct": "http://purl.org/dc/terms/"
  }
}
```

## GitHub Pages URLs

All schemas are accessible via GitHub Pages:
- Base URL: `https://litlfred.github.io/notebooks/schema/`
- Widget schemas: `https://litlfred.github.io/notebooks/schema/{widget}/input.schema.json`
- JSON-LD contexts: `https://litlfred.github.io/notebooks/schema/{widget}/input.jsonld`

## PROV-O Integration

The framework supports full PROV-O provenance tracking:

### Widget Execution Flow
1. **Widget Instance** (`prov:Entity`) - Configuration and parameters
2. **Activity** (`prov:Activity`) - Execution process  
3. **Output** (`prov:Entity`) - Generated results

### Dependencies
Widgets can depend on outputs from other widgets:
```json
{
  "dependencies": [
    {
      "source_widget": "urn:uuid:pq-torus-widget-1",
      "source_path": "p",
      "target_path": "p"
    }
  ]
}
```

## Example Usage

### Widget Instance Creation
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld", 
    "https://litlfred.github.io/notebooks/schema/ontology/context.jsonld"
  ],
  "@id": "urn:uuid:widget-123",
  "@type": ["prov:Entity", "weier:widget"],
  "dct:conformsTo": "https://litlfred.github.io/notebooks/schema/weierstrass/widget.schema.json",
  "widget_id": "weier-1",
  "widget_type": "wp-two-panel",
  "input": {"p": 11, "q": 5, "N": 3}
}
```

### Notebook Graph
See `example-notebook-graph.jsonld` for a complete example showing:
- Widget dependencies (PQ-Torus → Weierstrass)
- PROV-O activity tracking
- Proper JSON-LD structure

## Validation

All schemas are valid JSON Schema Draft 7 and can be validated using standard tools:

```bash
# Validate schema syntax
ajv validate -s input.schema.json -d input-data.json

# Validate JSON-LD structure  
jsonld validate input.jsonld
```

## Adding New Widgets

1. Create widget directory: `mkdir schema/{widget-name}/`
2. Copy template files from existing widget
3. Update schemas with widget-specific properties
4. Define widget prefix in `ontology/context.jsonld`
5. Test all URLs resolve via GitHub Pages
6. Update documentation

## Compatibility

This schema system is:
- **GitHub Pages Ready**: All URLs resolve properly
- **CORS Compatible**: Supports cross-origin requests
- **PROV-O Compliant**: Full provenance tracking
- **JSON Schema Valid**: Draft 7 compliant
- **Backward Compatible**: Works with existing widget framework

The system supports complex notebook graphs with proper mathematical provenance, dependency tracking, and semantic web standards.