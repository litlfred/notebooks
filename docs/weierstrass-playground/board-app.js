/**
 * Mathematical Board - Miro-like Interactive Workspace
 * Handles widget management, drag-and-drop, and board operations
 */

class MathematicalBoard {
    constructor() {
        this.widgets = new Map();
        this.selectedWidget = null;
        this.dragOffset = { x: 0, y: 0 };
        this.widgetCounter = 0;
        this.isLibraryOpen = true;
        this.gridEnabled = true;
        
        this.initializeBoard();
        this.setupEventListeners();
        this.initializeUserPreferences();
    }

    /**
     * Initialize the board
     */
    initializeBoard() {
        const boardContent = document.getElementById('board-content');
        
        // Setup drag and drop
        this.setupDragAndDrop();
        
        // Load saved board if exists
        this.loadBoardFromStorage();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Widget library items
        const widgetItems = document.querySelectorAll('.widget-item');
        widgetItems.forEach(item => {
            item.addEventListener('dragstart', this.handleWidgetDragStart.bind(this));
            item.addEventListener('click', this.handleWidgetClick.bind(this));
        });

        // Board content
        const boardContent = document.getElementById('board-content');
        boardContent.addEventListener('click', (e) => {
            if (e.target === boardContent) {
                this.deselectAllWidgets();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboard.bind(this));
    }

    /**
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        const boardContent = document.getElementById('board-content');
        
        boardContent.addEventListener('dragover', (e) => {
            e.preventDefault();
            boardContent.classList.add('drag-over');
        });

        boardContent.addEventListener('dragleave', (e) => {
            if (!boardContent.contains(e.relatedTarget)) {
                boardContent.classList.remove('drag-over');
            }
        });

        boardContent.addEventListener('drop', (e) => {
            e.preventDefault();
            boardContent.classList.remove('drag-over');
            
            const widgetType = e.dataTransfer.getData('text/widget-type');
            if (widgetType) {
                const rect = boardContent.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                this.createWidget(widgetType, x, y);
            }
        });
    }

    /**
     * Handle widget drag start
     */
    handleWidgetDragStart(e) {
        const widgetType = e.target.closest('.widget-item').dataset.widgetType;
        e.dataTransfer.setData('text/widget-type', widgetType);
        e.target.closest('.widget-item').classList.add('dragging');
        
        setTimeout(() => {
            e.target.closest('.widget-item').classList.remove('dragging');
        }, 100);
    }

    /**
     * Handle widget click (double-click to add)
     */
    handleWidgetClick(e) {
        const widgetType = e.target.closest('.widget-item').dataset.widgetType;
        
        // Add to center of visible area
        const boardContent = document.getElementById('board-content');
        const rect = boardContent.getBoundingClientRect();
        const x = rect.width / 2 - 150; // Center minus half widget width
        const y = rect.height / 2 - 100; // Center minus half widget height
        
        this.createWidget(widgetType, x, y);
    }

    /**
     * Create a new widget
     */
    createWidget(type, x, y) {
        const widgetId = `widget-${++this.widgetCounter}`;
        const widget = {
            id: widgetId,
            type: type,
            x: x,
            y: y,
            width: 300,
            height: 200,
            title: this.getWidgetTitle(type),
            content: this.getDefaultContent(type),
            config: {}
        };

        // Create DOM element
        const element = this.createWidgetElement(widget);
        
        // Add to board
        document.getElementById('board-content').appendChild(element);
        
        // Store widget
        this.widgets.set(widgetId, widget);
        
        // Make draggable
        this.makeDraggable(element);
        
        // Auto-select new widget
        this.selectWidget(widgetId);
        
        // Auto-save
        this.saveBoardToStorage();
        
        console.log(`Created ${type} widget:`, widget);
    }

    /**
     * Get default title for widget type
     */
    getWidgetTitle(type) {
        const titles = {
            'markdown': '📝 Markdown Note',
            'latex': '🔢 LaTeX Math',
            'python': '🐍 Python Code',
            'weierstrass': '∞ Weierstrass ℘',
            'plot': '📊 2D Plot',
            '3dplot': '📈 3D Plot',
            'dataset': '📋 Dataset',
            'csv': '📄 CSV Data'
        };
        return titles[type] || '📌 Widget';
    }

    /**
     * Get default content for widget type
     */
    getDefaultContent(type) {
        const defaults = {
            'markdown': '# New Note\n\nClick edit to add your **markdown** content with *LaTeX* support:\n\n$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$',
            'latex': '$$\\begin{align}\n\\nabla \\times \\vec{E} &= -\\frac{\\partial \\vec{B}}{\\partial t} \\\\\n\\nabla \\times \\vec{B} &= \\mu_0 \\vec{J} + \\mu_0 \\epsilon_0 \\frac{\\partial \\vec{E}}{\\partial t}\n\\end{align}$$',
            'python': '# Python code cell\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n# Create sample data\nx = np.linspace(0, 2*np.pi, 100)\ny = np.sin(x)\n\n# Plot\nplt.plot(x, y)\nplt.title("Sine Wave")\nplt.show()',
            'weierstrass': 'Interactive Weierstrass ℘ function visualization',
            'plot': 'f(x) = x^2 + 2*x + 1',
            '3dplot': 'f(x,y) = sin(x) * cos(y)',
            'dataset': 'Sample dataset with 100 rows',
            'csv': 'name,value,category\nItem 1,10,A\nItem 2,20,B'
        };
        return defaults[type] || 'Widget content';
    }

    /**
     * Create widget DOM element
     */
    createWidgetElement(widget) {
        const element = document.createElement('div');
        element.className = `board-widget widget-${widget.type}`;
        element.dataset.widgetId = widget.id;
        element.style.left = `${widget.x}px`;
        element.style.top = `${widget.y}px`;
        element.style.width = `${widget.width}px`;
        element.style.height = `${widget.height}px`;

        element.innerHTML = `
            <div class="widget-header">
                <div class="widget-title">
                    ${widget.title}
                </div>
                <div class="widget-actions">
                    <button class="widget-btn" onclick="editWidget('${widget.id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="widget-btn" onclick="runWidget('${widget.id}')" title="Run">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="widget-btn" onclick="deleteWidget('${widget.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="widget-content" id="content-${widget.id}">
                ${this.renderWidgetContent(widget)}
            </div>
        `;

        return element;
    }

    /**
     * Render widget content based on type
     */
    renderWidgetContent(widget) {
        switch (widget.type) {
            case 'markdown':
                return `<div class="markdown-content">${this.renderMarkdown(widget.content)}</div>`;
            
            case 'latex':
                return `<div class="latex-content">${widget.content}</div>`;
            
            case 'python':
                return `<pre class="python-code">${widget.content}</pre>`;
            
            case 'weierstrass':
                return `<div class="visualization-placeholder">
                    <p>Weierstrass ℘ Function</p>
                    <button onclick="loadWeierstrassWidget('${widget.id}')">Load Visualization</button>
                </div>`;
            
            case 'plot':
            case '3dplot':
                return `<div class="plot-placeholder">
                    <p>${widget.content}</p>
                    <button onclick="renderPlot('${widget.id}')">Render Plot</button>
                </div>`;
            
            case 'dataset':
            case 'csv':
                return `<div class="data-preview">
                    <pre>${widget.content}</pre>
                </div>`;
            
            default:
                return `<p>${widget.content}</p>`;
        }
    }

    /**
     * Simple markdown rendering (basic)
     */
    renderMarkdown(content) {
        return content
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    /**
     * Make widget draggable
     */
    makeDraggable(element) {
        let isDragging = false;
        let startX, startY, initialX, initialY;

        const header = element.querySelector('.widget-header');
        
        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            
            const rect = element.getBoundingClientRect();
            initialX = rect.left;
            initialY = rect.top;
            
            element.classList.add('dragging');
            this.selectWidget(element.dataset.widgetId);
            
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            
            const newX = initialX + dx;
            const newY = initialY + dy;
            
            element.style.left = `${Math.max(0, newX)}px`;
            element.style.top = `${Math.max(0, newY)}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                element.classList.remove('dragging');
                
                // Update widget data
                const widget = this.widgets.get(element.dataset.widgetId);
                if (widget) {
                    widget.x = parseInt(element.style.left);
                    widget.y = parseInt(element.style.top);
                    this.saveBoardToStorage();
                }
            }
        });
    }

    /**
     * Select widget
     */
    selectWidget(widgetId) {
        // Deselect all
        this.deselectAllWidgets();
        
        // Select new widget
        const element = document.querySelector(`[data-widget-id="${widgetId}"]`);
        if (element) {
            element.classList.add('selected');
            this.selectedWidget = widgetId;
        }
    }

    /**
     * Deselect all widgets
     */
    deselectAllWidgets() {
        document.querySelectorAll('.board-widget.selected').forEach(el => {
            el.classList.remove('selected');
        });
        this.selectedWidget = null;
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboard(e) {
        if (e.key === 'Delete' && this.selectedWidget) {
            this.deleteWidget(this.selectedWidget);
        }
        
        if (e.key === 'Escape') {
            this.deselectAllWidgets();
            this.closeEditor();
        }
        
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 's':
                    e.preventDefault();
                    this.saveBoard();
                    break;
                case 'z':
                    e.preventDefault();
                    // TODO: Implement undo
                    break;
            }
        }
    }

    /**
     * Delete widget
     */
    deleteWidget(widgetId) {
        const element = document.querySelector(`[data-widget-id="${widgetId}"]`);
        if (element) {
            element.remove();
            this.widgets.delete(widgetId);
            this.saveBoardToStorage();
            console.log(`Deleted widget: ${widgetId}`);
        }
    }

    /**
     * Save board configuration
     */
    saveBoard() {
        const boardData = {
            title: document.getElementById('board-title').textContent,
            widgets: Array.from(this.widgets.values()),
            meta: {
                saved: new Date().toISOString(),
                version: '1.0.0'
            }
        };
        
        // Save to localStorage
        localStorage.setItem('mathematical_board', JSON.stringify(boardData));
        
        // Update status
        this.updateStatus('Board saved', 'success');
        
        console.log('Board saved:', boardData);
    }

    /**
     * Load board configuration
     */
    loadBoard() {
        try {
            const boardData = JSON.parse(localStorage.getItem('mathematical_board'));
            if (!boardData) {
                this.updateStatus('No saved board found', 'warning');
                return;
            }

            // Clear current board
            this.clearBoard();
            
            // Load title
            if (boardData.title) {
                document.getElementById('board-title').textContent = boardData.title;
            }

            // Load widgets
            if (boardData.widgets) {
                boardData.widgets.forEach(widget => {
                    this.widgets.set(widget.id, widget);
                    const element = this.createWidgetElement(widget);
                    document.getElementById('board-content').appendChild(element);
                    this.makeDraggable(element);
                });
                
                this.widgetCounter = Math.max(...boardData.widgets.map(w => 
                    parseInt(w.id.replace('widget-', ''))), 0);
            }

            this.updateStatus('Board loaded', 'success');
            console.log('Board loaded:', boardData);
        } catch (error) {
            console.error('Failed to load board:', error);
            this.updateStatus('Failed to load board', 'error');
        }
    }

    /**
     * Auto-save to localStorage
     */
    saveBoardToStorage() {
        this.saveBoard();
    }

    /**
     * Auto-load from localStorage
     */
    loadBoardFromStorage() {
        // Don't auto-load on initialization to avoid overwriting
        // User can manually load if needed
    }

    /**
     * Clear board
     */
    clearBoard() {
        document.querySelectorAll('.board-widget').forEach(el => el.remove());
        this.widgets.clear();
        this.selectedWidget = null;
        this.widgetCounter = 0;
    }

    /**
     * Export board as JSON
     */
    exportBoard() {
        const boardData = {
            title: document.getElementById('board-title').textContent,
            widgets: Array.from(this.widgets.values()),
            meta: {
                exported: new Date().toISOString(),
                version: '1.0.0'
            }
        };
        
        const blob = new Blob([JSON.stringify(boardData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mathematical-board-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.updateStatus('Board exported', 'success');
    }

    /**
     * Update status
     */
    updateStatus(message, type = 'ready') {
        const statusText = document.getElementById('session-status-text');
        const statusDot = document.getElementById('session-status-dot');
        
        if (statusText) statusText.textContent = message;
        if (statusDot) statusDot.className = `status-dot ${type}`;

        setTimeout(() => {
            if (statusText) statusText.textContent = 'Board Ready';
            if (statusDot) statusDot.className = 'status-dot';
        }, 3000);
    }

    /**
     * Initialize user preferences
     */
    initializeUserPreferences() {
        // Initialize theme
        const savedTheme = localStorage.getItem('weierstrass_theme') || 'dark';
        setTheme(savedTheme);
        
        // Initialize layout mode based on screen size
        const isMobile = window.innerWidth < 1024;
        const defaultMode = isMobile ? 'mobile' : 'desktop';
        setLayoutMode(defaultMode);
    }
}

// ===== GLOBAL FUNCTIONS =====

let boardApp;

/**
 * Widget management functions
 */
function editWidget(widgetId) {
    const widget = boardApp.widgets.get(widgetId);
    if (!widget) return;
    
    const editor = document.getElementById('widget-editor');
    const title = document.getElementById('editor-title');
    const body = document.getElementById('editor-body');
    
    title.textContent = `Edit ${widget.title}`;
    
    // Create appropriate editor based on widget type
    let editorHTML = '';
    switch (widget.type) {
        case 'markdown':
        case 'latex':
            editorHTML = `
                <label>Content:</label>
                <textarea id="editor-content" rows="15" style="width: 100%; padding: 0.5rem; border: 1px solid var(--border-color); border-radius: 4px; background: var(--bg-secondary); color: var(--text-primary);">${widget.content}</textarea>
            `;
            break;
        
        case 'python':
            editorHTML = `
                <label>Python Code:</label>
                <textarea id="editor-content" rows="15" style="width: 100%; padding: 0.5rem; border: 1px solid var(--border-color); border-radius: 4px; background: var(--bg-tertiary); color: var(--text-primary); font-family: monospace;">${widget.content}</textarea>
            `;
            break;
        
        default:
            editorHTML = `
                <label>Content:</label>
                <textarea id="editor-content" rows="10" style="width: 100%; padding: 0.5rem;">${widget.content}</textarea>
            `;
    }
    
    body.innerHTML = editorHTML;
    editor.style.display = 'flex';
    
    // Store current widget for saving
    editor.dataset.widgetId = widgetId;
}

function saveWidget() {
    const editor = document.getElementById('widget-editor');
    const widgetId = editor.dataset.widgetId;
    const content = document.getElementById('editor-content').value;
    
    const widget = boardApp.widgets.get(widgetId);
    if (widget) {
        widget.content = content;
        
        // Update widget display
        const contentElement = document.getElementById(`content-${widgetId}`);
        if (contentElement) {
            contentElement.innerHTML = boardApp.renderWidgetContent(widget);
        }
        
        boardApp.saveBoardToStorage();
        boardApp.updateStatus('Widget saved', 'success');
    }
    
    closeEditor();
}

function closeEditor() {
    document.getElementById('widget-editor').style.display = 'none';
}

function runWidget(widgetId) {
    const widget = boardApp.widgets.get(widgetId);
    if (!widget) return;
    
    boardApp.updateStatus(`Running ${widget.type} widget...`, 'computing');
    
    // TODO: Implement widget execution based on type
    console.log(`Running widget: ${widgetId}`);
    
    setTimeout(() => {
        boardApp.updateStatus('Widget executed', 'success');
    }, 1000);
}

function deleteWidget(widgetId) {
    if (confirm('Delete this widget?')) {
        boardApp.deleteWidget(widgetId);
    }
}

/**
 * Control panel functions
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

function toggleLibrary() {
    const library = document.querySelector('.widget-library');
    if (window.innerWidth <= 768) {
        library.classList.toggle('open');
    } else {
        // Desktop: hide/show library
        const body = document.body;
        body.style.gridTemplateColumns = library.style.display === 'none' 
            ? 'var(--library-width) 1fr' 
            : '0 1fr';
        library.style.display = library.style.display === 'none' ? 'flex' : 'none';
    }
}

function fitToScreen() {
    // TODO: Implement fit to screen functionality
    boardApp.updateStatus('Fit to screen', 'success');
}

function toggleGrid() {
    const boardContent = document.getElementById('board-content');
    boardContent.classList.toggle('no-grid');
    boardApp.gridEnabled = !boardApp.gridEnabled;
    boardApp.updateStatus(`Grid ${boardApp.gridEnabled ? 'enabled' : 'disabled'}`, 'success');
}

function saveBoard() {
    boardApp.saveBoard();
}

function loadBoard() {
    boardApp.loadBoard();
}

function exportBoard() {
    boardApp.exportBoard();
}

function playAllWidgets() {
    boardApp.updateStatus('Running all widgets...', 'computing');
    // TODO: Execute all runnable widgets
    setTimeout(() => {
        boardApp.updateStatus('All widgets executed', 'success');
    }, 2000);
}

function pauseAllWidgets() {
    boardApp.updateStatus('Paused all widgets', 'paused');
    // TODO: Pause all running widgets
}

function clearBoard() {
    if (confirm('Clear all widgets from the board?')) {
        boardApp.clearBoard();
        boardApp.updateStatus('Board cleared', 'success');
    }
}

/**
 * Layout and theme functions
 */
function setLayoutMode(mode) {
    const body = document.body;
    
    body.classList.remove('desktop-mode', 'mobile-mode');
    body.classList.add(`${mode}-mode`);
    
    // Update button states
    document.querySelectorAll('.control-section .control-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeButton = document.getElementById(`${mode}-mode-btn`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
    
    console.log(`Layout mode set to: ${mode}`);
}

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
    
    localStorage.setItem('weierstrass_theme', theme);
    console.log(`Theme set to: ${theme}`);
}

/**
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', () => {
    boardApp = new MathematicalBoard();
    window.boardApp = boardApp; // Make globally available
    
    console.log('Mathematical Board initialized');
});