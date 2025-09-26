# Widget Framework Documentation

## Overview

The Widget Framework is a modular, JSON schema-based system for creating interactive computational and visualization components that can be embedded in markdown-like content and arranged on an interactive blackboard workspace. This framework enables users to build complex mathematical and data analysis workflows through a visual, node-based interface.

## Core Concepts

### Widget Definition
A widget is a self-contained computational or visualization component defined by:
- **JSON Schema**: Defines input/output data structure and validation
- **Python Script**: Implements the core computational logic
- **Metadata**: Describes the widget's purpose, category, and UI properties
- **Instance Configuration**: Runtime parameters and connections

### Blackboard/Workspace
An interactive canvas where widget instances can be:
- Placed and arranged visually
- Connected to form data processing pipelines
- Executed individually or as part of a dependency graph
- Configured through dynamically generated UIs

## JSON Schema Structure

### Named Schema System with GitHub Pages URLs

The framework uses **named JSON schemas** with proper URLs designed for GitHub Pages deployment:

**Base URL**: `https://litlfred.github.io/notebooks/schemas/`

**Core Schemas**:
- `common.json` - Reusable definitions (metadata, execution results, data structures)
- `widget-definition.json` - Widget configuration structure
- `sticky-note.json` - Sticky note widget schemas
- `python-code.json` - Python execution widget schemas  
- `weierstrass.json` - Mathematical function widget schemas
- `data-visualization.json` - Data plotting widget schemas

### Schema Reusability and Composition

Schemas can be **reused and composed** using:
- **External references**: `"$ref": "https://litlfred.github.io/notebooks/schemas/common.json#/definitions/metadata"`
- **Schema composition**: `"allOf": [{"$ref": "..."}]`
- **Multiple schema arrays**: With precedence order

### Widget Schema Definition with Multiple Schemas

```json
{
  "$schema": "https://litlfred.github.io/notebooks/schemas/widget-definition.json",
  "widget-schemas": {
    "widget-id": {
      "id": "widget-id",
      "name": "Widget Name",
      "description": "Widget description",
      "category": "content|computation|visualization|data|utility",
      "icon": "📝",
      "input_schemas": [
        "https://litlfred.github.io/notebooks/schemas/common.json#/definitions/markdown_content",
        "https://litlfred.github.io/notebooks/schemas/common.json#/definitions/ui_configuration",
        {
          "type": "object",
          "properties": {
            "custom_param": {"type": "string", "default": "value"}
          }
        }
      ],
      "output_schemas": [
        "https://litlfred.github.io/notebooks/schemas/common.json#/definitions/execution_result"
      ],
      "python_script": "widgets/widget_script.py",
      "version": "1.0.0",
      "author": "Author Name",
      "tags": ["tag1", "tag2"]
    }
  }
}
```

### Schema Precedence Order

**Multiple schemas with precedence**: First schema in array takes precedence for conflicting properties.

```json
{
  "input_schemas": [
    "https://litlfred.github.io/notebooks/schemas/weierstrass.json#/definitions/weierstrass_input",
    {
      "type": "object", 
      "properties": {
        "contours": {"type": "integer", "minimum": 0, "maximum": 30, "default": 10}
      }
    }
  ]
}
```

**Result**: Weierstrass input schema merged with additional `contours` parameter.

### Input Schema Properties
- `type`: JSON Schema data type
- `description`: Human-readable parameter description
- `default`: Default value when not specified
- `minimum`/`maximum`: Numeric constraints
- `enum`: Enumerated valid values
- `required`: Array of required parameter names

### Output Schema Properties
- Defines expected output structure
- Enables type validation and UI generation
- Supports nested objects and arrays
- Includes metadata fields for execution context

## Widget Execution Framework

### WidgetExecutor Base Class

```python
class WidgetExecutor:
    """Base class for executing schema-based widgets"""
    
    def __init__(self, widget_schema: Dict[str, Any]):
        self.schema = widget_schema
        self.id = widget_schema['id']
        self.name = widget_schema['name']
        self.input_schema = widget_schema['input_schema']
        self.output_schema = widget_schema['output_schema']
        
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data against schema and apply defaults"""
        # Implementation handles validation and default application
        
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute widget with validated input"""
        validated_input = self.validate_input(input_data)
        return self._execute_impl(validated_input)
        
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_impl")
```

### Widget Types

#### 1. Markdown Widgets
- Rich text content with LaTeX math support
- Variable substitution from connected inputs
- Real-time rendering updates

#### 2. Python Code Widgets  
- Execute arbitrary Python code
- Capture stdout/stderr and execution results
- Access to scientific computing libraries
- Variable passing between widgets

#### 3. Visualization Widgets
- Mathematical plotting and analysis
- Interactive charts and graphs
- Image output with download capabilities
- Support for various plot types

#### 4. Data Widgets
- Data generation and transformation
- Import/export capabilities
- Statistical analysis functions

## Blackboard/Workspace Interface

### MathematicalBoard Class

```javascript
class MathematicalBoard {
    constructor() {
        this.widgets = new Map();           // Widget instances
        this.connections = new Map();       // Data flow connections
        this.widgetGraph = new WidgetGraph(); // Dependency management
        this.selectedWidget = null;
        // ... other properties
    }
    
    // Core widget management
    createWidget(type, x, y, customConfig = {})
    deleteWidget(widgetId)
    executeWidget(widgetId)
    
    // Connection management  
    connectWidgets(sourceId, targetId, outputPath, inputPath)
    updateWidgetInputFromConnection(targetWidget, inputPath, sourceOutput)
    
    // UI generation
    generateSchemaForm(inputSchema, currentConfig)
    renderWidgetContent(widget)
    renderOutput(output, outputSchema)
}
```

### Widget Instance Structure

```javascript
const widget = {
    id: "widget-1",                    // Unique instance ID
    type: "widget-type",              // Schema reference
    x: 100, y: 200,                   // Position
    width: 350, height: 250,          // Size
    title: "Widget Title",            // Display name
    config: { /* input parameters */ }, // Current configuration
    schema: { /* JSON schema */ },     // Widget definition
    connections: {                     // Data flow connections
        inputs: new Map(),
        outputs: new Map()
    },
    lastOutput: null,                 // Cached execution result
    status: 'idle'                    // 'idle'|'running'|'completed'|'error'
}
```

## Widget Lifecycle

### 1. Creation
- Widget selected from library/palette
- Instance created with default configuration from schema
- Placed on blackboard at specified coordinates
- Assigned unique incremental ID

### 2. Configuration
- Dynamic UI generated from input schema
- User edits parameters through form interface
- Real-time validation against schema constraints
- Configuration saved to widget instance

### 3. Execution
- Input validation against schema
- Dependency resolution if connected to other widgets
- Python script execution with validated inputs
- Output capture and validation
- UI update with results

### 4. Connection
- Visual connection interface for linking widgets
- Output-to-input data flow definition
- Dependency graph management
- Automatic re-execution on input changes

## Dependency Management

### WidgetGraph Class
Manages execution order and data flow:

```javascript
class WidgetGraph {
    constructor() {
        this.widgets = new Map();
        this.connections = new Map();
    }
    
    addWidget(id, widget)
    removeWidget(id)  
    connectWidgets(sourceId, targetId, outputPath, inputPath)
    
    // Execution with dependency resolution
    executeWidget(widgetId, force_recompute = false)
}
```

### Dependency Resolution
- Widgets execute in dependency order
- Circular dependencies detected and prevented
- Caching prevents unnecessary re-computation
- Manual force-recompute available

### Connection System
- Visual arrows indicate data flow
- Flexible path mapping (e.g., `output.data.x` → `input.x_values`)
- Support for complex data transformations
- ETL scripting for data format conversion

## UI Integration and Embedding

### Markdown Integration
Widgets can be embedded in markdown content using custom tags:

```markdown
<widget type="data-plot" config='{"data": {"x": [1,2,3], "y": [1,4,9]}}' />
```

### Dynamic UI Generation
- Forms automatically generated from input schemas
- Support for all JSON Schema types and constraints
- Real-time validation feedback
- Responsive design for mobile/desktop

### Widget Library/Palette
- Categorized widget browser
- Drag-and-drop widget placement
- Search and filtering capabilities
- Custom widget icons and descriptions

## Common Widget Interface

### Standard Methods
Every widget supports these operations:

#### User Interactions
- **Run**: Execute widget with current configuration
- **Stop**: Halt running execution
- **Edit Config**: Open configuration dialog
- **Resize**: Adjust widget dimensions
- **Delete**: Remove widget and connections

#### System Operations
- **Input Validation**: Schema-based parameter checking
- **Output Generation**: Structured result production
- **Error Handling**: Graceful failure with user feedback
- **State Management**: Configuration persistence

### Standard Properties
- **Instance ID**: Incremental counter (not UUID)
- **Metadata**: Slug, timestamps, execution history
- **Visualization Size**: Captured as input metadata
- **Theme Support**: Dark/light mode coordination
- **Accessibility**: Keyboard navigation and screen reader support

## Sticky Note Widget (Simplest Example)

The simplest widget with empty input/output schemas beyond metadata:

```json
{
  "sticky-note": {
    "id": "sticky-note",
    "name": "Sticky Note",
    "description": "Simple markdown note widget",
    "category": "content",
    "icon": "📝",
    "input_schema": {
      "type": "object",
      "properties": {
        "content": {
          "type": "string",
          "description": "Markdown content",
          "default": "# New Note\n\nClick edit to add content..."
        },
        "show_note": {
          "type": "boolean", 
          "description": "Show/hide note",
          "default": true
        }
      },
      "required": ["content"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "rendered_html": {
          "type": "string",
          "description": "Rendered HTML output"
        }
      }
    },
    "python_script": "widgets/sticky_note.py"
  }
}
```

## Advanced Features

### Attached Notes System
Each widget instance includes an editable markdown note:
- **Default State**: Visible by default
- **Toggle Visibility**: Can be shown/hidden
- **Dynamic Content**: Access to widget input/output variables
- **Live Updates**: Refreshes when widget executes
- **Error Indication**: Red underline for failed widget references
- **LaTeX Support**: Mathematical notation rendering
- **Notebook Integration**: Metadata, timestamps, configuration variables

### Event System
Widgets fire events for system integration:
- **Input Changed**: When configuration updates
- **Output Generated**: When execution completes
- **Status Changed**: When execution state changes
- **Connection Modified**: When dependencies change

### Internationalization Support
- **Schema Descriptions**: Multi-language support
- **UI Labels**: Localized interface elements
- **Error Messages**: Translated feedback
- **Number Formats**: Locale-aware formatting

### Accessibility Features
- **Keyboard Navigation**: Full keyboard control
- **Screen Reader Support**: Descriptive text and ARIA labels
- **High Contrast**: Configurable color schemes
- **Focus Management**: Clear visual indicators
- **Alternative Text**: Image and visualization descriptions

### Binary Data Support
- **Buffer Handling**: Efficient binary data management
- **MIME Type Support**: Proper content type identification
- **Download Capabilities**: Export visualizations and data
- **Streaming Support**: Handle large datasets efficiently

## Architecture Design Options

### 1. Widget Registration System
**Option A: Schema File Registration**
- Widgets defined in centralized JSON schema file
- Static loading at application startup
- Simple to implement and maintain

**Option B: Dynamic Plugin System**
- Widgets as separate modules/packages
- Runtime discovery and loading
- More flexible but complex implementation

**Recommendation**: Start with Option A for simplicity, migrate to Option B as framework matures.

### 2. Execution Environment
**Option A: Server-side Python Execution**
- Secure sandboxed execution
- Access to full Python ecosystem
- Requires backend infrastructure

**Option B: Client-side JavaScript Execution**  
- Immediate execution without network calls
- Limited computational capabilities
- Better for simple widgets

**Option C: Hybrid Approach**
- Simple widgets run client-side
- Complex computations run server-side
- Best performance and capability balance

**Recommendation**: Option C for optimal user experience.

### 3. State Management
**Option A: Local Browser Storage**
- Persists between sessions
- Limited storage capacity
- No server requirements

**Option B: Server-side Persistence**
- Unlimited storage
- Multi-device synchronization
- Requires user authentication

**Option C: File-based Export/Import**
- User-controlled data
- Portable between systems
- Manual synchronization

**Recommendation**: Combine all three options for maximum flexibility.

## Migration Plan for Existing Widgets

### Phase 1: Schema Extraction
1. **Analyze Current Widgets**: Document existing parameter structures
2. **Generate JSON Schemas**: Convert to formal schema definitions
3. **Validate Schemas**: Ensure all parameters properly defined
4. **Create Migration Scripts**: Automate schema conversion

### Phase 2: Execution Framework Integration
1. **Wrap Existing Code**: Create WidgetExecutor subclasses
2. **Standardize Interfaces**: Ensure consistent input/output handling
3. **Add Validation**: Implement schema-based parameter checking
4. **Test Compatibility**: Verify existing functionality preserved

### Phase 3: UI Enhancement
1. **Generate Configuration Forms**: Replace manual UI with schema-driven forms
2. **Update Visualization Output**: Standardize result rendering
3. **Add Connection Support**: Enable widget-to-widget data flow
4. **Improve Error Handling**: Provide better user feedback

### Phase 4: Advanced Features
1. **Add Attached Notes**: Implement per-widget documentation
2. **Enable Event System**: Support for widget communication
3. **Accessibility Improvements**: Add keyboard and screen reader support
4. **Performance Optimization**: Implement caching and lazy loading

### Backward Compatibility
- **Legacy Support**: Maintain existing widget interfaces during transition
- **Gradual Migration**: Widgets can be updated incrementally
- **Configuration Preservation**: Existing widget configurations preserved
- **Deprecation Warnings**: Clear migration path communication

## Framework Benefits

### For Widget Authors
- **Simplified Development**: Focus on mathematical/visualization logic
- **Automatic UI Generation**: No manual form creation required
- **Built-in Validation**: Schema-based parameter checking
- **Standard Integration**: Consistent framework interfaces
- **Documentation Support**: Self-documenting schema structure

### For Users
- **Intuitive Interface**: Visual, drag-and-drop workflow creation
- **Type Safety**: Schema validation prevents errors
- **Live Updates**: Real-time result visualization
- **Flexible Connections**: Complex data flow pipelines
- **Persistent State**: Save and restore workspace configurations

### For System Integrators
- **Modular Architecture**: Clean component separation
- **Extensible Design**: Easy to add new widget types
- **Standard APIs**: Consistent integration patterns
- **Framework Agnostic**: Can be embedded in various systems
- **Open Standards**: JSON Schema-based definitions

## Implementation Guidelines

### Widget Development Best Practices
1. **Clear Schema Definition**: Comprehensive parameter documentation
2. **Robust Error Handling**: Graceful failure modes
3. **Performance Considerations**: Efficient algorithms and caching
4. **User Experience**: Intuitive parameter naming and organization
5. **Testing**: Unit tests for execution logic

### Framework Extension Points
1. **Custom Widget Types**: Extend WidgetExecutor base class
2. **UI Components**: Custom form field types
3. **Connection Handlers**: Specialized data transformation logic
4. **Export Formats**: Additional output formats
5. **Theme Support**: Custom styling and visualization themes

This framework provides a solid foundation for creating interactive computational workflows while maintaining clean interfaces and modular architecture. The schema-based approach ensures consistency while allowing for extensive customization and extension.