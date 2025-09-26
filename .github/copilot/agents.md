# Copilot Agents Configuration for Mathematical Notebooks

## Agent Specializations

### Mathematical Development Agent
- **Role**: Implement mathematical functions and algorithms
- **Focus Areas**:
  - Complex analysis functions (Weierstrass ℘, derivatives)
  - Numerical integration and trajectory computation
  - Grid-based field calculations
  - Performance optimization for real-time interaction
- **Key Files**: `src/weierstrass_playground/core.py`, `src/weierstrass_playground/integration.py`
- **Testing Requirements**: Mathematical correctness validation with known values

### Visualization Agent  
- **Role**: Create mathematical visualizations and interactive plots
- **Focus Areas**:
  - Matplotlib-based plotting with Pyodide compatibility
  - Color mapping and background generation
  - Contour plotting and vector field overlays
  - Interactive parameter controls and widgets
- **Key Files**: `src/weierstrass_playground/visualization.py`, UI modules
- **Testing Requirements**: Visual output validation and browser compatibility

### Web Development Agent
- **Role**: Browser integration and GitHub Pages deployment
- **Focus Areas**:
  - Pyodide integration for browser-based Python execution
  - Jekyll static site generation
  - Responsive web design for mathematical interfaces
  - JavaScript integration for interactive controls
- **Key Files**: `docs/` directory, Jekyll templates, JavaScript files
- **Testing Requirements**: Cross-browser compatibility and mobile responsiveness

### Documentation Agent
- **Role**: Technical documentation and mathematical explanations
- **Focus Areas**:
  - Mathematical background and theory explanations
  - Code documentation with proper docstrings
  - Usage instructions and tutorials
  - API documentation for reusable components
- **Key Files**: README files, docstrings, `*_preamble.py` files
- **Testing Requirements**: Documentation completeness and accuracy

## Agent Coordination Guidelines

### Branch Naming Protocol
- All agents MUST use `feature-descriptive-name` format
- Examples: `feature-elliptic-function-optimization`, `feature-mobile-responsive-ui`
- FORBIDDEN: `copilot/fix-*`, generic or UUID-based names

### Code Organization Protocol
- Follow 4-file architecture: notebook, preamble, lib, ui
- Mathematical logic in `*_lib.py`, UI components in `*_ui.py`
- Browser adaptations in dedicated modules
- Comprehensive test coverage for mathematical functions

### Quality Assurance Protocol
- Mathematical correctness verified with analytical solutions
- Browser compatibility tested with Pyodide
- Performance benchmarks for interactive use
- Visual output validation for plots and visualizations

### Deployment Protocol
- Local development and testing first
- Browser adaptation with Pyodide compatibility
- Static site generation for GitHub Pages
- Automated quality gates via GitHub Actions

## Domain-Specific Guidelines

### Mathematical Accuracy
- Use appropriate numerical precision for elliptic functions
- Handle singularities and poles properly
- Implement proper fundamental domain wrapping
- Validate results against known mathematical properties

### Performance Considerations
- Optimize grid computations for real-time interaction
- Use efficient algorithms for lattice sum truncation
- Memory management for browser environments
- Progressive rendering for complex visualizations

### User Experience Standards
- Intuitive parameter controls with meaningful ranges
- Clear visual feedback during computations
- Responsive design for desktop and mobile
- Educational context with mathematical explanations