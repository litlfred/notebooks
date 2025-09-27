# Widget Libraries

This directory contains the consolidated widget library system for the notebooks repository. The widgets have been organized into modular libraries with proper JSON-LD schema definitions and shared base classes.

## Structure

```
libraries/
├── core/                           # Core Widget Library
│   ├── ontology/                   # Shared JSON-LD vocabulary
│   │   └── context.jsonld         
│   ├── common/                     # Shared schemas
│   │   ├── metadata.schema.json   
│   │   └── execution-result.schema.json
│   ├── sticky-note/               # Sticky note widget schemas
│   │   ├── input.schema.json      
│   │   ├── input.jsonld           
│   │   ├── output.schema.json     
│   │   ├── output.jsonld          
│   │   ├── widget.schema.json     
│   │   └── widget.jsonld          
│   ├── widgets/                   # Python widget implementations
│   │   ├── base_widget.py         # Base WidgetExecutor class
│   │   └── sticky_note.py         # StickyNoteWidget implementation
│   └── core.jsonld               # Core library definition
└── pq-torus/                      # PQ-Torus Mathematical Widget Library
    ├── weierstrass/              # Weierstrass ℘ function widget schemas
    │   ├── two-panel/            # Two-panel visualization schemas
    │   ├── three-panel/          # Three-panel analysis schemas
    │   ├── five-panel/           # Five-panel complete analysis
    │   ├── trajectories/         # Trajectory analysis schemas
    │   └── contours/             # Contour mapping schemas
    ├── widgets/                  # Python widget implementations
    │   ├── pq_torus.py           # PQTorusWidget (prime lattice parameters)
    │   ├── weierstrass_two_panel.py
    │   └── weierstrass_five_panel.py
    ├── example-notebook-graph.jsonld # PROV-O workflow example
    ├── input.schema.json         # PQ-Torus input validation
    ├── output.schema.json        # PQ-Torus output schema
    ├── widget.schema.json        # PQ-Torus widget instance schema
    └── pq-torus.jsonld           # PQ-Torus library definition
```

## Libraries

### Core Library (`libraries/core/`)

The **Core Library** provides fundamental widget functionality and shared infrastructure:

**Widgets:**
- **Sticky Note Widget** 📝: Markdown content widget with LaTeX support

**Shared Components:**
- `base_widget.py`: Base `WidgetExecutor` class with validation, actions, and error handling
- `common/`: Shared JSON schemas for metadata and execution results
- `ontology/`: JSON-LD vocabulary and context definitions

**GitHub Pages URL:** `https://litlfred.github.io/notebooks/libraries/core/core.jsonld`

### PQ-Torus Library (`libraries/pq-torus/`)

The **PQ-Torus Library** provides advanced mathematical widgets for prime lattice torus analysis and Weierstrass ℘-function visualization:

**Widgets:**
- **PQ-Torus Widget** 🔴: Prime lattice parameter definition (T = ℂ / L where L = ℤp + ℤqi)
- **Weierstrass Two-Panel** ∞: ℘(z) and ℘′(z) visualization
- **Weierstrass Five-Panel** 🔍: Complete ℘-function analysis with derivatives
- **Weierstrass Three-Panel**: ℘(z), Re(℘′(z)), Im(℘′(z)) analysis
- **Weierstrass Trajectories** 🌀: Particle trajectory integration

**Mathematical Features:**
- Prime number validation for lattice parameters
- Full provenance tracking with PROV-O
- Dependency system for parameter passing between widgets
- Complex mathematical visualization generation

**GitHub Pages URL:** `https://litlfred.github.io/notebooks/libraries/pq-torus/pq-torus.jsonld`

## Schema Organization

Each widget follows a standardized schema structure:

- `input.schema.json`: JSON Schema for input validation
- `input.jsonld`: JSON-LD context for input data with PROV-O integration
- `output.schema.json`: JSON Schema for output validation
- `output.jsonld`: JSON-LD context for output data with provenance
- `widget.schema.json`: JSON Schema for widget instance definition
- `widget.jsonld`: JSON-LD context for widget instances

All schemas use GitHub Pages URLs and are CORS-compatible for cross-origin requests.

## Usage

### Python Widget Development

1. **Inherit from Base Class:**
   ```python
   from base_widget import WidgetExecutor
   
   class MyWidget(WidgetExecutor):
       def _execute_impl(self, validated_input):
           # Widget logic here
           return {'success': True, 'result': 'data'}
   ```

2. **Override Validation (if needed):**
   ```python
   def validate_input(self, input_data):
       # Custom validation logic
       return validated_data
   ```

3. **Register in widget-schemas.json:**
   ```json
   {
     "my-widget": {
       "id": "my-widget",
       "input_schemas": ["https://litlfred.github.io/notebooks/libraries/my-lib/widget/input.schema.json"]
     }
   }
   ```

### Interactive Blackboard

The widget libraries integrate with the interactive blackboard system at:
`https://litlfred.github.io/notebooks/weierstrass-playground/board.html`

Features:
- Visual drag-and-drop widget placement
- Dependency connections (PQ-Torus → Weierstrass widgets)
- Real-time execution with status indicators
- Schema-based configuration forms

## Migration from Old System

This library system replaces the previous schema organization:

**Removed:**
- `docs/schemas/` - Old named schema files
- `docs/schema/` - Old directory-based system

**Added:**
- Modular library organization
- Shared base classes
- Proper inheritance hierarchy
- GitHub Pages URLs with library prefixes

## Development Guidelines

### Adding New Widgets

1. Choose appropriate library (`core/`, `pq-torus/`, or create new library)
2. Create widget directory with 6 schema files
3. Implement Python widget inheriting from `WidgetExecutor`
4. Update library JSON-LD definition
5. Register in `docs/weierstrass-playground/widget-schemas.json`
6. Test GitHub Pages URL resolution

### Creating New Libraries

1. Create `libraries/{library-name}/` directory
2. Create `{library-name}.jsonld` definition file
3. Organize widgets with proper schema structure
4. Add Python implementations in `widgets/` subdirectory
5. Update documentation and widget registry

## Testing

The library structure has been tested for:
- ✅ JSON validity of all schema files
- ✅ JSON-LD validity of context files
- ✅ Python syntax compilation of all widgets
- ✅ Widget instantiation and execution
- ✅ Input validation and error handling
- ✅ Dependency resolution between widgets

## Documentation

- **Complete Framework**: `docs/widget-framework.md`
- **JSON Schema Specification**: `docs/json-schema-specification.md`
- **Widget Overview**: `docs/widget-overview.md`
- **Architecture Examples**: `docs/architecture-examples.md`