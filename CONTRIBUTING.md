# Contributing to Notebooks Repository

Welcome! This repository contains interactive mathematical notebooks and a comprehensive widget framework for building advanced mathematical computing environments.

## Quick Start

1. Fork the repository
2. Create a descriptive branch following our naming conventions (see below)
3. Make your changes following our code standards
4. Test your changes
5. Submit a pull request

## Branch Naming Conventions

**All branches MUST follow this pattern:**

```
feature-descriptive-name
```

### ✅ Valid Examples:
- `feature-weierstrass-playground`
- `feature-mandelbrot-explorer` 
- `feature-fourier-analysis`
- `feature-neural-network-viz`
- `feature-prime-spirals`
- `feature-board-system-widgets`
- `feature-pyodide-deployment`
- `feature-trajectory-visualization`

### ❌ Invalid Branch Names:
- `copilot/fix-xyz-123-456`
- `copilot/fix-<any-uuid>`  
- `main`
- `fix-bug`
- `update-notebook`
- Generic or non-descriptive names

### Requirements:
1. **MUST start with `feature-`**
2. **MUST describe the actual functionality being added**
3. **MUST use kebab-case (dashes, not underscores or camelCase)**
4. **MUST be readable and self-explanatory**
5. **MUST NOT use UUIDs, random IDs, or generic patterns**

## Development Workflow

### Repository Structure

This repository contains two main components:

1. **📓 Interactive Notebooks**: Self-contained mathematical explorations
2. **🧩 Widget Framework**: Schema-based system for drag-and-drop mathematical computing

### Four-File Architecture Pattern

For notebooks, follow this pattern:
```
repository-root/
├── notebook_name.ipynb          # MINIMAL notebook (imports + UI display only)
├── notebook_name_lib.py         # Mathematical/computational logic
├── notebook_name_ui.py          # UI widgets and layout code
├── test_notebook_name.py        # Optional: tests for library functions
```

### Code Quality Standards

#### Documentation
- Each notebook must have a clear title and description
- Include mathematical background where relevant
- Provide usage instructions
- Add tips for interesting parameter values

#### Code Quality
- Extract complex logic to separate modules
- Use meaningful function and variable names
- Include docstrings for all functions
- Handle edge cases gracefully

#### User Experience
- Controls should be intuitive and well-organized
- Include clear usage instructions at the top
- Provide meaningful error messages
- Add progress indicators for long computations

## Widget Framework Development

For detailed widget framework guidelines, see [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

### Adding New Widgets

1. Create widget directory: `docs/schema/{widget-name}/`
2. Create 6 required files (input/output/widget × schema.json/jsonld)
3. Update ontology context with widget prefix
4. Add widget to registry: `docs/weierstrass-playground/widget-schemas.json`
5. Implement Python backend: `docs/weierstrass-playground/widgets/{widget}.py`
6. Test all URLs resolve via GitHub Pages

## Testing

Run the test suite before submitting changes:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_weierstrass.py
```

## Dependencies

- Python 3.8+
- NumPy >= 1.20.0
- Matplotlib >= 3.5.0
- IPyWidgets >= 7.6.0

For widget framework development, see `docs/schema/README.md` for additional requirements.

## Getting Help

- **General questions**: Open an issue
- **Widget framework**: See `docs/widget-overview.md`
- **Development setup**: See `docs/DEVELOPMENT.md`
- **AI agent guidelines**: See [`.github/copilot-instructions.md`](.github/copilot-instructions.md)

## License

This project is licensed under the terms specified in the LICENSE file.