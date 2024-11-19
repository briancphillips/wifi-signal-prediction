"""Module for visualizing WiFi signal strength and building materials."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from typing import List, Tuple, Optional, Dict
from src.physics.materials import Material, MATERIALS

class BuildingVisualizer:
    """Visualizes WiFi signal strength and building materials."""
    
    def __init__(self, width: float = 50.0, height: float = 50.0, resolution: float = 0.5):
        """Initialize the building visualizer.
        
        Args:
            width (float): Width of the building in meters
            height (float): Height of the building in meters
            resolution (float): Grid resolution in meters
        """
        self.width = width
        self.height = height
        self.resolution = resolution
        self.materials_grid = None
        self.walls = []  # List of (material, x, y, w, h) tuples
        self.material_colors = {
            'concrete': '#808080',  # Gray
            'glass': '#ADD8E6',    # Light blue
            'wood': '#8B4513',     # Saddle brown
            'drywall': '#F5F5F5',  # White smoke
            'metal': '#C0C0C0',    # Silver
        }
        
    def add_material(self, material: Material, x: float, y: float, w: float, h: float):
        """Add a material to the building at specified location.
        
        Args:
            material (Material): Material to add
            x (float): X coordinate of bottom-left corner
            y (float): Y coordinate of bottom-left corner
            w (float): Width of material
            h (float): Height of material
        """
        if self.materials_grid is None:
            rows = int(self.height / self.resolution)
            cols = int(self.width / self.resolution)
            self.materials_grid = [[None for _ in range(cols)] for _ in range(rows)]
            
        # Store wall for visualization
        self.walls.append((material, x, y, w, h))
        
        # Convert coordinates to grid indices
        x1 = int(x / self.resolution)
        y1 = int(y / self.resolution)
        x2 = int((x + w) / self.resolution)
        y2 = int((y + h) / self.resolution)
        
        # Ensure indices are within bounds
        x1 = max(0, min(x1, len(self.materials_grid[0])))
        x2 = max(0, min(x2, len(self.materials_grid[0])))
        y1 = max(0, min(y1, len(self.materials_grid)))
        y2 = max(0, min(y2, len(self.materials_grid)))
        
        # Add material to grid
        for i in range(y1, y2):
            for j in range(x1, x2):
                self.materials_grid[i][j] = material
                    
    def plot_signal_strength(self, rssi_values: np.ndarray, points: List[Tuple[float, float]], 
                           ap_location: Tuple[float, float], output_path: str):
        """Plot signal strength heatmap with materials.
        
        Args:
            rssi_values (np.ndarray): Array of RSSI values
            points (List[Tuple[float, float]]): List of measurement points
            ap_location (Tuple[float, float]): Access point location
            output_path (str): Path to save the plot
        """
        plt.figure(figsize=(12, 8))
        
        # Create a regular grid for interpolation
        x = np.linspace(0, self.width, 100)
        y = np.linspace(0, self.height, 75)
        X, Y = np.meshgrid(x, y)
        
        # Interpolate RSSI values
        points_array = np.array(points)
        from scipy.interpolate import griddata
        grid_z = griddata(points_array, rssi_values, (X, Y), method='cubic')
        
        # Plot heatmap
        plt.imshow(grid_z, extent=[0, self.width, 0, self.height], origin='lower',
                  cmap='RdYlBu_r', aspect='equal')
        plt.colorbar(label='Signal Strength (dBm)')
        
        # Plot materials
        for material, x, y, w, h in self.walls:
            color = self.material_colors.get(material.name.lower(), '#FFFFFF')
            rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='black', alpha=0.7)
            plt.gca().add_patch(rect)
            
            # Add material label if the wall is wide enough
            if w > 1.0 or h > 1.0:
                plt.text(x + w/2, y + h/2, material.name,
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=8)
        
        # Plot AP location
        plt.plot(ap_location[0], ap_location[1], 'r*', markersize=15, label='Access Point')
        
        plt.title('WiFi Signal Strength Heatmap')
        plt.xlabel('X (meters)')
        plt.ylabel('Y (meters)')
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
