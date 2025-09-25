"""
Weierstrass ℘ Playground UI Components

This module contains all UI widgets and layout code for the Weierstrass playground,
separated from both the mathematical logic and the notebook for better maintainability.
"""

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML, Javascript
import matplotlib.pyplot as plt
import numpy as np
from weierstrass_lib import *


class WeierstrassUI:
    """Main UI class for the Weierstrass playground."""
    
    def __init__(self):
        self.current_fig = None
        self.output_widget = widgets.Output()
        self.particle_list = []
        self.particles_container = widgets.VBox()
        
        self._create_widgets()
        self._setup_layout()
        self._initialize_particles()
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Visualization mode selection
        self.mode_dropdown = widgets.Dropdown(
            options=[('Two-panel: ℘(z) and ℘′(z)', 'two_panel'),
                     ('Three-panel: ℘(z), Re(℘′(z)), Im(℘′(z))', 'three_panel'),
                     ('Five-panel: ℘(z), ℘′(z), Re(℘(z)), Im(℘(z))', 'five_panel')],
            value='two_panel',
            description='Mode:'
        )

        # Lattice parameters
        self.p_slider = widgets.FloatSlider(value=11.0, min=1.0, max=20.0, step=0.1, description='p')
        self.q_slider = widgets.FloatSlider(value=5.0, min=1.0, max=20.0, step=0.1, description='q')
        self.N_slider = widgets.IntSlider(value=3, min=0, max=6, description='N (truncation)')

        # Rendering parameters
        self.grid_x_slider = widgets.IntSlider(value=100, min=50, max=300, description='Grid X')
        self.grid_y_slider = widgets.IntSlider(value=100, min=50, max=300, description='Grid Y')
        self.contours_slider = widgets.IntSlider(value=10, min=0, max=30, description='# Contours')
        self.vec_density_slider = widgets.IntSlider(value=20, min=0, max=50, description='Vec density')
        self.vec_width_slider = widgets.FloatSlider(value=0.002, min=0.001, max=0.01, step=0.001, description='Vec width')
        self.vec_max_len_slider = widgets.FloatSlider(value=0.5, min=0.1, max=2.0, step=0.1, description='Vec max len')
        self.show_vectors_checkbox = widgets.Checkbox(value=True, description='Show vectors')

        # Palette parameters (soft by default)
        self.saturation_slider = widgets.FloatSlider(value=0.2, min=0.0, max=1.0, step=0.05, description='Saturation')
        self.value_floor_slider = widgets.FloatSlider(value=0.4, min=0.0, max=1.0, step=0.05, description='Value floor')
        self.mag_scale_slider = widgets.FloatSlider(value=0.8, min=0.1, max=5.0, step=0.1, description='Mag scale')

        # Integration parameters
        self.dt_text = widgets.FloatText(value=0.01, description='dt')
        self.T_slider = widgets.FloatSlider(value=10.0, min=1.0, max=50.0, step=1.0, description='T (duration)')
        self.blowup_thresh_slider = widgets.FloatSlider(value=10.0, min=1.0, max=50.0, step=1.0, description='Blow-up |Δz|')
        self.emoji_size_slider = widgets.IntSlider(value=20, min=10, max=50, description='Emoji size')
        
        # Lattice trajectories option
        self.show_lattice_trajectories_checkbox = widgets.Checkbox(value=False, description='Show lattice trajectories (z=1,2,3..p-1, z\'=i)')

        # Control buttons
        self.render_btn = widgets.Button(description='Render', button_style='primary')
        self.save_btn = widgets.Button(description='Save PNG', button_style='info')
        self.save_hires_btn = widgets.Button(description='Save High-Res PNG', button_style='warning')
        self.help_btn = widgets.Button(description='Help', button_style='', icon='question')
        
        # Particle management
        self.add_particle_btn = widgets.Button(description='Add Particle', button_style='success')
        
        # Connect callbacks
        self.render_btn.on_click(lambda b: self.render_playground())
        self.save_btn.on_click(self.save_figure)
        self.save_hires_btn.on_click(self.save_high_res_figure)
        self.help_btn.on_click(self.show_help)
        self.add_particle_btn.on_click(self.add_particle)
    
    def _setup_layout(self):
        """Setup the UI layout."""
        # Create organized sections
        mode_box = widgets.VBox([
            widgets.HTML("<h3>Visualization Mode</h3>"),
            self.mode_dropdown
        ])

        lattice_box = widgets.VBox([
            widgets.HTML("<h3>Lattice Parameters</h3>"),
            self.p_slider, self.q_slider, self.N_slider
        ])

        rendering_box = widgets.VBox([
            widgets.HTML("<h3>Rendering</h3>"),
            self.grid_x_slider, self.grid_y_slider, self.contours_slider,
            self.show_vectors_checkbox, self.vec_density_slider, 
            self.vec_width_slider, self.vec_max_len_slider
        ])

        palette_box = widgets.VBox([
            widgets.HTML("<h3>Palette</h3>"),
            self.saturation_slider, self.value_floor_slider, self.mag_scale_slider
        ])

        integration_box = widgets.VBox([
            widgets.HTML("<h3>Integration</h3>"),
            self.dt_text, self.T_slider, self.blowup_thresh_slider, self.emoji_size_slider,
            self.show_lattice_trajectories_checkbox
        ])

        particles_box = widgets.VBox([
            widgets.HTML("<h3>Particles</h3>"),
            self.particles_container,
            self.add_particle_btn
        ])

        controls_box = widgets.VBox([
            widgets.HTML("<h3>Controls</h3>"),
            self.render_btn, self.save_btn, self.save_hires_btn, self.help_btn
        ])

        # Layout in three columns
        left_column = widgets.VBox([mode_box, lattice_box, rendering_box])
        middle_column = widgets.VBox([palette_box, integration_box])
        right_column = widgets.VBox([particles_box, controls_box])

        self.ui = widgets.HBox([left_column, middle_column, right_column])
    
    def create_particle_row(self, idx=0, z0_default='5.5+0j', v0_default='0+1j'):
        """Create a particle input row."""
        z0_text = widgets.Text(value=z0_default, description=f'z0 #{idx}')
        v0_text = widgets.Text(value=v0_default, description=f'v0 #{idx}')
        remove_btn = widgets.Button(description='Remove', button_style='danger', 
                                   layout=widgets.Layout(width='80px'))
        
        def remove_particle(b):
            if len(self.particle_list) > 1:
                self.particle_list.remove((z0_text, v0_text, remove_btn, row))
                self.update_particles_display()
        
        remove_btn.on_click(remove_particle)
        row = widgets.HBox([z0_text, v0_text, remove_btn])
        
        return z0_text, v0_text, remove_btn, row
    
    def add_particle(self, b=None, z0_default='5.5+0j', v0_default='0+1j'):
        """Add a new particle."""
        idx = len(self.particle_list)
        particle_row = self.create_particle_row(idx, z0_default, v0_default)
        self.particle_list.append(particle_row)
        self.update_particles_display()
    
    def update_particles_display(self):
        """Update the particles display."""
        for i, (z0_text, v0_text, remove_btn, row) in enumerate(self.particle_list):
            z0_text.description = f'z0 #{i}'
            v0_text.description = f'v0 #{i}'
        
        self.particles_container.children = [row for _, _, _, row in self.particle_list]
    
    def get_particles(self):
        """Get current particle initial conditions."""
        particles = []
        for z0_text, v0_text, _, _ in self.particle_list:
            try:
                z0 = complex(z0_text.value)
                v0 = complex(v0_text.value)
                particles.append((z0, v0))
            except ValueError:
                continue
        return particles
    
    def _initialize_particles(self):
        """Initialize with default particles."""
        # z = 5.5, z' = i
        self.add_particle(z0_default='5.5+0j', v0_default='0+1j')
        # z = 5, z' = i  
        self.add_particle(z0_default='5+0j', v0_default='0+1j')
        # z = 7
        self.add_particle(z0_default='7+0j', v0_default='0+0j')
    
    def display(self):
        """Display the UI."""
        display(self.ui)
        
        print("Weierstrass ℘ Playground loaded!")
        print("Configure parameters above and click 'Render' to generate visualization.")
        print("\\nFeatures:")
        print("- Two-panel mode shows ℘(z) and ℘′(z) with color mapping")
        print("- Three-panel mode shows ℘(z), Re(℘′(z)), and Im(℘′(z)) in grayscale")
        print("- Five-panel mode shows ℘(z), ℘′(z), complex plane, Re(℘(z)), and Im(℘(z))")
        print("- Higher N values give more accurate ℘ function but slower computation")
        print("- Trajectories follow z''(t) = -℘(z(t)) * z(t)")
        print("- 💥 marks indicate trajectory blow-ups near poles")
        print("- Click rendered images to view high-resolution versions")
    
    def render_playground(self):
        """Main rendering function."""
        with self.output_widget:
            clear_output(wait=True)
            
            # Get parameters
            mode = self.mode_dropdown.value
            p, q, N = self.p_slider.value, self.q_slider.value, self.N_slider.value
            nx, ny = self.grid_x_slider.value, self.grid_y_slider.value
            n_contours = self.contours_slider.value
            vec_density = self.vec_density_slider.value if self.show_vectors_checkbox.value else 0
            vec_width = self.vec_width_slider.value
            vec_max_len = self.vec_max_len_slider.value
            
            saturation = self.saturation_slider.value
            value_floor = self.value_floor_slider.value
            mag_scale = self.mag_scale_slider.value
            
            dt = max(self.dt_text.value, 1e-6)  # Ensure positive dt
            T = self.T_slider.value
            blow_thresh = self.blowup_thresh_slider.value
            emoji_size = self.emoji_size_slider.value
            show_lattice_trajectories = self.show_lattice_trajectories_checkbox.value
            
            particles = self.get_particles()
            
            print(f"Rendering {mode} with p={p}, q={q}, N={N}, particles={len(particles)}")
            print(f"Grid: {nx}×{ny}, dt={dt}, T={T}")
            
            # Create figure based on mode
            if mode == 'two_panel':
                fig, axes = create_two_panel_figure(p, q)
                ax1, ax2 = axes
                
                # Compute fields
                X1, Y1, F1, M1 = field_grid(p, q, 'wp', N, nx, ny)
                X2, Y2, F2, M2 = field_grid(p, q, 'wp_deriv', N, nx, ny)
                
                # Create backgrounds
                bg1 = soft_background(F1, M1, saturation, mag_scale, value_floor)
                bg2 = soft_background(F2, M2, saturation, mag_scale, value_floor)
                
                # Display backgrounds
                ax1.imshow(bg1, extent=[0, p, 0, q], origin='lower', aspect='equal')
                ax2.imshow(bg2, extent=[0, p, 0, q], origin='lower', aspect='equal')
                
                # Add contours
                add_topo_contours(ax1, X1, Y1, F1, M1, n_contours)
                add_topo_contours(ax2, X2, Y2, F2, M2, n_contours)
                
                # Add vector fields
                if vec_density > 0:
                    vector_overlay(ax1, X1, Y1, F1, M1, vec_density, vec_width, vec_max_len)
                    vector_overlay(ax2, X2, Y2, F2, M2, vec_density, vec_width, vec_max_len)
            
            elif mode == 'three_panel':
                fig, axes = create_three_panel_figure(p, q)
                ax1, ax2, ax3 = axes
                
                # Compute fields
                X1, Y1, F1, M1 = field_grid(p, q, 'wp', N, nx, ny)
                X2, Y2, F2, M2 = field_grid(p, q, 'wp_deriv', N, nx, ny)
                
                # Create backgrounds
                bg1 = soft_background(F1, M1, saturation, mag_scale, value_floor)
                bg2 = grayscale_background(np.real(F2), M2, value_floor)
                bg3 = grayscale_background(np.imag(F2), M2, value_floor)
                
                # Display backgrounds
                ax1.imshow(bg1, extent=[0, p, 0, q], origin='lower', aspect='equal')
                ax2.imshow(bg2, extent=[0, p, 0, q], origin='lower', aspect='equal', cmap='gray')
                ax3.imshow(bg3, extent=[0, p, 0, q], origin='lower', aspect='equal', cmap='gray')
                
                # Add contours
                add_topo_contours(ax1, X1, Y1, F1, M1, n_contours)
                # For grayscale panels, add contours of the real/imaginary parts
                if n_contours > 0:
                    re_F2 = np.real(F2)
                    im_F2 = np.imag(F2)
                    re_F2 = np.where(M2, re_F2, np.nan)
                    im_F2 = np.where(M2, im_F2, np.nan)
                    
                    if not np.all(np.isnan(re_F2)):
                        vmin, vmax = np.nanmin(re_F2), np.nanmax(re_F2)
                        if vmax > vmin:
                            levels = np.linspace(vmin, vmax, n_contours)
                            ax2.contour(X2, Y2, re_F2, levels=levels, colors='black', alpha=0.3, linewidths=0.5)
                    
                    if not np.all(np.isnan(im_F2)):
                        vmin, vmax = np.nanmin(im_F2), np.nanmax(im_F2)
                        if vmax > vmin:
                            levels = np.linspace(vmin, vmax, n_contours)
                            ax3.contour(X2, Y2, im_F2, levels=levels, colors='black', alpha=0.3, linewidths=0.5)
                
                # Add vector fields only to the first panel in three-panel mode
                if vec_density > 0:
                    vector_overlay(ax1, X1, Y1, F1, M1, vec_density, vec_width, vec_max_len)
            
            elif mode == 'five_panel':
                fig, axes = create_five_panel_figure(p, q)
                ax1, ax2, ax3, ax4, ax5 = axes
                
                # Compute fields
                X1, Y1, F1, M1 = field_grid(p, q, 'wp', N, nx, ny)
                X2, Y2, F2, M2 = field_grid(p, q, 'wp_deriv', N, nx, ny)
                
                # Create backgrounds
                bg1 = soft_background(F1, M1, saturation, mag_scale, value_floor)  # ℘(z) color
                bg2 = soft_background(F2, M2, saturation, mag_scale, value_floor)  # ℘′(z) color
                # For ax3, show a simple grid or lattice visualization
                bg3 = np.ones((ny, nx, 3)) * 0.95  # Light gray background
                bg4 = grayscale_background(np.real(F1), M1, value_floor)  # Re(℘(z))
                bg5 = grayscale_background(np.imag(F1), M1, value_floor)  # Im(℘(z))
                
                # Display backgrounds
                ax1.imshow(bg1, extent=[0, p, 0, q], origin='lower', aspect='equal')
                ax2.imshow(bg2, extent=[0, p, 0, q], origin='lower', aspect='equal')
                ax3.imshow(bg3, extent=[0, p, 0, q], origin='lower', aspect='equal')
                ax4.imshow(bg4, extent=[0, p, 0, q], origin='lower', aspect='equal', cmap='gray')
                ax5.imshow(bg5, extent=[0, p, 0, q], origin='lower', aspect='equal', cmap='gray')
                
                # Add contours
                add_topo_contours(ax1, X1, Y1, F1, M1, n_contours)
                add_topo_contours(ax2, X2, Y2, F2, M2, n_contours)
                
                # For grayscale panels, add contours of the real/imaginary parts
                if n_contours > 0:
                    re_F1 = np.real(F1)
                    im_F1 = np.imag(F1)
                    re_F1 = np.where(M1, re_F1, np.nan)
                    im_F1 = np.where(M1, im_F1, np.nan)
                    
                    if not np.all(np.isnan(re_F1)):
                        vmin, vmax = np.nanmin(re_F1), np.nanmax(re_F1)
                        if vmax > vmin:
                            levels = np.linspace(vmin, vmax, n_contours)
                            ax4.contour(X1, Y1, re_F1, levels=levels, colors='black', alpha=0.3, linewidths=0.5)
                    
                    if not np.all(np.isnan(im_F1)):
                        vmin, vmax = np.nanmin(im_F1), np.nanmax(im_F1)
                        if vmax > vmin:
                            levels = np.linspace(vmin, vmax, n_contours)
                            ax5.contour(X1, Y1, im_F1, levels=levels, colors='black', alpha=0.3, linewidths=0.5)
                
                # Add vector fields to first two panels
                if vec_density > 0:
                    vector_overlay(ax1, X1, Y1, F1, M1, vec_density, vec_width, vec_max_len)
                    vector_overlay(ax2, X2, Y2, F2, M2, vec_density, vec_width, vec_max_len)
                
                # Draw lattice points on ax3 (complex plane)
                for m in range(-N, N+1):
                    for n in range(-N, N+1):
                        omega = m * p + n * 1j * q
                        omega_wrapped = (omega.real % p) + 1j * (omega.imag % q)
                        ax3.plot(omega_wrapped.real, omega_wrapped.imag, 'ko', markersize=3, alpha=0.6)
            
            else:  # fallback to two_panel
                fig, axes = create_two_panel_figure(p, q)
                ax1, ax2 = axes
                
                # Compute fields
                X1, Y1, F1, M1 = field_grid(p, q, 'wp', N, nx, ny)
                X2, Y2, F2, M2 = field_grid(p, q, 'wp_deriv', N, nx, ny)
                
                # Create backgrounds
                bg1 = soft_background(F1, M1, saturation, mag_scale, value_floor)
                bg2 = soft_background(F2, M2, saturation, mag_scale, value_floor)
                
                # Display backgrounds
                ax1.imshow(bg1, extent=[0, p, 0, q], origin='lower', aspect='equal')
                ax2.imshow(bg2, extent=[0, p, 0, q], origin='lower', aspect='equal')
                
                # Add contours
                add_topo_contours(ax1, X1, Y1, F1, M1, n_contours)
                add_topo_contours(ax2, X2, Y2, F2, M2, n_contours)
                
                # Add vector fields
                if vec_density > 0:
                    vector_overlay(ax1, X1, Y1, F1, M1, vec_density, vec_width, vec_max_len)
                    vector_overlay(ax2, X2, Y2, F2, M2, vec_density, vec_width, vec_max_len)
            
            # Integrate and plot trajectories
            trajectories = []
            colors = plt.cm.tab10(np.linspace(0, 1, len(particles)))
            
            for i, (z0, v0) in enumerate(particles):
                try:
                    trajectory, blowup_point = integrate_second_order_with_blowup(
                        z0, v0, dt, T, p, q, N, blow_thresh
                    )
                    trajectories.append((trajectory, blowup_point))
                except Exception as e:
                    print(f"Error integrating particle {i}: {e}")
                    trajectories.append((np.array([z0]), None))
            
            # Plot trajectories on all axes
            plot_trajectories_on_axes(axes, trajectories, colors, p, q, emoji_size)
            
            # Plot lattice trajectories if requested
            if show_lattice_trajectories:
                lattice_trajectories = []
                # Generate trajectories for z = 1, 2, 3, ..., p-1 with z' = i
                for k in range(1, int(p)):
                    z0 = complex(k, 0)
                    v0 = complex(0, 1)  # z' = i
                    try:
                        trajectory, blowup_point = integrate_second_order_with_blowup(
                            z0, v0, dt, T, p, q, N, blow_thresh
                        )
                        lattice_trajectories.append((trajectory, blowup_point))
                    except Exception as e:
                        print(f"Error integrating lattice trajectory k={k}: {e}")
                        lattice_trajectories.append((np.array([z0]), None))
                
                # Plot lattice trajectories as dotted grey lines
                plot_lattice_trajectories_on_axes(axes, lattice_trajectories, p, q)
            
            plt.tight_layout()
            self.current_fig = fig
            plt.show()
            
            # Add clickable high-res functionality
            print("\\n✨ Click the image above to open a high-resolution version in a new tab!")
    
    def show_help(self, b):
        """Display help information."""
        from weierstrass_preamble import get_help
        with self.output:
            self.output.clear_output()
            get_help()
    
    def save_figure(self, b=None):
        """Save current figure as PNG."""
        if self.current_fig is not None:
            filename = 'weierstrass_playground.png'
            self.current_fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Figure saved as {filename}")
        else:
            print("No figure to save. Please render first.")
    
    def save_high_res_figure(self, b=None):
        """Save current figure as high-resolution PNG."""
        if self.current_fig is not None:
            filename = 'weierstrass_playground_highres.png'
            self.current_fig.savefig(filename, dpi=600, bbox_inches='tight', facecolor='white')
            print(f"High-resolution figure saved as {filename} (600 DPI)")
        else:
            print("No figure to save. Please render first.")
    
    def get_output_widget(self):
        """Get the output widget for displaying results."""
        return self.output_widget


# Convenience function for easy notebook usage
def create_ui():
    """Create and return a new WeierstrassUI instance."""
    return WeierstrassUI()