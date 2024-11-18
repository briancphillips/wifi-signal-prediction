import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.floor_plan_generator import FloorPlanGenerator, BuildingMaterials
from src.visualization.building_visualizer import BuildingVisualizer
import matplotlib.pyplot as plt
import numpy as np

def generate_example_images():
    """Generate example images for the visualization guide."""
    
    output_dir = os.path.join('results', 'visualization_guide')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a simple floor plan
    generator = FloorPlanGenerator(width=800, height=600)
    generator.add_room(100, 100, 600, 400, 'open_space')
    floor_plan_path = os.path.join(output_dir, 'simple_floor_plan.png')
    generator.draw_floor_plan(floor_plan_path)
    
    # Single AP Coverage Example
    building_viz = BuildingVisualizer(floor_plan_path, output_dir=output_dir)
    building_viz.add_access_point(50, 50, 'AP1_Ch1')
    building_viz.create_all_visualizations()
    
    # Rename the single AP coverage map
    os.rename(
        os.path.join(output_dir, 'coverage_AP1_Ch1.png'),
        os.path.join(output_dir, 'coverage_example.png')
    )
    
    # Generate bad deployment example
    building_viz = BuildingVisualizer(floor_plan_path, output_dir=output_dir)
    # Add clustered APs
    building_viz.add_access_point(30, 30, 'AP1_Ch1')
    building_viz.add_access_point(35, 35, 'AP2_Ch6')
    building_viz.add_access_point(32, 33, 'AP3_Ch11')
    building_viz.create_all_visualizations()
    
    # Rename the combined coverage map for bad deployment
    os.rename(
        os.path.join(output_dir, 'coverage_combined.png'),
        os.path.join(output_dir, 'bad_deployment.png')
    )
    os.rename(
        os.path.join(output_dir, 'interference_map.png'),
        os.path.join(output_dir, 'interference_example.png')
    )
    
    # Generate good deployment example
    building_viz = BuildingVisualizer(floor_plan_path, output_dir=output_dir)
    # Add well-spaced APs
    building_viz.add_access_point(20, 30, 'AP1_Ch1')
    building_viz.add_access_point(50, 50, 'AP2_Ch6')
    building_viz.add_access_point(80, 30, 'AP3_Ch11')
    building_viz.create_all_visualizations()
    
    # Rename the combined coverage map for good deployment
    os.rename(
        os.path.join(output_dir, 'coverage_combined.png'),
        os.path.join(output_dir, 'good_deployment.png')
    )
    
    # Create a legend image
    plt.figure(figsize=(8, 3))
    gradient = np.linspace(-100, -30, 256).reshape(1, -1)
    plt.imshow(gradient, cmap='RdYlBu_r', aspect='auto')
    plt.colorbar(label='Signal Strength (dBm)')
    plt.title('Signal Strength Scale')
    plt.axis('off')
    plt.savefig(os.path.join(output_dir, 'signal_scale.png'), bbox_inches='tight')
    plt.close()
    
    print("Generated example images for visualization guide")

if __name__ == "__main__":
    generate_example_images()
