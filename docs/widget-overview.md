# Widget Library Framework Overview

The notebooks repository includes a comprehensive widget framework organized into modular libraries for building interactive mathematical computing environments. This document provides an overview of all available widget libraries.

## Framework Architecture

The widget framework uses a library-based organization with JSON-LD integration for provenance tracking:

```
libraries/
├── core/                           # Core widget library
│   ├── ontology/context.jsonld    # Shared JSON-LD vocabulary  
│   ├── common/                     # Shared schemas
│   ├── sticky-note/               # Markdown note widgets
│   ├── widgets/                   # Python widget implementations
│   │   ├── base_widget.py         # Base widget executor class
│   │   └── sticky_note.py         # Sticky note implementation
│   └── core.jsonld               # Core library definition
└── pq-torus/                      # PQ-Torus mathematical widget library
    ├── weierstrass/              # Weierstrass ℘ function widgets
    ├── widgets/                  # Python widget implementations  
    │   ├── pq_torus.py           # PQ-Torus implementation
    │   ├── weierstrass_two_panel.py
    │   └── weierstrass_five_panel.py
    ├── example-notebook-graph.jsonld # PROV-O workflow example
    └── pq-torus.jsonld           # PQ-Torus library definition
```

## Widget Libraries

### Core Library

The **Core Library** (`libraries/core/`) provides base functionality and essential widgets:

#### 1. Sticky Note Widget 📝

**Purpose**: Simple markdown content widget for documentation and notes

**Schema**: `https://litlfred.github.io/notebooks/libraries/core/sticky-note/`

**Input**:
- `content`: Markdown content (default: "# New Note\n\nEdit to add content...")
- `show_note`: Whether to show note by default (boolean, default: true)

**Output**:
- `rendered_html`: HTML rendered from markdown
- `metadata`: Rendering metadata including visibility and content length

**Use Cases**:
- Documentation within computational workflows
- Mathematical explanations with LaTeX support
- Annotations for complex calculations

### PQ-Torus Mathematical Library

The **PQ-Torus Library** (`libraries/pq-torus/`) provides advanced mathematical widgets for prime lattice torus analysis and Weierstrass ℘-function visualization:

#### 2. PQ-Torus Widget 🔴

**Purpose**: Defines torus T = ℂ / L where L = ℤp + ℤqi with prime lattice parameters

**Schema**: `https://litlfred.github.io/notebooks/libraries/pq-torus/`

**Input**:
- `p`: First prime integer (2-100, default: 11)
- `q`: Second prime integer (2-100, default: 5)

**Output**:
- `p`, `q`: Validated prime parameters
- `torus_description`: Mathematical description "T = ℂ / L where L = ℤ11 + ℤ5i"
- `lattice_description`: Lattice structure description
- `prime_validation`: Validation status for both parameters
- `markdown_content`: Rich mathematical documentation

**Use Cases**:
- Parameter source for Weierstrass function analysis
- Prime number lattice research
- Mathematical torus visualization setup

**Dependencies**: Serves as input to all Weierstrass widgets

#### 3. Weierstrass Function Widgets ∞

**Purpose**: Visualization and analysis of Weierstrass ℘ functions using PQ-Torus lattice parameters

**Schema**: `https://litlfred.github.io/notebooks/libraries/pq-torus/weierstrass/`

**Input**:
- `p`: Lattice parameter p (prime integer, 2-100, default: 11)  
- `q`: Lattice parameter q (prime integer, 2-100, default: 5)
- `N`: Truncation level (0-6, default: 3)
- `grid_size`: Computation grid dimensions (default: 100x100)

**Output**:
- `plot_data`: Generated visualization (base64 image, width, height, format)
- `field_data`: ℘(z) field data and analysis points
- `lattice_params`: Lattice description and mathematical properties
- `visualization_params`: Rendering parameters and configuration

**Widget Types**:
- `weierstrass-two-panel`: ℘(z) and ℘′(z) visualization
- `weierstrass-three-panel`: ℘(z), Re(℘′(z)), Im(℘′(z)) analysis  
- `weierstrass-five-panel`: Complete field analysis with derivatives
- `weierstrass-trajectories`: Particle trajectory integration

**Dependencies**: Can receive parameters from PQ-Torus widgets via dependency system

## Library URLs

All widget libraries are accessible via GitHub Pages:

- **Core Library**: `https://litlfred.github.io/notebooks/libraries/core/core.jsonld`
- **PQ-Torus Library**: `https://litlfred.github.io/notebooks/libraries/pq-torus/pq-torus.jsonld`

## Removed Legacy Widgets

The following widget descriptions have been removed as part of the library consolidation:

- Old individual schema files from `docs/schemas/` (consolidated into libraries)

## Interactive Blackboard

The widget framework includes a visual programming interface:

🚀 **[Try the interactive blackboard](https://litlfred.github.io/notebooks/weierstrass-playground/board.html)**

Features:
- Drag-and-drop widget placement
- Visual dependency connections between PQ-Torus and Weierstrass widgets
- Real-time execution with status indicators
- Schema-based configuration forms
- Export capabilities for mathematical workflows

## Development Guidelines

### Adding New Widgets to Libraries

1. Choose appropriate library (`core/` or `pq-torus/`) or create new library
2. Create widget directory with schema files
3. Update library JSON-LD definition
4. Add widget to registry: `docs/weierstrass-playground/widget-schemas.json`
5. Implement Python backend inheriting from `base_widget.py`
6. Test all URLs resolve via GitHub Pages

### Schema Requirements

- Use library URLs: `https://litlfred.github.io/notebooks/libraries/{library-name}/`
- Include PROV-O compatibility: `"@type": ["prov:Entity", "{prefix}:{type}"]`
- Reference schemas: `"dct:conformsTo": "./input.schema.json"`
- Follow JSON Schema Draft 7 specification

## Migration from Old Schema System

This document reflects the consolidated library structure. The following changes were made:

- **Removed**: `docs/schemas/` directory (old named schema system)
- **Removed**: `docs/schema/` directory (old directory-based system)
- **Added**: `libraries/core/` and `libraries/pq-torus/` with proper organization
- **Updated**: All schema URLs to point to new library locations
- **Updated**: Widget implementations to use shared base classes

## Library Documentation

For detailed documentation on each library:

- **Core Library**: See `libraries/core/core.jsonld` and widget implementations
- **PQ-Torus Library**: See `libraries/pq-torus/pq-torus.jsonld` and widget implementations
- **Framework Documentation**: `docs/widget-framework.md`
- **Schema Specifications**: `docs/json-schema-specification.md`