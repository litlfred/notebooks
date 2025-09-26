---
layout: default
title: Weierstrass ℘ Playground
description: Interactive visualization of the Weierstrass ℘ function with particle trajectory dynamics
---

# Weierstrass ℘ Playground

Interactive mathematical playground exploring the **Weierstrass ℘ function** and particle dynamics in complex fields.

## About the Mathematics

The [Weierstrass ℘ function](https://en.wikipedia.org/wiki/Weierstrass_elliptic_function) is a doubly periodic meromorphic function that plays a fundamental role in the theory of elliptic functions. For a rectangular lattice Λ = ℤp + ℤiq, it's defined as:

℘(z) = 1/z² + Σ[1/(z-ω)² - 1/ω²]

where the sum runs over all non-zero lattice points ω within a truncation bound N.

## Particle Dynamics

This playground integrates **particle trajectories** following the second-order differential equation:

**z''(t) = -℘(z(t)) · z(t)**

The particles move in the complex plane under the influence of the Weierstrass potential, creating beautiful and mathematically rich trajectories that reveal the structure of elliptic functions.

## Features

- **Real-time visualization** of ℘(z) and ℘'(z) fields using HSV color mapping
- **Interactive trajectory integration** with RK4 method and blow-up detection  
- **Dynamic parameter adjustment** with immediate visual feedback
- **Lattice structure exploration** with systematic trajectory generation
- **Mobile responsive** interface that works on any device
- **Zero installation** required - runs entirely in your browser using Python + NumPy + Matplotlib via WebAssembly

---

<!-- Interactive Playground Component -->
<div id="weierstrass-playground">
    <div class="loading-section" id="loading">
        <div class="loader">
            <i class="fas fa-cog fa-spin"></i>
            <p>Loading Pyodide and mathematical libraries...</p>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
            <p class="progress-text" id="progress-text">Initializing...</p>
        </div>
    </div>

    <div class="main-content" id="main-content" style="display: none;">
        <div class="controls-section">
            <div class="control-panel">
                <div class="control-group">
                    <h3><i class="fas fa-cogs"></i> Visualization Mode</h3>
                    <div class="form-group">
                        <label for="mode">Mode:</label>
                        <select id="mode">
                            <option value="two_panel">Two-panel: ℘(z) and ℘′(z)</option>
                        </select>
                    </div>
                </div>

                <div class="control-group">
                    <h3><i class="fas fa-th"></i> Lattice Parameters</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="p">p:</label>
                            <input type="range" id="p" min="1" max="20" step="0.1" value="11">
                            <span class="value-display" id="p-value">11.0</span>
                        </div>
                        <div class="form-group">
                            <label for="q">q:</label>
                            <input type="range" id="q" min="1" max="20" step="0.1" value="5">
                            <span class="value-display" id="q-value">5.0</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="N">N (truncation):</label>
                        <input type="range" id="N" min="0" max="6" step="1" value="3">
                        <span class="value-display" id="N-value">3</span>
                    </div>
                </div>

                <div class="control-group">
                    <h3><i class="fas fa-paint-brush"></i> Rendering</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="grid-x">Grid X:</label>
                            <input type="range" id="grid-x" min="50" max="200" step="10" value="100">
                            <span class="value-display" id="grid-x-value">100</span>
                        </div>
                        <div class="form-group">
                            <label for="grid-y">Grid Y:</label>
                            <input type="range" id="grid-y" min="50" max="200" step="10" value="100">
                            <span class="value-display" id="grid-y-value">100</span>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="contours">Contours:</label>
                            <input type="range" id="contours" min="0" max="30" step="1" value="10">
                            <span class="value-display" id="contours-value">10</span>
                        </div>
                        <div class="form-group">
                            <label for="vec-density">Vector Density:</label>
                            <input type="range" id="vec-density" min="0" max="30" step="1" value="15">
                            <span class="value-display" id="vec-density-value">15</span>
                        </div>
                    </div>
                </div>

                <div class="control-group">
                    <h3><i class="fas fa-palette"></i> Color Palette</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="saturation">Saturation:</label>
                            <input type="range" id="saturation" min="0" max="1" step="0.05" value="0.2">
                            <span class="value-display" id="saturation-value">0.20</span>
                        </div>
                        <div class="form-group">
                            <label for="value-floor">Value Floor:</label>
                            <input type="range" id="value-floor" min="0" max="1" step="0.05" value="0.4">
                            <span class="value-display" id="value-floor-value">0.40</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="mag-scale">Magnitude Scale:</label>
                        <input type="range" id="mag-scale" min="0.1" max="3" step="0.1" value="0.8">
                        <span class="value-display" id="mag-scale-value">0.8</span>
                    </div>
                </div>

                <div class="control-group">
                    <h3><i class="fas fa-atom"></i> Particles & Integration</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="dt">Time Step (dt):</label>
                            <input type="number" id="dt" min="0.001" max="0.1" step="0.001" value="0.01">
                        </div>
                        <div class="form-group">
                            <label for="T">Duration (T):</label>
                            <input type="range" id="T" min="1" max="30" step="1" value="10">
                            <span class="value-display" id="T-value">10</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="show-lattice" checked>
                            Show lattice trajectories (z=1,2,3..p-1, z'=i)
                        </label>
                    </div>
                    
                    <div class="particles-section">
                        <h4>Initial Conditions</h4>
                        <div id="particles-container">
                            <div class="particle-row">
                                <input type="text" class="particle-z0" placeholder="z₀ (e.g., 5.5+0j)" value="5.5+0j">
                                <input type="text" class="particle-v0" placeholder="v₀ (e.g., 0+1j)" value="0+1j">
                                <button class="remove-particle" onclick="removeParticle(this)">×</button>
                            </div>
                            <div class="particle-row">
                                <input type="text" class="particle-z0" placeholder="z₀ (e.g., 5+0j)" value="5+0j">
                                <input type="text" class="particle-v0" placeholder="v₀ (e.g., 0+1j)" value="0+1j">
                                <button class="remove-particle" onclick="removeParticle(this)">×</button>
                            </div>
                        </div>
                        <button class="add-particle" onclick="addParticle()">+ Add Particle</button>
                    </div>
                </div>

                <div class="control-group">
                    <div class="action-buttons">
                        <button id="render-btn" class="btn btn-primary">
                            <i class="fas fa-play"></i> Render
                        </button>
                        <button id="save-btn" class="btn btn-secondary">
                            <i class="fas fa-download"></i> Save PNG
                        </button>
                        <button id="help-btn" class="btn btn-info">
                            <i class="fas fa-question-circle"></i> Help
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="visualization-section">
            <div class="computation-status" id="status">
                <p>Ready to render. Configure parameters and click "Render" to generate visualization.</p>
            </div>
            <div class="plot-container">
                <div id="plot-area"></div>
            </div>
        </div>
    </div>

    <div class="help-modal" id="help-modal" style="display: none;">
        <div class="modal-content">
            <span class="close-btn" onclick="closeHelp()">&times;</span>
            <h2>Weierstrass ℘ Playground Help</h2>
            
            <h3>About</h3>
            <p>This playground visualizes the Weierstrass ℘ function and integrates particle trajectories following:</p>
            <p><code>z''(t) = -℘(z(t)) * z(t)</code></p>
            
            <h3>Parameters</h3>
            <ul>
                <li><strong>p, q:</strong> Lattice periods defining Λ = ℤp + ℤiq</li>
                <li><strong>N:</strong> Truncation level (higher = more accurate but slower)</li>
                <li><strong>Grid X/Y:</strong> Resolution of field visualization</li>
                <li><strong>dt, T:</strong> Integration time step and duration</li>
            </ul>
            
            <h3>Performance</h3>
            <p>For best browser performance: Keep grid ≤150, use N≤4, reduce particles for speed</p>
        </div>
    </div>
</div>

<!-- Load required libraries and app -->
<link rel="stylesheet" href="/weierstrass-playground/style.css">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
<script src="/weierstrass-playground/weierstrass-app.js"></script>

---

## Mathematical Background

### Elliptic Functions Theory

The Weierstrass ℘ function is the fundamental building block of **elliptic function theory**. Unlike trigonometric functions which are singly periodic, elliptic functions are **doubly periodic** - they repeat their values when translated by any lattice vector.

### Applications

- **Cryptography**: Elliptic curve cryptography
- **Physics**: Integrable systems and soliton theory  
- **Number Theory**: Modular forms and L-functions
- **Geometry**: Riemann surfaces and algebraic curves

### Further Reading

- *A First Course in Modular Forms* by Diamond & Shurman
- *Elliptic Functions* by Serge Lang  
- *Introduction to Elliptic Curves and Modular Forms* by Neal Koblitz

---

*This interactive playground runs entirely in your browser using [Pyodide](https://pyodide.org/) - Python compiled to WebAssembly. No installation required!*