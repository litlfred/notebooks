---
layout: default
title: Mathematical Notebooks
description: Interactive browser-based mathematical playgrounds powered by Python and WebAssembly
---

# 🧮 Mathematical Notebooks

Welcome to an interactive collection of **mathematical notebooks** that run entirely in your browser. These playgrounds leverage the power of Python, NumPy, and Matplotlib through WebAssembly, requiring zero installation.

## Available Notebooks

### [℘ Weierstrass Mathematical Workspace](weierstrass-playground/)

**Revolutionary Miro-like mathematical workspace** for exploring the Weierstrass ℘ function with drag-and-drop widgets, schema-based configurations, and computational pipelines.

**New in v2.0:** 🔐 **GitHub Integration**
- **Personal Access Token Authentication** - Secure login with your GitHub PAT
- **Direct Repository Saves** - Save notebooks directly to the `notebooks/` directory
- **Collaborative Editing** - Edit and update shared notebooks with proper permissions
- **Version Control** - Automatic commit messages and change tracking
- **Create New Notebooks** - Generate empty notebooks from the interface

**Features:**
- **🧩 Widget-Based Interface**: Drag mathematical components onto a collaborative board
- **∞ Specialized Visualizations**: 7+ different Weierstrass ℘ visualization types
- **🔗 Widget Connections**: Connect outputs to inputs for computational pipelines  
- **📝 Rich Content**: Markdown with LaTeX, Python code execution, data analysis
- **💾 Session Management**: Save/load complete workspace configurations
- **📱 Responsive Design**: Desktop and mobile layouts with touch support
- **🌙 Dark Mode Default**: Professional dark theme with light mode option

**Widget Library:**
- **∞ Two-Panel Plot**: ℘(z) and ℘′(z) with color mapping
- **∞ Three-Panel Analysis**: Grayscale ℘(z), Re(℘′(z)), Im(℘′(z))  
- **∞ Five-Panel Complete**: Full derivative and magnitude analysis
- **🎯 Trajectory Integration**: Particle dynamics in ℘ potential field
- **🔗 Lattice Analysis**: Systematic lattice point trajectories
- **⚪ Pole Structure**: Singularity and residue analysis
- **📈 Contour Mapping**: Topographic field visualization
- **📝 Markdown Notes**: Rich text with variable substitution
- **🐍 Python Execution**: Interactive code cells with output
- **📊 Data Visualization**: Configurable 2D plotting widgets
- **📋 Data Generation**: Synthetic datasets for analysis

**Topics:** Complex Analysis • Elliptic Functions • Interactive Workspaces • Computational Notebooks

---

## About This Platform

This platform transforms mathematical concepts into **interactive collaborative workspaces** that run entirely in your web browser. Each notebook combines:

- **🧩 Widget-Based Architecture** with drag-and-drop mathematical components
- **📊 Interactive Visualizations** powered by Python scientific libraries in WebAssembly
- **🔗 Schema-Driven Connections** for building computational pipelines
- **💾 Session Persistence** with JSON-based configuration management
- **📱 Responsive Design** optimized for desktop, tablet, and mobile
- **🌙 Professional Dark Mode** with clean, modern interface design
- **⚡ Zero Installation** - just click and start building mathematical workspaces

## Technology

Built with modern web technologies:
- **[Pyodide](https://pyodide.org/)**: Python compiled to WebAssembly
- **Scientific Computing**: NumPy, Matplotlib running in browser  
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Static Deployment**: Hosted via GitHub Pages with no server required

## Adding New Notebooks

This platform is designed for extensibility. New mathematical notebooks can be added by:

1. Creating a new markdown file (e.g., `fourier-analysis.md`)
2. Adding the interactive components using HTML within markdown
3. Including the necessary JavaScript and CSS files
4. Updating the main index to list the new notebook

Each notebook operates independently with its own resources and mathematical focus.

---

*Start exploring by clicking on any notebook above, or browse the [source code](https://github.com/litlfred/notebooks) to see how these interactive mathematical experiences are created.*