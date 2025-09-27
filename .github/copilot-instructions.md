# Copilot Instructions for Notebooks Repository

## Repository Overview

This repository contains both a **collection of interactive Python notebooks** for mathematical explorations AND a comprehensive **widget framework** for building advanced mathematical computing environments.

### Core Components

1. **📓 Interactive Notebooks**: Self-contained mathematical explorations (Weierstrass functions, chaos games, etc.)
2. **🧩 Widget Framework**: Schema-based system for building drag-and-drop mathematical computing interfaces
3. **🌐 Browser Deployment**: Zero-install web applications via GitHub Pages and Pyodide

### Widget Framework Architecture

The repository includes a complete **production-ready widget framework** with:

- **🎯 Schema-Based Design**: Named JSON schemas with GitHub Pages URLs
- **🔗 JSON-LD & PROV-O Integration**: Full provenance tracking for computational workflows  
- **🧩 Visual Programming**: Drag-and-drop widget blackboard with dependency management
- **📊 Mathematical Focus**: Specialized widgets for computational mathematics
- **🌐 GitHub Pages Ready**: All schemas accessible via HTTPS with proper CORS

#### Widget Types Available

- **Sticky Note**: Markdown content widgets with LaTeX support
- **PQ-Torus**: Prime lattice torus definition widgets (T = ℂ / L where L = ℤp + ℤqi)
- **Weierstrass Functions**: ℘(z) visualization and analysis widgets  
- **Python Code**: Interactive code execution widgets
- **Data Visualization**: Plotting and data generation widgets

#### Framework Structure

```
docs/
├── schema/                        # Widget Schema & JSON-LD Framework
│   ├── weierstrass/              # Weierstrass ℘ function schemas
│   │   ├── input.schema.json    # Input validation schema
│   │   ├── input.jsonld         # Input JSON-LD context
│   │   ├── output.schema.json   # Output validation schema  
│   │   ├── output.jsonld        # Output JSON-LD context
│   │   ├── widget.schema.json   # Widget instance schema
│   │   └── widget.jsonld        # Widget JSON-LD context
│   ├── pq-torus/                # Prime lattice torus schemas
│   ├── sticky-note/             # Markdown note schemas
│   ├── common/                  # Shared schemas (execution results, metadata)
│   ├── ontology/                # JSON-LD contexts and vocabularies
│   └── example-notebook-graph.jsonld  # PROV-O workflow example
├── weierstrass-playground/       # Interactive blackboard system
│   ├── board.html               # Main widget blackboard interface
│   ├── widgets/                 # Python widget implementations
│   └── widget-schemas.json      # Widget registry and definitions
├── widget-framework.md          # Complete framework documentation
├── json-schema-specification.md # Schema specifications and guidelines
├── architecture-examples.md     # Implementation examples and patterns
└── migration-guide.md           # Migration strategy for existing widgets
```

## 🚨 URGENT: Branch Naming Compliance Required

**IMMEDIATE ACTION NEEDED**: Recent PRs (#2, #3, #7) ALL violated branch naming requirements by using `copilot/fix-<UUID>` patterns instead of the required `feature-descriptive-name` format.

**GOING FORWARD**: Every branch MUST use descriptive names like:
- `feature-weierstrass-board-system` ✅  
- `feature-pyodide-browser-deployment` ✅
- `feature-trajectory-visualization-fixes` ✅

**NOT allowed**:
- `copilot/fix-79449fca-2fc8-42d9-b210-2bf7c4d836d0` ❌
- `copilot/fix-anything` ❌
- Generic UUID-based names ❌

## Branch Naming Convention

**🚨 CRITICAL REQUIREMENT**: All Copilot branches MUST follow the pattern:

```
feature-descriptive-name
```

**⚠️ RECENT VIOLATIONS**: All recent PRs (#2, #3, #7) violated this requirement by using `copilot/fix-<UUID>` patterns. This MUST be corrected going forward.

### ✅ Valid Examples:
- `feature-weierstrass-playground`
- `feature-mandelbrot-explorer` 
- `feature-fourier-analysis`
- `feature-neural-network-viz`
- `feature-prime-spirals`
- `feature-board-system-widgets`
- `feature-pyodide-deployment`
- `feature-trajectory-visualization`

### ❌ STRICTLY FORBIDDEN Branch Names:
- `copilot/fix-xyz-123-456` ← **RECENTLY USED INCORRECTLY**
- `copilot/fix-<any-uuid>` ← **RECENTLY USED INCORRECTLY**  
- `main`
- `fix-bug`
- `update-notebook`
- Any non-descriptive generic names

### 🎯 Branch Name Requirements:
1. **MUST start with `feature-`**
2. **MUST describe the actual functionality being added**
3. **MUST use kebab-case (dashes, not underscores or camelCase)**
4. **MUST be readable and self-explanatory**
5. **MUST NOT use UUIDs, random IDs, or generic patterns**

## Code Architecture Guidelines

### 1. Separation of Concerns
- **Notebooks** should contain ONLY minimal imports and calls to UI modules
- **Mathematical/computational logic** should be extracted to `{notebook_name}_lib.py` modules  
- **UI code** should be extracted to `{notebook_name}_ui.py` modules
- Create three separate files for each major notebook

### 2. File Structure
```python
# Example structure for a notebook called "chaos_game":

# chaos_game.ipynb - MINIMAL notebook (3-4 cells max)
"""
Ultra-minimal notebook with just:
- Import preamble, lib, and ui modules
- Call setup from preamble
- Display UI
- Display output widget
"""

# chaos_game_preamble.py - Documentation and setup
"""
Contains:
- Comprehensive documentation and mathematical background
- Module docstring with detailed explanations  
- setup_environment() function for configuration
- get_help() function for user guidance
- All verbose explanations moved from notebook
"""

# chaos_game_lib.py - Mathematical/computational logic
"""
All mathematical functions and algorithms:
- Core computation functions
- Integration/simulation methods
- Data processing utilities
- Visualization helpers (backgrounds, contours, etc.)
"""

# chaos_game_ui.py - UI components and layout
"""
All UI widgets and interaction logic:
- Widget creation and configuration
- Layout and styling
- Event handlers that call lib functions
- Help button linking to preamble.get_help()
- Parameter validation
- File I/O operations
"""
```

### 3. Four-File Architecture Pattern
```python
# notebook_name.ipynb (ULTRA-MINIMAL)
from notebook_name_preamble import setup_environment
from notebook_name_lib import *
from notebook_name_ui import create_ui

setup_environment()

# notebook_name_preamble.py  
def setup_environment(): ...
def get_help(): ...
# Comprehensive documentation in module docstring

# notebook_name_lib.py
def mathematical_function(): ...
def visualization_function(): ...

# notebook_name_ui.py  
class UI:
    def show_help(self): 
        from notebook_name_preamble import get_help
        get_help()
ui.display()
display(ui.get_output_widget())

# notebook_name_lib.py  
def core_mathematical_function():
    """Core computation logic"""
    pass

def visualization_helper():
    """Visualization utilities"""
    pass

# notebook_name_ui.py
class NotebookUI:
    def __init__(self):
        self._create_widgets()
        self._setup_layout()
    
    def display(self):
        display(self.ui)
        
def create_ui():
    return NotebookUI()
```

## Working with Widget Framework

### Schema Development Guidelines

When creating new widgets, follow the directory-based schema structure:

#### 1. Widget Directory Structure
```bash
# Create new widget directory
mkdir docs/schema/{widget-name}/

# Required files (6 total):
docs/schema/{widget-name}/
├── input.schema.json    # Input validation (JSON Schema)
├── input.jsonld         # Input context (JSON-LD)  
├── output.schema.json   # Output validation (JSON Schema)
├── output.jsonld        # Output context (JSON-LD)
├── widget.schema.json   # Widget instance schema
└── widget.jsonld        # Widget instance context
```

#### 2. Schema URL Pattern
All schemas must use GitHub Pages URLs:
```json
{
  "$id": "https://litlfred.github.io/notebooks/schema/{widget}/input.schema.json"
}
```

#### 3. JSON-LD Integration
Every JSON-LD file must:
- Include PROV-O context: `"https://www.w3.org/ns/prov-o.jsonld"`
- Include widget context: `"https://litlfred.github.io/notebooks/schema/ontology/context.jsonld"`
- Reference corresponding schema: `"dct:conformsTo": "./input.schema.json"`
- Use proper type array: `"@type": ["prov:Entity", "{prefix}:input"]`

#### 4. Type Naming Convention
Use flat, human-readable prefixes:
- **Weierstrass**: `weier:input`, `weier:output`, `weier:widget`
- **PQ-Torus**: `pqt:input`, `pqt:output`, `pqt:widget`
- **New Widget**: `{abbrev}:input`, `{abbrev}:output`, `{abbrev}:widget`

#### 5. Widget Implementation
Create Python implementation in `docs/weierstrass-playground/widgets/{widget_name}.py`:
```python
from widgets.widget_executor import WidgetExecutor

class NewWidgetExecutor(WidgetExecutor):
    def _execute_impl(self, validated_input):
        # Widget logic here
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            # ... widget-specific output
        }
```

#### 6. Schema Registration
Add widget to `docs/weierstrass-playground/widget-schemas.json`:
```json
{
  "new-widget": {
    "id": "new-widget",
    "name": "New Widget",
    "input_schemas": [
      "https://litlfred.github.io/notebooks/schema/new-widget/input.schema.json"
    ],
    "output_schemas": [
      "https://litlfred.github.io/notebooks/schema/new-widget/output.schema.json"  
    ],
    "python_script": "widgets/new_widget.py"
  }
}
```

### Widget Dependency Patterns

The framework supports complex mathematical workflows:

#### Example: PQ-Torus → Weierstrass Pipeline
1. **PQ-Torus Widget**: Validates prime parameters (p, q)
2. **Output**: Prime lattice parameters with validation
3. **Weierstrass Widgets**: Receive parameters for ℘-function analysis
4. **Result**: Complete mathematical visualization pipeline

#### Dependency Configuration
```json
{
  "dependencies": [
    {
      "source_widget": "urn:uuid:pq-torus-widget-1",
      "source_path": "p",
      "target_path": "p"
    },
    {
      "source_widget": "urn:uuid:pq-torus-widget-1", 
      "source_path": "q",
      "target_path": "q"
    }
  ]
}
```

### PROV-O Notebook Graphs

The framework generates complete provenance graphs:
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld",
    "https://litlfred.github.io/notebooks/schema/ontology/context.jsonld"
  ],
  "@graph": [
    {
      "@id": "urn:uuid:widget-1",
      "@type": ["prov:Entity", "pqt:widget"],
      "prov:generatedAtTime": "2024-09-27T09:00:00Z"
    },
    {
      "@id": "urn:uuid:activity-1", 
      "@type": "prov:Activity",
      "prov:used": "urn:uuid:widget-1"
    }
  ]
}
```

## Quality Standards

### Documentation
- Each notebook must have a clear title and description
- Include mathematical background where relevant
- Provide usage instructions
- Add tips for interesting parameter values

### User Experience
- Controls should be intuitive and well-organized
- Include clear usage instructions at the top
- Provide meaningful error messages
- Add progress indicators for long computations

### Code Quality
- Extract complex logic to separate modules
- Use meaningful function and variable names
- Include docstrings for all functions
- Handle edge cases gracefully

## File Organization

```
repository-root/
├── notebook_name.ipynb          # MINIMAL notebook (imports + UI display only)
├── notebook_name_lib.py         # Mathematical/computational logic
├── notebook_name_ui.py          # UI widgets and layout code
├── test_notebook_name.py        # Optional: tests for library functions
├── requirements.txt             # Dependencies
└── README.md                    # Repository overview
```

## Dependencies

### Standard Stack
- `numpy` - Numerical computations
- `matplotlib` - Plotting and visualization  
- `ipywidgets` - Interactive controls
- `jupyter` - Notebook environment

### Additional Libraries (as needed)
- `scipy` - Scientific computing
- `sympy` - Symbolic mathematics
- `plotly` - Interactive plots
- `PIL/Pillow` - Image processing

## Commit Guidelines

### Commit Messages
- Use descriptive commit messages
- Reference issue numbers when applicable
- Example: `Add three-panel mode for Weierstrass playground`

### Progress Reporting
- Use `report_progress` tool frequently during development
- Update PR descriptions with checklists showing progress
- Commit working increments rather than large monolithic changes

### Branch Name Enforcement
- **Before creating any PR**: Verify your branch follows `feature-descriptive-name`
- **Self-check**: Would a developer understand what this branch contains from the name alone?
- **If using auto-generated branch names**: IMMEDIATELY rename to a descriptive name
- **Review requirement**: All PRs with non-compliant branch names MUST be declined

## Testing

### Manual Testing
- Test all interactive controls
- Verify mathematical correctness with known cases
- Check edge cases and error handling
- Ensure notebook runs from top to bottom without errors

### Automated Testing (Optional)
- Create test files for library functions
- Validate mathematical computations
- Test visualization pipeline

## Example Workflow

1. **Create branch**: `feature-chaos-game`
2. **Plan implementation**:
   - Main notebook: `chaos_game.ipynb`
   - Library: `chaos_game_lib.py`
   - Functions: `iterate_chaos_game()`, `plot_attractor()`, etc.
3. **Develop iteratively**:
   - Implement core math in library
   - Create notebook UI
   - Test and refine
4. **Document and polish**:
   - Add clear instructions
   - Include interesting examples
   - Optimize performance

## Repository Goals

### Primary Objectives
- **Educational**: Help others learn mathematical concepts through interaction
- **Exploratory**: Enable experimentation with parameters and visualizations
- **Reusable**: Create modular code that can be adapted for other projects

### Secondary Objectives  
- **Performance**: Efficient computation for real-time interaction
- **Aesthetics**: Beautiful, publication-quality visualizations
- **Robustness**: Handle edge cases and provide helpful error messages

## Review Criteria

Before submitting:
- [ ] **🚨 CRITICAL**: Branch name follows `feature-descriptive-name` pattern (NOT `copilot/fix-*`)
- [ ] Branch name clearly describes the feature/functionality being added
- [ ] Mathematical logic extracted to separate module
- [ ] Notebook runs completely from top to bottom
- [ ] UI controls are intuitive and well-organized
- [ ] Documentation is clear and helpful
- [ ] Error handling is robust
- [ ] Code is well-structured and documented