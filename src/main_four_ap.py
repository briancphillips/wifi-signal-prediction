"""Main script for WiFi signal strength prediction with four access points."""

import os
import json
import time
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.visualization.building_visualizer import BuildingVisualizer
from src.data_collection.wifi_data_collector import WiFiDataCollector
from src.physics.materials import MATERIALS, SignalPath
import logging
from datetime import datetime

def create_building_layout(width, height):
    """Create a complex office layout with walls and different materials.
    
    Args:
        width: Building width in meters
        height: Building height in meters
        
    Returns:
        materials_grid: 2D array of materials
    """
    # Initialize visualizer with correct dimensions and resolution
    resolution = 0.1  # 10cm resolution for better wall definition
    visualizer = BuildingVisualizer(width=width, height=height, resolution=resolution)
    
    # Material thicknesses
    CONCRETE_THICKNESS = 0.6  # Doubled from 0.3
    DRYWALL_THICKNESS = 0.3  # Doubled from 0.15
    DOOR_WIDTH = 2.0  # Doubled from 1.0
    WINDOW_WIDTH = 4.0  # Doubled from 2.0
    WINDOW_HEIGHT = 3.0  # Doubled from 1.5
    
    # Outer walls (concrete)
    visualizer.add_material(MATERIALS['concrete'], 0, 0, CONCRETE_THICKNESS, height)  # Left wall
    visualizer.add_material(MATERIALS['concrete'], 0, height-CONCRETE_THICKNESS, width, CONCRETE_THICKNESS)  # Top wall
    visualizer.add_material(MATERIALS['concrete'], width-CONCRETE_THICKNESS, 0, CONCRETE_THICKNESS, height)  # Right wall
    visualizer.add_material(MATERIALS['concrete'], 0, 0, width, CONCRETE_THICKNESS)  # Bottom wall
    
    # Meeting rooms (top)
    room_width = width / 4 - CONCRETE_THICKNESS
    room_height = height / 3
    for i in range(4):
        x = i * width/4 + CONCRETE_THICKNESS
        # Room dividers
        if i < 3:
            visualizer.add_material(MATERIALS['drywall'], (i+1)*width/4, CONCRETE_THICKNESS, 
                                  DRYWALL_THICKNESS, room_height)
        # Add glass windows
        visualizer.add_material(MATERIALS['glass'], x + room_width/2 - WINDOW_WIDTH/2, 
                              room_height - CONCRETE_THICKNESS, WINDOW_WIDTH, CONCRETE_THICKNESS)
        # Add wooden doors
        visualizer.add_material(MATERIALS['wood'], x + room_width/2 - DOOR_WIDTH/2, 
                              room_height + DRYWALL_THICKNESS, DOOR_WIDTH, DRYWALL_THICKNESS)
    
    # Open office area (middle)
    visualizer.add_material(MATERIALS['drywall'], 0, room_height, width, DRYWALL_THICKNESS)
    visualizer.add_material(MATERIALS['drywall'], 0, 2*room_height, width, DRYWALL_THICKNESS)
    
    # Private offices (bottom)
    office_width = width / 5 - CONCRETE_THICKNESS
    for i in range(5):
        x = i * width/5 + CONCRETE_THICKNESS
        # Office dividers
        if i < 4:
            visualizer.add_material(MATERIALS['drywall'], (i+1)*width/5, 2*room_height, 
                                  DRYWALL_THICKNESS, room_height - CONCRETE_THICKNESS)
        # Add wooden doors
        visualizer.add_material(MATERIALS['wood'], x + office_width/2 - DOOR_WIDTH/2, 
                              2*room_height - DRYWALL_THICKNESS, DOOR_WIDTH, DRYWALL_THICKNESS)
    
    return visualizer.materials_grid, visualizer

def collect_wifi_data(points, ap_locations, collector, materials_grid):
    """Collect WiFi signal strength data from multiple access points.
    
    Args:
        points: List of (x, y) coordinates to sample
        ap_locations: Dictionary of AP names and their (x, y) coordinates
        collector: WiFiDataCollector instance
        materials_grid: Grid of materials in the building
        
    Returns:
        DataFrame containing collected WiFi data
    """
    data = []
    timestamp = time.time()
    
    for ap_name, ap_loc in ap_locations.items():
        # Collect RSSI values for all points
        rssi_values = collector.collect_samples(points, ap_loc, materials_grid)
        
        # Add some realistic noise
        noise = np.random.normal(0, 2, size=len(points))  # 2 dB standard deviation
        rssi_values += noise
        
        # Create data entries
        for (x, y), rssi in zip(points, rssi_values):
            entry = {
                'timestamp': timestamp,
                'ssid': ap_name,
                'bssid': f'00:11:22:33:44:{40+int(ap_name[-1])}',  # Generate unique BSSID
                'rssi': rssi,
                'channel': 1 + (int(ap_name[-1])-1)*5,  # AP1: ch1, AP2: ch6, AP3: ch11, AP4: ch16
                'security': 'WPA2',
                'x': x,
                'y': y
            }
            data.append(entry)
    
    return pd.DataFrame(data)

def save_run_info(args, run_dir, ap_locations):
    """Save run configuration and metadata.
    
    Args:
        args: Command line arguments
        run_dir: Directory to save run information
        ap_locations: Dictionary of AP locations
    """
    run_info = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'configuration': {
            'building_width': args.width,
            'building_height': args.height,
            'resolution': args.resolution,
            'ap_locations': ap_locations
        },
        'materials_used': list(MATERIALS.keys()),
        'access_points': list(ap_locations.keys())
    }
    
    with open(os.path.join(run_dir, 'run_info.json'), 'w') as f:
        json.dump(run_info, f, indent=2)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='WiFi Signal Strength Prediction')
    
    # Building dimensions
    parser.add_argument('--width', type=float, default=30.0,
                      help='Building width in meters (default: 30.0)')
    parser.add_argument('--height', type=float, default=20.0,
                      help='Building height in meters (default: 20.0)')
    
    # Sampling resolution
    parser.add_argument('--resolution', type=int, default=100,
                      help='Number of sample points along width (default: 100)')
    
    return parser.parse_args()

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Initialize components
    collector = WiFiDataCollector()
    
    # Define building layout and materials
    building_width = 50  # meters
    building_height = 30  # meters
    materials_grid, visualizer = create_building_layout(building_width, building_height)
    
    # Define AP locations (in meters)
    ap_locations = {
        'AP1': (10, 10),
        'AP2': (40, 10),
        'AP3': (10, 20),
        'AP4': (40, 20)
    }
    
    # Create higher resolution sampling points grid
    x = np.linspace(0, building_width, 200)  # Increased from 50 to 200
    y = np.linspace(0, building_height, 120)  # Increased from 30 to 120
    X, Y = np.meshgrid(x, y)
    points = list(zip(X.flatten(), Y.flatten()))
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    runs_dir = "runs"
    output_dir = os.path.join(runs_dir, f"run_{timestamp}")
    data_dir = os.path.join(output_dir, "data")
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    # Create or update symbolic link to latest run
    run_last = os.path.join(runs_dir, "run_last")
    if os.path.exists(run_last):
        if os.path.islink(run_last):
            os.unlink(run_last)
        else:
            import shutil
            shutil.rmtree(run_last)
    try:
        os.symlink(f"run_{timestamp}", run_last, target_is_directory=True)
    except OSError:
        # If symlink fails (e.g., on Windows without admin), just copy the directory
        import shutil
        if os.path.exists(run_last):
            shutil.rmtree(run_last)
        shutil.copytree(output_dir, run_last)
    
    # Collect WiFi data
    logging.info("Collecting WiFi data...")
    wifi_data = collect_wifi_data(points, ap_locations, collector, materials_grid)
    
    # Save raw data
    data_path = os.path.join(data_dir, "wifi_data.csv")
    wifi_data.to_csv(data_path, index=False)
    logging.info(f"Raw data saved to {data_path}")
    
    # Process and visualize data
    logging.info("Processing and visualizing data...")
    rssi_by_ap = {}
    for ap_name in ap_locations.keys():
        ap_data = wifi_data[wifi_data['ssid'] == ap_name]
        rssi_values = ap_data['rssi'].values
        rssi_grid = rssi_values.reshape(len(y), len(x))
        rssi_by_ap[ap_name] = rssi_grid
    
    # Combine RSSI values (take maximum at each point)
    combined_rssi = np.maximum.reduce(list(rssi_by_ap.values()))
    
    # Plot individual AP coverage
    for ap_name, rssi_grid in rssi_by_ap.items():
        output_path = os.path.join(plots_dir, f"coverage_{ap_name}.png")
        visualizer.plot_signal_strength(rssi_grid, points, ap_locations[ap_name], output_path)
        logging.info(f"Coverage plot for {ap_name} saved to {output_path}")
    
    # Plot combined coverage
    output_path = os.path.join(plots_dir, f"coverage_combined.png")
    visualizer.plot_signal_strength(combined_rssi, points, ap_locations, output_path)
    logging.info(f"Combined coverage plot saved to {output_path}")
    
    logging.info("Done!")

if __name__ == "__main__":
    main()