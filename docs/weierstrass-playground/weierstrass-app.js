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
        console.log('🎯 WeierstrassApp.initialize() called');
        try {
            console.log('📦 Starting loadPyodide()...');
            await this.loadPyodide();
            console.log('✅ loadPyodide() completed successfully');
            
            console.log('🐍 Starting setupPython()...');
            await this.setupPython();
            console.log('✅ setupPython() completed successfully');
            
            console.log('👁️ Starting showMainContent()...');
            this.showMainContent();
            console.log('✅ showMainContent() completed successfully');
            
            console.log('📢 Updating final status...');
            this.updateStatus('Ready to render. Configure parameters and click "Render" to generate visualization.', 'ready');
            console.log('🎉 Application initialization completed successfully!');
        } catch (error) {
            console.error('❌ Failed to initialize application:', error);
            console.error('❌ Error details:', {
                message: error.message,
                stack: error.stack,
                name: error.name
            });
            this.updateStatus(`Failed to load: ${error.message}`, 'error');
        }
    }

    /**
     * Load Pyodide and required packages with better error handling
     */
    async loadPyodide() {
        console.log('🔗 Starting Pyodide loading process...');
        this.updateProgress(5, 'Connecting to CDN...');
        
        try {
            // Check if loadPyodide is available
            console.log('🔍 Checking if loadPyodide function is available...');
            if (typeof loadPyodide === 'undefined') {
                console.error('❌ loadPyodide function is undefined');
                throw new Error('Pyodide script not loaded. This may be due to network restrictions or CDN blocking.');
            }
            console.log('✅ loadPyodide function is available');
            
            this.updateProgress(10, 'Initializing Pyodide runtime...');
            console.log('🚀 Calling loadPyodide() function...');
            
            this.pyodide = await loadPyodide({
                indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
                stdout: (text) => console.log("📤 Pyodide stdout:", text),
                stderr: (text) => console.warn("📤 Pyodide stderr:", text)
            });
            console.log('✅ Pyodide runtime initialized successfully');
            
            this.updateProgress(35, 'Loading NumPy...');
            console.log('📦 Loading NumPy package...');
            await this.pyodide.loadPackage(['numpy']);
            console.log('✅ NumPy loaded successfully');
            
            this.updateProgress(65, 'Loading Matplotlib...');
            console.log('📦 Loading Matplotlib package...');
            await this.pyodide.loadPackage(['matplotlib']);
            console.log('✅ Matplotlib loaded successfully');
            
        } catch (error) {
            console.error('❌ Failed to load Pyodide:', error);
            console.error('❌ Error type:', error.constructor.name);
            console.error('❌ Error message:', error.message);
            if (error.stack) console.error('❌ Error stack:', error.stack);
            
            if (error.message.includes('network') || error.message.includes('CDN') || error.message.includes('loadPyodide')) {
                throw new Error('Failed to load Pyodide from CDN. Please check your internet connection and any content blockers. If you\'re behind a firewall, you may need to allow access to cdn.jsdelivr.net and unpkg.com.');
            }
            throw error;
        }
        
        this.updateProgress(85, 'Setting up visualization...');
        console.log('🎨 Configuring matplotlib for web display...');
        
        // Configure matplotlib for web display
        try {
            this.pyodide.runPython(`
                import matplotlib
                matplotlib.use('Agg')  # Use Anti-Grain Geometry backend for PNG output
                import matplotlib.pyplot as plt
                plt.rcParams['figure.dpi'] = 100
                plt.rcParams['savefig.dpi'] = 150
                plt.rcParams['font.size'] = 10
            `);
            console.log('✅ Matplotlib configured successfully');
        } catch (error) {
            console.error('❌ Failed to configure matplotlib:', error);
            throw error;
        }
        
        this.updateProgress(95, 'Loading Weierstrass library...');
        console.log('📚 Moving to setupPython() next...');
    }

    /**
     * Setup Python environment and load our library
     */
    async setupPython() {
        console.log('🐍 Starting Python environment setup...');
        
        try {
            console.log('📂 Loading Weierstrass playground library...');
            // Load our Weierstrass playground library using new package structure
            this.pyodide.runPython(`
                print("🔧 Setting up Python sys.path...")
                import sys
                sys.path.append('./python')
                print(f"✅ Python sys.path: {sys.path}")
                
                print("📦 Importing weierstrass_playground package...")
                # Import the weierstrass_playground package  
                import weierstrass_playground as wp
                from weierstrass_playground import browser
                print("✅ weierstrass_playground package imported successfully")
                
                print("🔧 Setting up browser-specific functions...")
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
                
                print("✅ Browser-specific functions set up successfully")
            `);
            console.log('✅ Python environment setup completed successfully');
        } catch (error) {
            console.error('❌ Failed to setup Python environment:', error);
            console.error('❌ Python setup error details:', {
                message: error.message,
                stack: error.stack,
                name: error.name
            });
            throw error;
        }
        
        console.log('📈 Updating progress to 100%...');
        this.updateProgress(100, 'Ready!');
        
        console.log('✅ Setting isInitialized flag...');
        this.isInitialized = true;
        console.log('🎉 setupPython() completed successfully!');
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
        const progressPercentage = document.getElementById('progress-percentage');
        
        if (progressFill) progressFill.style.width = percentage + '%';
        if (progressText) progressText.textContent = text;
        if (progressPercentage) progressPercentage.textContent = percentage + '%';
        
        // Update loading details based on progress
        const loadingDetails = document.getElementById('loading-details');
        if (loadingDetails) {
            if (percentage < 30) {
                loadingDetails.innerHTML = '<small>Downloading Pyodide runtime (~3MB)...</small>';
            } else if (percentage < 60) {
                loadingDetails.innerHTML = '<small>Loading NumPy library...</small>';
            } else if (percentage < 90) {
                loadingDetails.innerHTML = '<small>Loading Matplotlib library...</small>';
            } else if (percentage < 100) {
                loadingDetails.innerHTML = '<small>Setting up visualization environment...</small>';
            } else {
                loadingDetails.innerHTML = '<small>Ready to use!</small>';
            }
        }
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

    /**
     * Session Management - Save configuration to localStorage
     */
    saveSession() {
        const sessionData = {
            parameters: this.getParameters(),
            theme: document.body.getAttribute('data-theme'),
            layoutMode: document.body.classList.contains('desktop-mode') ? 'desktop' : 'mobile',
            timestamp: new Date().toISOString(),
            version: '1.0.0'
        };
        
        localStorage.setItem('weierstrass_session', JSON.stringify(sessionData));
        this.updateSessionStatus('Session saved', 'success');
        console.log('Session saved:', sessionData);
    }

    /**
     * Load session configuration from localStorage
     */
    loadSession() {
        try {
            const sessionData = JSON.parse(localStorage.getItem('weierstrass_session'));
            if (!sessionData) {
                this.updateSessionStatus('No saved session found', 'warning');
                return;
            }

            // Restore parameters
            if (sessionData.parameters) {
                this.setParameters(sessionData.parameters);
            }

            // Restore theme
            if (sessionData.theme) {
                setTheme(sessionData.theme);
            }

            // Restore layout mode
            if (sessionData.layoutMode) {
                setLayoutMode(sessionData.layoutMode);
            }

            this.updateSessionStatus('Session loaded', 'success');
            console.log('Session loaded:', sessionData);
        } catch (error) {
            console.error('Failed to load session:', error);
            this.updateSessionStatus('Failed to load session', 'error');
        }
    }

    /**
     * Set parameters from session data
     */
    setParameters(params) {
        Object.entries(params).forEach(([key, value]) => {
            const element = document.getElementById(key) || document.getElementById(key.replace('_', '-'));
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = value;
                } else {
                    element.value = value;
                }
            }
        });
    }

    /**
     * Update session status indicator
     */
    updateSessionStatus(message, type = 'ready') {
        const statusText = document.getElementById('session-status-text');
        const statusDot = document.getElementById('session-status-dot');
        
        if (statusText) statusText.textContent = message;
        if (statusDot) {
            statusDot.className = `status-dot ${type}`;
        }

        // Clear status after 3 seconds
        setTimeout(() => {
            if (statusText) statusText.textContent = 'Ready';
            if (statusDot) statusDot.className = 'status-dot';
        }, 3000);
    }

    /**
     * Control visualization state
     */
    pauseVisualization() {
        this.isComputing = false;
        this.updateSessionStatus('Visualization paused', 'paused');
    }

    resumeVisualization() {
        if (this.lastRenderParams && this.isInitialized) {
            this.render();
        }
    }

    stopVisualization() {
        this.isComputing = false;
        this.lastRenderParams = null;
        const renderBtn = document.getElementById('render-btn');
        if (renderBtn) {
            renderBtn.innerHTML = '<i class="fas fa-play"></i> Render';
            renderBtn.disabled = false;
        }
        this.updateSessionStatus('Visualization stopped', 'error');
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

// ===== GLOBAL CONTROL FUNCTIONS =====

/**
 * Toggle control panel expansion on mobile
 */
function toggleControlPanel() {
    const panel = document.getElementById('global-controls');
    const icon = document.getElementById('panel-toggle-icon');
    
    panel.classList.toggle('expanded');
    
    if (panel.classList.contains('expanded')) {
        icon.className = 'fas fa-chevron-down';
    } else {
        icon.className = 'fas fa-chevron-up';
    }
}

/**
 * Control all visualizations
 */
function playAllVisualizations() {
    if (window.weierstrassApp) {
        window.weierstrassApp.resumeVisualization();
    }
    updateControlButtonState('play');
}

function pauseAllVisualizations() {
    if (window.weierstrassApp) {
        window.weierstrassApp.pauseVisualization();
    }
    updateControlButtonState('pause');
}

function stopAllVisualizations() {
    if (window.weierstrassApp) {
        window.weierstrassApp.stopVisualization();
    }
    updateControlButtonState('stop');
}

function restartAllVisualizations() {
    if (window.weierstrassApp) {
        window.weierstrassApp.resumeVisualization();
    }
    updateControlButtonState('restart');
}

function updateControlButtonState(action) {
    // Reset all button states
    const buttons = document.querySelectorAll('#global-controls .control-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Set active button
    const activeButton = document.getElementById(`${action}-all-btn`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
}

/**
 * Layout mode switching
 */
function setLayoutMode(mode) {
    const body = document.body;
    
    // Remove existing mode classes
    body.classList.remove('desktop-mode', 'mobile-mode');
    
    // Add new mode class
    body.classList.add(`${mode}-mode`);
    
    // Update button states
    document.querySelectorAll('.control-section .control-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeButton = document.getElementById(`${mode}-mode-btn`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
    
    // Save to session
    if (window.weierstrassApp) {
        window.weierstrassApp.updateSessionStatus(`Layout: ${mode} mode`, 'success');
    }
    
    console.log(`Layout mode set to: ${mode}`);
}

/**
 * Theme switching
 */
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    }
    
    // Save to localStorage for persistence
    localStorage.setItem('weierstrass_theme', theme);
    
    console.log(`Theme set to: ${theme}`);
}

/**
 * Session management functions
 */
function saveSession() {
    if (window.weierstrassApp) {
        window.weierstrassApp.saveSession();
    }
}

function loadSession() {
    if (window.weierstrassApp) {
        window.weierstrassApp.loadSession();
    }
}

/**
 * Initialize theme and layout from localStorage
 */
function initializeUserPreferences() {
    // Initialize theme
    const savedTheme = localStorage.getItem('weierstrass_theme') || 'dark';
    setTheme(savedTheme);
    
    // Initialize layout mode based on screen size
    const isMobile = window.innerWidth < 1024;
    const defaultMode = isMobile ? 'mobile' : 'desktop';
    setLayoutMode(defaultMode);
    
    // Auto-detect layout mode changes on resize
    window.addEventListener('resize', () => {
        const isMobile = window.innerWidth < 1024;
        const currentMode = document.body.classList.contains('desktop-mode') ? 'desktop' : 'mobile';
        const preferredMode = isMobile ? 'mobile' : 'desktop';
        
        if (currentMode !== preferredMode) {
            setLayoutMode(preferredMode);
        }
    });
}

// Initialize the application
function initializeApp() {
    console.log('🚀 Starting app initialization...');
    
    // Initialize user preferences first
    console.log('⚙️ Initializing user preferences...');
    initializeUserPreferences();
    console.log('✅ User preferences initialized');
    
    console.log('🏗️ Creating WeierstrassApp instance...');
    const app = new WeierstrassApp();
    console.log('✅ WeierstrassApp instance created');
    
    // Start initialization
    console.log('🔄 Starting app.initialize()...');
    app.initialize().catch(error => {
        console.error('❌ Application initialization failed:', error);
        console.error('❌ Error stack:', error.stack);
    });
    
    // Make app globally available for debugging
    window.weierstrassApp = app;
    console.log('✅ App made globally available as window.weierstrassApp');
}

// Run initialization when DOM is ready or immediately if already loaded
console.log('🔍 Checking document ready state:', document.readyState);
if (document.readyState === 'loading') {
    console.log('📋 DOM still loading, setting up DOMContentLoaded listener...');
    document.addEventListener('DOMContentLoaded', () => {
        console.log('📋 DOMContentLoaded event fired, initializing app...');
        initializeApp();
    });
} else {
    // DOM is already loaded, run immediately
    console.log('📋 DOM already loaded, initializing app immediately...');
    initializeApp();
}