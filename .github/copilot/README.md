# Copilot Configuration for Mathematical Notebooks Repository

This directory contains configuration and guidance for GitHub Copilot agents working on the mathematical notebooks repository.

## Configuration Files

### `config.yml`
Main configuration with environment settings, dependencies, and quality standards.

### `knowledge.md` 
Comprehensive knowledge base covering:
- Repository architecture and structure
- Mathematical domain knowledge (Weierstrass ℘ functions)
- Development guidelines and patterns
- Common issues and solutions

### `agents.md`
Specialized agent configurations for:
- Mathematical Development Agent
- Visualization Agent  
- Web Development Agent
- Documentation Agent

### `templates/`
Code templates and examples:
- `mathematical_lib_template.py` - Template for mathematical modules
- `notebook_template.md` - Complete notebook creation guide

## Key Guidelines for Agents

### 🚨 Critical Requirements
1. **Branch Naming**: MUST use `feature-descriptive-name` format
2. **Architecture**: Follow 4-file pattern (notebook, preamble, lib, ui)
3. **Testing**: Mathematical correctness + browser compatibility
4. **Documentation**: Mathematical background + clear usage instructions

### Mathematical Focus
- **Primary**: Weierstrass ℘ elliptic function implementation and visualization
- **Secondary**: Complex analysis, numerical integration, interactive mathematics
- **Deployment**: Browser-based execution via Pyodide + GitHub Pages

### Quality Standards
- Mathematical accuracy validated against analytical solutions
- Real-time performance for interactive use
- Responsive design for desktop and mobile
- Comprehensive error handling and edge case coverage

## Development Workflow

1. **Feature Development**: Create descriptively-named branch
2. **Mathematical Implementation**: Follow templates and test thoroughly  
3. **Browser Adaptation**: Ensure Pyodide compatibility
4. **Quality Validation**: Run automated tests and visual verification
5. **Documentation**: Add mathematical context and usage instructions
6. **Deployment**: GitHub Pages integration with Jekyll

## Resources

- **Live Site**: https://litlfred.github.io/notebooks/
- **Main Feature**: Weierstrass ℘ Playground with trajectory integration
- **Testing**: Run `python test_weierstrass.py` for mathematical validation

This configuration enables Copilot agents to work effectively on mathematical notebook development with proper context, templates, and quality standards.