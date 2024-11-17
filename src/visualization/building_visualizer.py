import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle
import matplotlib.image as mpimg
from scipy.interpolate import griddata
import os

class BuildingVisualizer:
    def __init__(self, floor_plan_path, output_dir="visualizations"):
        """Initialize the building visualizer.
        
        Args:
            floor_plan_path (str): Path to the floor plan image
            output_dir (str): Directory to store visualizations
        """
        self.floor_plan_path = floor_plan_path
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Load and store the floor plan image
        self.floor_plan = mpimg.imread(floor_plan_path)
        
        # Get image dimensions
        self.img_height, self.img_width = self.floor_plan.shape[:2]
        
        # Define the building dimensions in pixels
        self.building_width = self.img_width
        self.building_height = self.img_height
        
        # Store AP locations and their properties
        self.access_points = []
        
    def add_access_point(self, x_percent, y_percent, ssid, rssi_range=(-90, -30)):
        """Add an access point to the visualization.
        
        Args:
            x_percent (float): X coordinate as percentage of width (0-100)
            y_percent (float): Y coordinate as percentage of height (0-100)
            ssid (str): Access point SSID
            rssi_range (tuple): Range of RSSI values (min, max)
        """
        # Convert percentage to pixel coordinates
        x = (x_percent / 100) * self.building_width
        y = (y_percent / 100) * self.building_height
        
        self.access_points.append({
            'x': x,
            'y': y,
            'ssid': ssid,
            'rssi_range': rssi_range
        })
        
    def calculate_signal_strength(self, x, y, ap):
        """Calculate theoretical signal strength at a point.
        
        Args:
            x (float): X coordinate in pixels
            y (float): Y coordinate in pixels
            ap (dict): Access point information
            
        Returns:
            float: Estimated RSSI value
        """
        # Calculate distance from AP in pixels
        distance = np.sqrt((x - ap['x'])**2 + (y - ap['y'])**2)
        
        # Convert distance to meters (assume 1 meter = 20 pixels)
        distance_meters = distance / 20
        
        # Path loss model with wall attenuation
        # RSSI = -20 * log10(distance) - 35 - wall_loss
        wall_loss = 0  # This could be calculated based on floor plan analysis
        rssi = -20 * np.log10(max(distance_meters, 0.1)) - 35 - wall_loss
        
        # Clip to the specified range
        return np.clip(rssi, ap['rssi_range'][0], ap['rssi_range'][1])
        
    def create_signal_heatmap(self, resolution=100):
        """Create a signal strength heatmap overlay.
        
        Args:
            resolution (int): Number of points in each dimension
        """
        # Create grid of points
        x = np.linspace(0, self.building_width, resolution)
        y = np.linspace(0, self.building_height, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Calculate signal strength for each AP
        for ap in self.access_points:
            Z = np.zeros_like(X)
            for i in range(resolution):
                for j in range(resolution):
                    Z[i,j] = self.calculate_signal_strength(X[i,j], Y[i,j], ap)
            
            plt.figure(figsize=(15, 10))
            
            # Plot floor plan
            plt.imshow(self.floor_plan, extent=[0, self.building_width, 0, self.building_height], origin='upper')
            
            # Create heatmap overlay
            heatmap = plt.imshow(Z, extent=[0, self.building_width, 0, self.building_height],
                               alpha=0.5, cmap='RdYlBu_r', origin='upper')
            plt.colorbar(heatmap, label='Signal Strength (dBm)')
            
            # Plot AP location
            plt.plot(ap['x'], ap['y'], 'k^', markersize=10, label=f'AP: {ap["ssid"]}')
            
            # Add coverage circles (in pixels)
            coverage_radii = [100, 200, 300]  # pixels
            for radius in coverage_radii:
                circle = Circle((ap['x'], ap['y']), radius, 
                              fill=False, linestyle='--', alpha=0.5)
                plt.gca().add_patch(circle)
            
            plt.title(f'Signal Strength Heatmap - {ap["ssid"]}')
            plt.xlabel('X (pixels)')
            plt.ylabel('Y (pixels)')
            plt.legend()
            
            # Save the plot
            plt.savefig(os.path.join(self.output_dir, f'building_heatmap_{ap["ssid"]}.png'))
            plt.close()
            
    def visualize_combined_coverage(self):
        """Create a visualization showing combined coverage of all APs."""
        plt.figure(figsize=(15, 10))
        
        # Plot floor plan
        plt.imshow(self.floor_plan, extent=[0, self.building_width, 0, self.building_height], origin='upper')
        
        # Plot all APs and their coverage areas
        for ap in self.access_points:
            plt.plot(ap['x'], ap['y'], 'k^', markersize=10, label=f'AP: {ap["ssid"]}')
            
            # Add coverage circles (in pixels)
            coverage_radii = [100, 200, 300]  # pixels
            for radius in coverage_radii:
                circle = Circle((ap['x'], ap['y']), radius, 
                              fill=False, linestyle='--', alpha=0.3)
                plt.gca().add_patch(circle)
        
        plt.title('Combined WiFi Coverage Map')
        plt.xlabel('X (pixels)')
        plt.ylabel('Y (pixels)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'building_coverage.png'))
        plt.close()
        
    def create_3d_signal_map(self, resolution=50):
        """Create a 3D visualization of signal strength.
        
        Args:
            resolution (int): Number of points in each dimension
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        # Create grid of points
        x = np.linspace(0, self.building_width, resolution)
        y = np.linspace(0, self.building_height, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Calculate combined signal strength
        Z = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                # Use maximum signal strength from any AP
                signals = [self.calculate_signal_strength(X[i,j], Y[i,j], ap) 
                          for ap in self.access_points]
                Z[i,j] = max(signals)
        
        # Create 3D plot
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot the surface
        surf = ax.plot_surface(X, Y, Z, cmap='RdYlBu_r', alpha=0.8)
        
        # Add color bar
        plt.colorbar(surf, label='Signal Strength (dBm)')
        
        # Plot AP locations
        for ap in self.access_points:
            ax.scatter([ap['x']], [ap['y']], [-30], 
                      c='black', marker='^', s=100, label=f'AP: {ap["ssid"]}')
        
        ax.set_title('3D Signal Strength Map')
        ax.set_xlabel('X (pixels)')
        ax.set_ylabel('Y (pixels)')
        ax.set_zlabel('Signal Strength (dBm)')
        plt.legend()
        
        # Save the plot
        plt.savefig(os.path.join(self.output_dir, 'building_3d_map.png'))
        plt.close()
        
    def create_all_visualizations(self):
        """Create all building visualizations."""
        print("Creating building visualizations...")
        self.create_signal_heatmap()
        self.visualize_combined_coverage()
        self.create_3d_signal_map()
        print(f"Building visualizations saved in {self.output_dir}/")
