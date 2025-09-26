---
layout: default
title: Mathematical Notebooks
description: Interactive browser-based mathematical playgrounds powered by Python and WebAssembly
---

# 🧮 Mathematical Notebooks

Welcome to an interactive collection of **mathematical notebooks** that run entirely in your browser. These playgrounds leverage the power of Python, NumPy, and Matplotlib through WebAssembly, requiring zero installation.

## Available Notebooks

### [℘ Weierstrass ℘ Playground](weierstrass-playground/)

Interactive visualization of the **Weierstrass ℘ function** with particle trajectory dynamics. Explore elliptic functions, complex analysis, and differential equations in real-time.

**Features:**
- Complex field visualization with HSV color mapping
- Real-time particle trajectory integration
- RK4 numerical integration with blow-up detection  
- Dynamic parameter adjustment
- Mobile responsive interface

**Topics:** Complex Analysis • Elliptic Functions • Differential Equations • Numerical Integration

---

## About This Platform

This platform transforms mathematical concepts into **interactive experiences** that run entirely in your web browser. Each notebook combines:

- **Rich mathematical content** with proper documentation
- **Interactive visualizations** powered by Python scientific libraries
- **Zero installation requirements** - just click and explore
- **Educational accessibility** for students and researchers worldwide

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