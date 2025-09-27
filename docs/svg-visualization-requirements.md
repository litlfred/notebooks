# Widget SVG Visualization & Edge Routing Requirements

## Overview

This document defines the requirements for SVG visualization support in the widget framework, including snap-to-arrowhead functionality, proper edge routing, and consistent widget layout data for both auto-layout and user-defined positioning.

## 1. Arrowhead Snapping Requirements

### 1.1 Border Termination
- **SVG arrows representing edges must terminate exactly at the border of the source and target widget rectangles**, not at the center
- **Arrowhead tips must visually "touch" the widget edge** at the correct logical port (top, bottom, left, or right)
- **Edge splines/paths must be clipped** to start/end at the widget border, preventing overlap or floating away from widgets

### 1.2 Port-Based Connection
- Arrowheads should snap to the **closest appropriate port** on the widget border
- Ports are defined as connection points on the widget's four sides (top, bottom, left, right)
- **Support for custom port positions** within each side for advanced layouts

### 1.3 Non-Rectangular Border Support
- For widgets with **rounded or non-rectangular borders**, arrowheads should snap to the **closest point on the visible border**
- Support for **border radius calculations** to ensure proper visual connection

## 2. Widget Layout Data Requirements

### 2.1 Core Layout Properties
Each widget must define the following layout data regardless of placement method:

```json
{
  "layout": {
    "position": {
      "x": "Top-left X coordinate in layout space",
      "y": "Top-left Y coordinate in layout space"
    },
    "size": {
      "width": "Widget width in layout units",
      "height": "Widget height in layout units"
    },
    "z_index": "Widget stacking order",
    "locked": "Whether position/size is locked"
  }
}
```

### 2.2 SVG-Specific Layout Data
For SVG representation, additional properties are required:

```json
{
  "svg_visualization": {
    "enabled": true,
    "widget_rect": {
      "x": "Top-left X in SVG coordinate space",
      "y": "Top-left Y in SVG coordinate space", 
      "width": "Widget width in SVG units",
      "height": "Widget height in SVG units"
    },
    "connection_ports": {
      "top": [0.2, 0.8],      // X offsets (0-1) for top connections
      "bottom": [0.2, 0.8],   // X offsets (0-1) for bottom connections  
      "left": [0.3, 0.7],     // Y offsets (0-1) for left connections
      "right": [0.3, 0.7]     // Y offsets (0-1) for right connections
    },
    "edge_routing": {
      "snap_to_border": true,
      "border_padding": 2,
      "rounded_corner_support": false
    }
  }
}
```

### 2.3 Unique Widget Identification
- Each widget must have a **unique identifier** (`widget_id`) for edge mapping
- IDs should be **incremental based on widget slug**, not UUID (e.g., `sticky-note-1`, `pq-torus-2`)

## 3. SVG Representation Standards

### 3.1 SVG Element Structure
- **Widgets**: Represented as SVG `<rect>` or `<g>` elements with proper positioning
- **Edges**: Represented as SVG `<path>` elements with arrowhead markers
- **Arrowheads**: Defined as SVG `<marker>` elements for consistent appearance

### 3.2 Coordinate System Consistency
- **Widget layout data must drive SVG positioning**: `x`, `y`, `width`, `height` properties should directly correspond to SVG attributes
- **All coordinates must be consistent** between widget rendering and edge overlay
- **Support for coordinate transformations** between layout space and SVG space

### 3.3 Edge Path Calculation
```javascript
// Edge path must be calculated to terminate at widget border
function calculateEdgePath(sourceWidget, targetWidget, sourcePort, targetPort) {
  const sourcePoint = getPortCoordinates(sourceWidget, sourcePort);
  const targetPoint = getPortCoordinates(targetWidget, targetPort);
  
  // Clip path to widget borders
  const clippedSource = clipToWidgetBorder(sourcePoint, sourceWidget);
  const clippedTarget = clipToWidgetBorder(targetPoint, targetWidget);
  
  return generateSVGPath(clippedSource, clippedTarget);
}
```

## 4. Implementation Compatibility

### 4.1 Auto-Layout Support
- Requirements must work with **automatic layout engines** (Graphviz, dagre, elkjs)
- **Layout algorithm output** should populate widget layout data
- **Edge routing** should respect auto-generated positions

### 4.2 Manual Layout Support  
- Requirements must support **user-defined widget positioning**
- **Drag-and-drop functionality** should update layout data
- **Real-time edge updates** during widget repositioning

### 4.3 Mixed Layout Support
- Some widgets can be **auto-positioned** while others are **manually placed**
- **Edge routing** must handle mixed positioning scenarios
- **Layout constraints** should be respected (e.g., locked widgets)

## 5. CSS Integration Requirements

### 5.1 Widget SVG Styling
- Widgets should have **consistent CSS classes** for SVG styling
- **Status indicators** (idle, running, completed, error) must be visible in SVG
- **Theme support** (dark/light mode) for SVG elements

```css
/* SVG Widget Styling */
.svg-widget {
  stroke: var(--border-color);
  stroke-width: 1;
  fill: var(--widget-bg);
}

.svg-widget.widget-sticky-note {
  fill: #f4e4c1; /* Soft desert sand */
  stroke: #e6d7b8;
}

.svg-widget.running {
  stroke: var(--warning-color);
  stroke-width: 2;
  animation: svg-pulse 1.5s ease-in-out infinite;
}
```

### 5.2 Edge SVG Styling
```css
.svg-edge {
  stroke: var(--text-secondary);
  stroke-width: 2;
  fill: none;
  marker-end: url(#arrowhead);
}

.svg-edge:hover {
  stroke: var(--primary-color);
  stroke-width: 3;
}
```

## 6. Documentation & Standards

### 6.1 Developer Guidelines
- **All future widgets** must follow these SVG visualization standards
- **Edge routing algorithms** must implement snap-to-border functionality
- **Layout data validation** should ensure consistency

### 6.2 Testing Requirements
- **Visual regression tests** for edge termination accuracy
- **Layout consistency tests** between SVG and DOM rendering
- **Performance tests** for complex layouts with many edges

### 6.3 Migration Strategy
- **Existing widgets** should be updated to support SVG visualization
- **Backward compatibility** must be maintained for non-SVG widgets
- **Progressive enhancement** approach for SVG features

## 7. Examples

### 7.1 Basic Widget with SVG Support
```json
{
  "widget_id": "sticky-note-1",
  "widget_type": "sticky-note", 
  "layout": {
    "position": {"x": 100, "y": 200},
    "size": {"width": 280, "height": 200}
  },
  "svg_visualization": {
    "enabled": true,
    "widget_rect": {"x": 100, "y": 200, "width": 280, "height": 200},
    "connection_ports": {
      "top": [0.5],
      "bottom": [0.5], 
      "left": [0.5],
      "right": [0.5]
    }
  }
}
```

### 7.2 Edge Definition with Snapping
```json
{
  "edge_id": "edge-1",
  "source": {
    "widget_id": "pq-torus-1",
    "port": "right",
    "port_index": 0
  },
  "target": {
    "widget_id": "weierstrass-1", 
    "port": "left",
    "port_index": 0
  },
  "svg_path": "M350,300 Q375,300 400,300",
  "routing": {
    "snap_to_border": true,
    "clipped_start": {"x": 350, "y": 300},
    "clipped_end": {"x": 400, "y": 300}
  }
}
```

This specification ensures consistent, professional widget visualization with proper edge routing for both auto-generated and user-defined layouts.