/**
 * Weierstrass Playground - Browser Application with Pyodide
 * Main JavaScript application for handling UI and Python integration
 */

class WeierstrassApp {
    constructor() {
        this.pyodide = null;
        this.isInitialized = false;
        this.isComputing = false;
        this.lastRenderParams = null;
        this.resizeTimeout = null;
        
        this.initializeEventListeners();
        this.setupResizeHandler();
    }

    /**
     * Setup window resize handler for dynamic re-rendering
     */
    setupResizeHandler() {
        window.addEventListener('resize', () => {
            if (this.lastRenderParams && this.isInitialized && !this.isComputing) {
                // Clear existing timeout
                if (this.resizeTimeout) {
                    clearTimeout(this.resizeTimeout);
                }
                
                // Show re-rendering indicator
                this.updateStatus('Re-rendering due to window resize...', 'computing');
                
                // Debounce resize events - wait 500ms after last resize
                this.resizeTimeout = setTimeout(() => {
                    this.render(true); // Pass true to indicate this is a resize render
                }, 500);
            }
        });
    }

    /**
     * Initialize the application
     */
    async initialize() {
        try {
            await this.loadPyodide();
            await this.setupPython();
            this.showMainContent();
            this.updateStatus('Ready to render. Configure parameters and click "Render" to generate visualization.', 'ready');
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.updateStatus(`Failed to load: ${error.message}`, 'error');
        }
    }

    /**
     * Load Pyodide and required packages with better error handling
     */
    async loadPyodide() {
        this.updateProgress(10, 'Loading Pyodide...');
        
        try {
            // Check if loadPyodide is available
            if (typeof loadPyodide === 'undefined') {
                throw new Error('Pyodide script not loaded. This may be due to network restrictions or CDN blocking.');
            }
            
            this.pyodide = await loadPyodide({
                indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
            });
            
            this.updateProgress(30, 'Loading NumPy...');
            await this.pyodide.loadPackage(['numpy']);
            
            this.updateProgress(60, 'Loading Matplotlib...');
            await this.pyodide.loadPackage(['matplotlib']);
            
        } catch (error) {
            console.error('Failed to load Pyodide:', error);
            if (error.message.includes('network') || error.message.includes('CDN') || error.message.includes('loadPyodide')) {
                throw new Error('Failed to load Pyodide from CDN. Please check your internet connection and any content blockers. If you\'re behind a firewall, you may need to allow access to cdn.jsdelivr.net and unpkg.com.');
            }
            throw error;
        }
        
        this.updateProgress(80, 'Setting up visualization...');
        
        // Configure matplotlib for web display
        this.pyodide.runPython(`
            import matplotlib
            matplotlib.use('Agg')  # Use Anti-Grain Geometry backend for PNG output
            import matplotlib.pyplot as plt
            plt.rcParams['figure.dpi'] = 100
            plt.rcParams['savefig.dpi'] = 150
            plt.rcParams['font.size'] = 10
        `);
        
        this.updateProgress(90, 'Loading Weierstrass library...');
    }

    /**
     * Setup Python environment and load our library
     */
    async setupPython() {
        // Load our Weierstrass playground library using new package structure
        this.pyodide.runPython(`
            import sys
            sys.path.append('./python')
            
            # Import the weierstrass_playground package  
            import weierstrass_playground as wp
            from weierstrass_playground import browser
            
            # Set up browser-specific functions
            import io  
            import base64
            from matplotlib import pyplot as plt
            
            def plot_to_base64(fig):
                """Convert matplotlib figure to base64 string for web display."""
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white', dpi=150)
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                buf.close()
                plt.close(fig)  # Free memory
                return img_str
        `);
        
        this.updateProgress(100, 'Ready!');
        this.isInitialized = true;
    }

    /**
     * Initialize event listeners for UI controls
     */
    initializeEventListeners() {
        // Update value displays for range inputs
        document.querySelectorAll('input[type="range"]').forEach(slider => {
            const valueDisplay = document.getElementById(slider.id + '-value');
            if (valueDisplay) {
                slider.addEventListener('input', () => {
                    valueDisplay.textContent = parseFloat(slider.value).toFixed(slider.step?.includes('.') ? 2 : 0);
                });
            }
        });

        // Action buttons
        document.getElementById('render-btn').addEventListener('click', () => this.render());
        document.getElementById('save-btn').addEventListener('click', () => this.savePlot());
        document.getElementById('help-btn').addEventListener('click', () => this.showHelp());

        // Handle Enter key in number inputs
        document.getElementById('dt').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.render();
            }
        });
    }

    /**
     * Update progress bar and text
     */
    updateProgress(percentage, text) {
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progressFill) progressFill.style.width = percentage + '%';
        if (progressText) progressText.textContent = text;
    }

    /**
     * Show main content and hide loading screen
     */
    showMainContent() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('main-content').style.display = 'block';
    }

    /**
     * Update computation status
     */
    updateStatus(message, type = 'ready') {
        const statusElement = document.getElementById('status');
        const statusP = statusElement.querySelector('p');
        
        statusP.textContent = message;
        
        // Reset classes
        statusElement.className = 'computation-status';
        if (type !== 'ready') {
            statusElement.classList.add(type);
        }
    }

    /**
     * Get current parameter values from the UI
     */
    getParameters() {
        return {
            mode: document.getElementById('mode').value,
            p: parseFloat(document.getElementById('p').value),
            q: parseFloat(document.getElementById('q').value),
            N: parseInt(document.getElementById('N').value),
            grid_x: parseInt(document.getElementById('grid-x').value),
            grid_y: parseInt(document.getElementById('grid-y').value),
            contours: parseInt(document.getElementById('contours').value),
            vec_density: document.getElementById('show-vectors').checked ? 
                        parseInt(document.getElementById('vec-density').value) : 0,
            vec_width: 0.002,
            vec_max_len: 0.5,
            saturation: parseFloat(document.getElementById('saturation').value),
            value_floor: parseFloat(document.getElementById('value-floor').value),
            mag_scale: parseFloat(document.getElementById('mag-scale').value),
            dt: parseFloat(document.getElementById('dt').value),
            T: parseFloat(document.getElementById('T').value),
            blow_thresh: 10.0,
            emoji_size: 20,
            show_lattice_trajectories: document.getElementById('show-lattice').checked,
            particles: this.getParticles()
        };
    }

    /**
     * Get particle initial conditions from UI
     */
    getParticles() {
        const particles = [];
        const particleRows = document.querySelectorAll('.particle-row');
        
        particleRows.forEach(row => {
            const z0Input = row.querySelector('.particle-z0');
            const v0Input = row.querySelector('.particle-v0');
            
            if (z0Input && v0Input) {
                try {
                    // Parse complex numbers from strings like "5+2j" or "3-1j"
                    const z0 = this.parseComplex(z0Input.value);
                    const v0 = this.parseComplex(v0Input.value);
                    particles.push([z0.real, z0.imag, v0.real, v0.imag]);
                } catch (e) {
                    console.warn('Invalid particle values:', z0Input.value, v0Input.value);
                }
            }
        });
        
        return particles;
    }

    /**
     * Parse complex number from string
     */
    parseComplex(str) {
        str = str.trim().replace(/\s+/g, '');
        
        // Handle formats like "5+2j", "3-1j", "5", "2j", etc.
        let real = 0, imag = 0;
        
        // Remove j/i and extract imaginary part
        const imagMatch = str.match(/([+-]?\d*\.?\d*)j$/);
        if (imagMatch) {
            let imagStr = imagMatch[1];
            if (imagStr === '' || imagStr === '+') imagStr = '1';
            if (imagStr === '-') imagStr = '-1';
            imag = parseFloat(imagStr);
            str = str.replace(/[+-]?\d*\.?\d*j$/, '');
        }
        
        // Extract real part
        if (str !== '') {
            real = parseFloat(str);
        }
        
        return { real: isNaN(real) ? 0 : real, imag: isNaN(imag) ? 0 : imag };
    }

    /**
     * Main render function
     */
    async render(isResize = false) {
        if (!this.isInitialized || this.isComputing) {
            return;
        }

        this.isComputing = true;
        const renderBtn = document.getElementById('render-btn');
        renderBtn.disabled = true;
        
        if (isResize) {
            renderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Re-rendering...';
            this.updateStatus('Re-rendering visualization for new window size...', 'computing');
        } else {
            renderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Computing...';
            this.updateStatus('Computing Weierstrass function and trajectories...', 'computing');
        }
        
        try {
            const params = this.getParameters();
            
            // Store parameters for resize re-rendering
            this.lastRenderParams = params;
            
            // Validate parameters
            if (params.particles.length === 0) {
                throw new Error('No valid particles defined. Please add at least one particle.');
            }
            
            if (params.dt <= 0 || params.dt > 1) {
                throw new Error('Time step dt must be between 0 and 1.');
            }

            // Call Python rendering function using new package structure
            const pythonCode = `
# Validate and set parameters
params_dict = {
    'p': ${params.p},
    'q': ${params.q}, 
    'N': ${params.N},
    'nx': ${params.grid_x},
    'ny': ${params.grid_y},
    'n_contours': ${params.contours},
    'vec_density': ${params.vec_density},
    'dt': ${params.dt},
    'T': ${params.T},
    'saturation': ${params.saturation},
    'value_floor': ${params.value_floor},
    'mag_scale': ${params.mag_scale},
    'blow_thresh': ${params.blow_thresh}
}

# Validate parameters for browser safety
validated_params = browser.validate_browser_parameters(params_dict)

# Set parameters from validated values
mode = '${params.mode}'
p, q, N = validated_params['p'], validated_params['q'], validated_params['N']
nx, ny = validated_params['nx'], validated_params['ny'] 
n_contours = validated_params['n_contours']
vec_density = validated_params['vec_density']
vec_width = ${params.vec_width}
vec_max_len = ${params.vec_max_len}
saturation = validated_params['saturation']
value_floor = validated_params['value_floor']
mag_scale = validated_params['mag_scale']
dt = validated_params['dt']
T = validated_params['T']
blow_thresh = validated_params['blow_thresh']
emoji_size = ${params.emoji_size}
show_lattice_trajectories = ${params.show_lattice_trajectories ? 'True' : 'False'}

# Convert particles to the format expected by the browser module
particles = []
particle_data = ${JSON.stringify(params.particles)}
for p_data in particle_data:
    # p_data is [z0_real, z0_imag, v0_real, v0_imag]
    particles.append(p_data)

print(f"Rendering with {len(particles)} particles, grid {nx}x{ny}")

# Generate visualization using new package structure
fig = browser.create_complete_visualization(
    mode, p, q, N, nx, ny, n_contours, vec_density,
    vec_width, vec_max_len, saturation, value_floor,
    mag_scale, particles, dt, T, blow_thresh,
    emoji_size, show_lattice_trajectories
)

# Clean up memory
browser.cleanup_matplotlib()

# Convert to base64 for web display
image_data = plot_to_base64(fig)
`;
            
            this.pyodide.runPython(pythonCode);
            const imageData = this.pyodide.globals.get('image_data');
            
            // Display the image
            this.displayPlot(imageData);
            
            this.updateStatus(`Visualization complete! Grid: ${params.grid_x}×${params.grid_y}, Particles: ${params.particles.length}, N: ${params.N}. Resize window to re-render dynamically.`, 'success');
            
        } catch (error) {
            console.error('Rendering error:', error);
            this.updateStatus(`Error: ${error.message}`, 'error');
        } finally {
            this.isComputing = false;
            renderBtn.disabled = false;
            renderBtn.innerHTML = '<i class="fas fa-play"></i> Render';
        }
    }

    /**
     * Display the generated plot
     */
    displayPlot(imageData) {
        const plotArea = document.getElementById('plot-area');
        plotArea.innerHTML = `<img src="data:image/png;base64,${imageData}" alt="Weierstrass ℘ Visualization" />`;
    }

    /**
     * Save current plot
     */
    savePlot() {
        const img = document.querySelector('#plot-area img');
        if (!img) {
            this.updateStatus('No plot to save. Please render first.', 'error');
            return;
        }

        const link = document.createElement('a');
        link.href = img.src;
        link.download = 'weierstrass_playground.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.updateStatus('Plot saved successfully!', 'success');
    }

    /**
     * Show help modal
     */
    showHelp() {
        document.getElementById('help-modal').style.display = 'flex';
    }
}

// Particle management functions (called from HTML)
function addParticle() {
    const container = document.getElementById('particles-container');
    const newRow = document.createElement('div');
    newRow.className = 'particle-row';
    newRow.innerHTML = `
        <input type="text" class="particle-z0" placeholder="z₀ (e.g., 5+0j)" value="5+0j">
        <input type="text" class="particle-v0" placeholder="v₀ (e.g., 0+1j)" value="0+1j">
        <button class="remove-particle" onclick="removeParticle(this)">×</button>
    `;
    container.appendChild(newRow);
}

function removeParticle(button) {
    const container = document.getElementById('particles-container');
    if (container.children.length > 1) {
        button.parentElement.remove();
    }
}

function closeHelp() {
    document.getElementById('help-modal').style.display = 'none';
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    const app = new WeierstrassApp();
    
    // Start initialization
    app.initialize().catch(error => {
        console.error('Application initialization failed:', error);
    });
    
    // Make app globally available for debugging
    window.weierstrassApp = app;
});