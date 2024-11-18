import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os

class BuildingVisualizer:
    def __init__(self, floor_plan_path, output_dir='visualizations'):
        """Initialize the building visualizer.
        
        Args:
            floor_plan_path (str): Path to floor plan image
            output_dir (str): Directory to save visualizations
        """
        self.floor_plan_path = floor_plan_path
        self.output_dir = output_dir
        self.access_points = []
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def add_access_point(self, x_percent, y_percent, ssid, channel=None, power_dbm=-20):
        """Add an access point to the visualization.
        
        Args:
            x_percent (float): X position as percentage of width
            y_percent (float): Y position as percentage of height
            ssid (str): AP identifier
            channel (int): WiFi channel number
            power_dbm (float): Transmit power in dBm
        """
        if channel is None:
            # Extract channel from SSID if format is AP*_Ch*
            if '_Ch' in ssid:
                try:
                    channel = int(ssid.split('_Ch')[1])
                except ValueError:
                    channel = 1
            else:
                channel = 1
                
        self.access_points.append({
            'x': x_percent / 100,
            'y': y_percent / 100,
            'ssid': ssid,
            'channel': channel,
            'power': power_dbm
        })
        
    def _calculate_signal_strength(self, x, y, ap, material_loss=0):
        """Calculate signal strength at a point from an AP.
        
        Args:
            x, y (float): Point coordinates
            ap (dict): Access point information
            material_loss (float): Signal loss from materials in dB
            
        Returns:
            float: Signal strength in dBm
        """
        distance = np.sqrt((x - ap['x'])**2 + (y - ap['y'])**2) * 100  # Convert to meters
        # Free space path loss model with material attenuation
        if distance == 0:
            return ap['power']
        signal = ap['power'] - (20 * np.log10(distance) + 20 * np.log10(2400) - 27.55) - material_loss
        return max(-100, signal)  # Cap minimum signal at -100 dBm
        
    def _calculate_interference(self, x, y, channel, exclude_ap=None):
        """Calculate interference at a point from other APs on same or adjacent channels.
        
        Args:
            x, y (float): Point coordinates
            channel (int): Channel to calculate interference for
            exclude_ap (dict): AP to exclude from interference calculation
            
        Returns:
            float: Interference power in dBm
        """
        interference_power = []
        for ap in self.access_points:
            if ap == exclude_ap:
                continue
            # Calculate channel overlap factor (0 to 1)
            channel_diff = abs(ap['channel'] - channel)
            if channel_diff == 0:
                overlap = 1.0
            elif channel_diff <= 4:
                overlap = 1.0 - (channel_diff * 0.2)
            else:
                continue
                
            signal = self._calculate_signal_strength(x, y, ap)
            interference_power.append(10 ** (signal/10) * overlap)
            
        if not interference_power:
            return -100
        return 10 * np.log10(sum(interference_power))
        
    def create_all_visualizations(self):
        """Create all visualizations for the building layout."""
        print("Creating building visualizations...")
        
        # Load floor plan
        floor_plan = plt.imread(self.floor_plan_path)
        height, width = floor_plan.shape[:2]
        
        # Create grid for heatmap
        x = np.linspace(0, 1, 100)
        y = np.linspace(0, 1, 100)
        X, Y = np.meshgrid(x, y)
        
        # Create custom colormap
        colors = ['darkblue', 'blue', 'green', 'yellow', 'red']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('signal_strength', colors, N=n_bins)
        
        # Individual AP coverage maps
        for ap in self.access_points:
            Z = np.zeros_like(X)
            for i in range(len(x)):
                for j in range(len(y)):
                    Z[i,j] = self._calculate_signal_strength(X[i,j], Y[i,j], ap)
            
            plt.figure(figsize=(12, 8))
            plt.imshow(floor_plan, extent=[0, 1, 0, 1], alpha=0.5)
            plt.imshow(Z, extent=[0, 1, 0, 1], alpha=0.5, cmap=cmap)
            plt.colorbar(label='Signal Strength (dBm)')
            plt.scatter(ap['x'], ap['y'], color='red', marker='^', s=100, label=ap['ssid'])
            plt.title(f'Coverage Map - {ap["ssid"]} (Channel {ap["channel"]})')
            plt.legend()
            plt.savefig(os.path.join(self.output_dir, f'coverage_{ap["ssid"]}.png'))
            plt.close()
            
        # Combined coverage map
        Z_combined = np.full_like(X, -100)
        for i in range(len(x)):
            for j in range(len(y)):
                signals = [self._calculate_signal_strength(X[i,j], Y[i,j], ap)
                          for ap in self.access_points]
                Z_combined[i,j] = max(signals)  # Best signal at each point
        
        plt.figure(figsize=(12, 8))
        plt.imshow(floor_plan, extent=[0, 1, 0, 1], alpha=0.5)
        plt.imshow(Z_combined, extent=[0, 1, 0, 1], alpha=0.5, cmap=cmap)
        plt.colorbar(label='Signal Strength (dBm)')
        for ap in self.access_points:
            plt.scatter(ap['x'], ap['y'], color='red', marker='^', s=100, 
                       label=f'{ap["ssid"]} (Ch {ap["channel"]})')
        plt.title('Combined Coverage Map')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'coverage_combined.png'))
        plt.close()
        
        # Interference map
        Z_interference = np.zeros_like(X)
        for i in range(len(x)):
            for j in range(len(y)):
                # Find strongest AP at this point
                signals = [(ap, self._calculate_signal_strength(X[i,j], Y[i,j], ap))
                          for ap in self.access_points]
                best_ap, best_signal = max(signals, key=lambda x: x[1])
                
                # Calculate interference from other APs
                interference = self._calculate_interference(X[i,j], Y[i,j], 
                                                         best_ap['channel'], 
                                                         exclude_ap=best_ap)
                
                # Calculate Signal-to-Interference Ratio (SIR)
                Z_interference[i,j] = best_signal - interference
        
        plt.figure(figsize=(12, 8))
        plt.imshow(floor_plan, extent=[0, 1, 0, 1], alpha=0.5)
        plt.imshow(Z_interference, extent=[0, 1, 0, 1], alpha=0.5, 
                  cmap='RdYlBu_r', vmin=-10, vmax=30)
        plt.colorbar(label='Signal-to-Interference Ratio (dB)')
        for ap in self.access_points:
            plt.scatter(ap['x'], ap['y'], color='red', marker='^', s=100,
                       label=f'{ap["ssid"]} (Ch {ap["channel"]})')
        plt.title('Interference Map')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'interference_map.png'))
        plt.close()
        
        print(f"Building visualizations saved in {self.output_dir}/")
