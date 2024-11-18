import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib import patches
import os
from utils.display_config import DisplayConfig

class BuildingMaterial:
    """Class representing a building material with signal attenuation properties."""
    def __init__(self, name, color, attenuation):
        self.name = name
        self.color = color
        self.attenuation = attenuation

# Define common building materials
BUILDING_MATERIALS = [
    BuildingMaterial('Concrete Wall', '#808080', 12),
    BuildingMaterial('Glass Wall', '#ADD8E6', 3),
    BuildingMaterial('Drywall', '#F5F5DC', 4),
    BuildingMaterial('Metal Door', '#A0A0A0', 6)
]

class BuildingVisualizer:
    def __init__(self, floor_plan_path, output_dir=None, grid_size=100):
        """Initialize the building visualizer with enhanced parameters."""
        self.floor_plan_path = floor_plan_path
        self.output_dir = output_dir or os.path.dirname(floor_plan_path)
        self.grid_size = grid_size
        self.fig, self.ax = plt.subplots(figsize=(DisplayConfig.FIGURE_WIDTH, DisplayConfig.FIGURE_HEIGHT))
        self.status_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes)
        
        # Enhanced color map for signal strength (red = weak, green = strong)
        colors = ['#FF0000', '#FFA500', '#FFFF00', '#90EE90', '#00FF00']
        self.custom_cmap = LinearSegmentedColormap.from_list('custom', colors, N=256)
        
        # Signal strength categories (dBm)
        self.signal_categories = {
            (-30, -50): 'Excellent',
            (-50, -67): 'Very Good',
            (-67, -70): 'Good',
            (-70, -80): 'Fair',
            (-80, -90): 'Poor',
            (-90, -100): 'Very Poor'
        }
        
        self.access_points = []
        self.obstacles = []
        self.load_floor_plan()
        
    def load_floor_plan(self):
        """Load and setup the floor plan with proper scaling."""
        self.floor_plan = plt.imread(self.floor_plan_path)
        self.height, self.width = self.floor_plan.shape[:2]
        self.set_axis_units()
        
    def set_axis_units(self, unit='meters'):
        """Set axis labels with real-world units."""
        scale_factor = self.get_scale_factor(unit)
        self.ax.set_xlabel(f'Distance ({unit})')
        self.ax.set_ylabel(f'Distance ({unit})')
        self.ax.set_xticks(np.arange(0, self.width * scale_factor, 5))
        self.ax.set_yticks(np.arange(0, self.height * scale_factor, 5))
        
    def get_scale_factor(self, unit):
        """Get scale factor for unit conversion."""
        # Assuming 1 pixel = 10cm
        if unit == 'meters':
            return 0.1
        elif unit == 'feet':
            return 0.328084
        return 1.0
        
    def add_access_point(self, x, y, name, is_directional=False, beam_direction=0, beam_width=60):
        """Add an access point with optional directional properties."""
        ap = {
            'x': x, 'y': y, 'name': name,
            'is_directional': is_directional,
            'beam_direction': beam_direction,
            'beam_width': beam_width
        }
        self.access_points.append(ap)
        
    def plot_access_point(self, ap):
        """Plot an access point with reduced marker size."""
        self.ax.scatter(ap['x'], ap['y'],
                       marker='^',
                       color='red',
                       s=50,  # Reduced size
                       label=f"AP: {ap['name']}")
        if ap['is_directional']:
            self.add_directional_indicators(ap)
            
    def add_directional_indicators(self, ap):
        """Add directional beam pattern indicators."""
        angle = ap['beam_direction']
        width = ap['beam_width']
        radius = 50  # Beam length
        
        # Calculate beam edges
        left_angle = np.radians(angle - width/2)
        right_angle = np.radians(angle + width/2)
        
        # Plot beam pattern
        t = np.linspace(left_angle, right_angle, 100)
        x = ap['x'] + radius * np.cos(t)
        y = ap['y'] + radius * np.sin(t)
        self.ax.plot(x, y, '--', color='red', alpha=0.5)
        
    def add_obstacle(self, x, y, width, height, material):
        """Add an obstacle with material properties."""
        obstacle = {
            'x': x, 'y': y,
            'width': width, 'height': height,
            'material': material
        }
        self.obstacles.append(obstacle)
        
    def plot_obstacles(self):
        """Plot obstacles with material-specific colors and attenuation labels."""
        for obstacle in self.obstacles:
            rect = patches.Rectangle(
                (obstacle['x'], obstacle['y']),
                obstacle['width'], obstacle['height'],
                facecolor=obstacle['material'].color,
                alpha=0.5
            )
            self.ax.add_patch(rect)
            # Add attenuation label
            self.ax.text(
                obstacle['x'] + obstacle['width']/2,
                obstacle['y'] + obstacle['height']/2,
                f"-{obstacle['material'].attenuation}dB",
                ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.7)
            )
            
    def add_legend_elements(self):
        """Add comprehensive legend including materials and signal categories."""
        legend_elements = []
        
        # Material elements
        for material in BUILDING_MATERIALS:
            legend_elements.append(
                patches.Patch(facecolor=material.color,
                            alpha=0.5,
                            label=f'{material.name} (-{material.attenuation}dB)')
            )
            
        # Signal strength categories
        for (min_val, max_val), category in self.signal_categories.items():
            legend_elements.append(
                patches.Patch(facecolor=self.get_category_color(min_val),
                            label=f'{category} ({min_val} to {max_val} dBm)')
            )
            
        # AP symbol
        legend_elements.append(
            Line2D([0], [0], marker='^', color='w',
                  markerfacecolor='red', markersize=8,
                  label='Access Point')
        )
        
        self.ax.legend(handles=legend_elements,
                      loc='center left',
                      bbox_to_anchor=(1, 0.5))
        
    def get_category_color(self, signal_strength):
        """Get color for signal strength category."""
        normalized = (signal_strength + 100) / 70  # Normalize -100 to -30 range
        return self.custom_cmap(normalized)
        
    def make_plot_interactive(self):
        """Add interactive hover functionality."""
        def on_hover(event):
            if event.inaxes:
                signal_strength = self.get_signal_strength_at_point(event.xdata, event.ydata)
                self.status_text.set_text(f'Signal: {signal_strength:.1f} dBm')
                self.fig.canvas.draw_idle()
                
        self.fig.canvas.mpl_connect('motion_notify_event', on_hover)
        
    def get_signal_strength_at_point(self, x, y):
        """Calculate signal strength at a specific point."""
        total_signal = -100  # Minimum signal strength
        
        # Flip y-coordinate to match floor plan coordinate system
        y = self.height - y
        
        for ap in self.access_points:
            # Calculate distance in meters (assuming 1 unit = 1 meter)
            distance = np.sqrt((x - ap['x'])**2 + (y - ap['y'])**2)
            
            # WiFi parameters
            transmit_power = 20  # dBm (typical WiFi AP)
            frequency = 2.4  # GHz
            path_loss_exponent = 3.0  # Indoor environment with obstacles
            
            # Free space path loss at reference distance (1m)
            wavelength = 3e8 / (frequency * 1e9)  # meters
            reference_loss = -20 * np.log10(wavelength / (4 * np.pi))
            
            # Path loss model
            if distance > 0:
                path_loss = reference_loss + 10 * path_loss_exponent * np.log10(distance)
                signal = transmit_power - path_loss
                
                # Add material attenuation
                material_loss = self.calculate_material_attenuation(ap['x'], ap['y'], x, y)
                signal -= material_loss
                
                # Directional antenna pattern
                if ap['is_directional']:
                    angle = np.degrees(np.arctan2(y - ap['y'], x - ap['x']))
                    angle_diff = abs(angle - ap['beam_direction'])
                    if angle_diff > ap['beam_width']/2:
                        signal -= 20  # Additional loss outside main beam
                
                # Update total signal if this AP provides better coverage
                total_signal = max(total_signal, signal)
        
        return min(max(total_signal, -100), -30)  # Clamp between -100 and -30 dBm
        
    def calculate_coverage_statistics(self):
        """Calculate coverage statistics for the entire area."""
        x = np.linspace(0, self.width, self.grid_size)
        y = np.linspace(0, self.height, self.grid_size)
        X, Y = np.meshgrid(x, y)
        
        signals = np.zeros_like(X)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                signals[i,j] = self.get_signal_strength_at_point(X[i,j], Y[i,j])
                
        stats = {}
        total_points = signals.size
        for (min_val, max_val), category in self.signal_categories.items():
            points_in_range = np.sum((signals >= min_val) & (signals < max_val))
            stats[category.lower()] = (points_in_range / total_points) * 100
            
        return stats
        
    def create_all_visualizations(self):
        """Create and save all visualizations with enhanced features."""
        self.make_plot_interactive()
        
        # Plot floor plan
        self.ax.imshow(self.floor_plan, extent=[0, self.width, 0, self.height])
        
        # Plot obstacles with materials
        self.plot_obstacles()
        
        # Plot APs and coverage
        for ap in self.access_points:
            self.plot_access_point(ap)
            
        # Generate and plot heatmap
        self.plot_signal_heatmap()
        
        # Add comprehensive legend
        self.add_legend_elements()
        
        # Generate coverage report
        stats = self.calculate_coverage_statistics()
        self.generate_coverage_report(stats)
        
        # Save visualizations
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            plt.savefig(os.path.join(self.output_dir, 'coverage_map.png'),
                       bbox_inches='tight', dpi=DisplayConfig.DPI)
            
    def plot_signal_heatmap(self):
        """Plot signal strength heatmap with increased resolution."""
        x = np.linspace(0, self.width, self.grid_size)
        y = np.linspace(0, self.height, self.grid_size)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        
        # Calculate signal strength for each point
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                Z[i,j] = self.get_signal_strength_at_point(X[i,j], Y[i,j])
        
        # Create heatmap with proper normalization
        signal_range = (-100, -30)  # dBm
        normalized_Z = (Z - signal_range[0]) / (signal_range[1] - signal_range[0])  # 0 to 1
        
        # Plot heatmap with transparency
        # Note: No need for origin='lower' since we flip coordinates in get_signal_strength_at_point
        heatmap = plt.imshow(normalized_Z, extent=[0, self.width, 0, self.height],
                           cmap=self.custom_cmap, vmin=0, vmax=1, alpha=0.5)
        
        # Add colorbar with original dBm values
        cbar = plt.colorbar(heatmap)
        cbar.set_label('Signal Strength (dBm)')
        cbar_ticks = np.linspace(0, 1, 8)
        cbar_labels = [f"{signal_range[0] + x * (signal_range[1] - signal_range[0]):.0f}" for x in cbar_ticks]
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels(cbar_labels)
        
    def calculate_material_attenuation(self, x1, y1, x2, y2):
        """Calculate material attenuation between two points."""
        attenuation = 0
        for obstacle in self.obstacles:
            if (obstacle['x'] <= x1 <= obstacle['x'] + obstacle['width'] and
                obstacle['y'] <= y1 <= obstacle['y'] + obstacle['height']):
                attenuation += obstacle['material'].attenuation
            if (obstacle['x'] <= x2 <= obstacle['x'] + obstacle['width'] and
                obstacle['y'] <= y2 <= obstacle['y'] + obstacle['height']):
                attenuation += obstacle['material'].attenuation
        return attenuation
        
    def generate_coverage_report(self, stats):
        """Generate a detailed coverage analysis report."""
        report = ["# WiFi Coverage Analysis Report\n"]
        report.append("## Coverage Statistics")
        for category, percentage in stats.items():
            report.append(f"- {category.title()}: {percentage:.1f}%")
            
        report.append("\n## Access Points")
        for ap in self.access_points:
            report.append(f"- {ap['name']}: ({ap['x']:.1f}, {ap['y']:.1f})")
            if ap['is_directional']:
                report.append(f"  - Beam Direction: {ap['beam_direction']}°")
                report.append(f"  - Beam Width: {ap['beam_width']}°")
                
        report_path = os.path.join(self.output_dir, 'coverage_report.md')
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))

# Example usage
if __name__ == "__main__":
    visualizer = BuildingVisualizer('floor_plan.png', output_dir='visualizations')
    
    # Add access points
    visualizer.add_access_point(100, 100, 'AP1')
    visualizer.add_access_point(300, 300, 'AP2', is_directional=True, beam_direction=45, beam_width=60)
    
    # Add obstacles
    concrete = BUILDING_MATERIALS[0]
    visualizer.add_obstacle(200, 200, 50, 50, concrete)
    
    # Create visualizations
    visualizer.create_all_visualizations()
