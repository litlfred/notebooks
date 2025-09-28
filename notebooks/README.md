# Widget Framework Notebook Examples

This directory contains three carefully curated examples demonstrating the widget framework's capabilities, from basic usage to complete mathematical workflows.

## 📋 Example Notebooks

### 1. Simple Sticky Notes (`01-simple-sticky-notes.jsonld`)
- **Purpose**: Basic introduction to the widget framework
- **Widgets Used**: 2 × Sticky Note widgets from Core library
- **Features Demonstrated**:
  - Basic markdown content rendering
  - Widget layout and positioning
  - Simple JSON-LD structure with PROV-O
  - Widget metadata and timestamps

**Best for**: New users learning the framework basics

### 2. Minimal PQ-Torus (`02-minimal-pq-torus.jsonld`)
- **Purpose**: Introduction to PQ-Torus mathematical widgets
- **Widgets Used**: 
  - 1 × PQ-Torus umbrella widget
  - 1 × Sticky Note for documentation
- **Features Demonstrated**:
  - Prime parameter validation (p=5, q=7)
  - Torus definition: T = ℂ / L where L = ℤp + ℤqi
  - Mathematical property calculation
  - Mixed widget library usage
  - Proper input/output schema conformance

**Best for**: Users exploring mathematical widget capabilities

### 3. Complete PQ-Torus Workflow (`03-complete-pq-torus-workflow.jsonld`)
- **Purpose**: Comprehensive demonstration of umbrella widget pattern
- **Widgets Used**:
  - 1 × PQ-Torus umbrella widget (p=11, q=5)
  - 4 × Weierstrass sub-widgets:
    - Two-panel visualization (℘(z), ℘′(z))
    - Five-panel complete analysis
    - Trajectory analysis 
    - Contour mapping
  - 1 × Summary sticky note
- **Features Demonstrated**:
  - **Umbrella widget pattern** with parameter propagation
  - **Dependency linkages** between umbrella and sub-widgets
  - **Hierarchical widget IDs** (`pq-torus.weierstrass.two-panel`)
  - **Complete PROV-O provenance** tracking
  - **Sub-widget type declarations** with proper IRIs
  - **Mathematical workflow orchestration**

**Best for**: Advanced users implementing complex mathematical analysis workflows

## 🔗 Widget Relationship Patterns

### Umbrella Widget Architecture
The complete example demonstrates the umbrella widget pattern:

```
PQ-Torus (Umbrella)
├── Provides: p, q parameters
├── Validates: Prime number constraints
└── Connects to Sub-Widgets:
    ├── Weierstrass Two-Panel
    ├── Weierstrass Five-Panel  
    ├── Weierstrass Trajectories
    └── Weierstrass Contours
```

### Parameter Flow
```
Input: p=11, q=5
↓
PQ-Torus Widget (validation & processing)
↓
Output: Validated parameters + torus description
↓
Sub-Widgets (automatic parameter inheritance)
↓
Mathematical Analysis Results
```

## 📊 Schema Conformance

Each example demonstrates proper JSON-LD structure with:

- **Context Declaration**: References to library definitions
- **Type Declarations**: Proper `@type` arrays with PROV-O and library types
- **Schema Conformance**: `dct:conformsTo` references to widget schemas
- **Input/Output Typing**: Proper typing for widget inputs and outputs
- **Dependency Declaration**: Explicit parameter linkages between widgets
- **Provenance Tracking**: Complete PROV-O activity and entity relationships

## 🚀 Usage

These examples can be:

1. **Loaded into the interactive blackboard** at `docs/weierstrass-playground/board.html`
2. **Used as templates** for creating new mathematical workflows  
3. **Referenced for JSON-LD structure** when building custom notebooks
4. **Validated against schemas** to ensure compliance

## 🔍 Key Improvements in Complete Example

The complete example addresses the previous JSON-LD issues:

- **Proper Sub-Widget Types**: `@type: ["prov:Entity", "weier:widget", "pqt:subwidget"]`
- **Appropriate IRIs**: Each widget has proper JSON-LD identifiers
- **Schema Declarations**: Sub-widgets properly declare input/output schemas
- **Dependency Linkages**: Explicit parameter connections from umbrella to sub-widgets
- **Hierarchical IDs**: Widget types follow umbrella pattern (`pq-torus.weierstrass.two-panel`)

This structure ensures proper mathematical workflow orchestration with complete provenance tracking and schema compliance.