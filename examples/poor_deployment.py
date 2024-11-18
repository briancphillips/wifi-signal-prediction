import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.floor_plan_generator import FloorPlanGenerator, BuildingMaterials, Wall
from src.utils.results_manager import ResultsManager

def run_poor_deployment():
    """Run a simulation of a poor WiFi deployment with common mistakes:
    1. Too few access points
    2. Poor AP placement (all clustered in one area)
    3. Interference from overlapping channels
    4. Signal blocking materials
    5. No coverage in important areas
    """
    
    # Initialize results manager
    results_manager = ResultsManager()
    results_manager.start_new_run(description="Poor WiFi Deployment Example")
    
    # Create floor plan generator
    generator = FloorPlanGenerator(width=1200, height=1000, pixels_per_meter=20)
    
    # Add rooms with problematic layout
    # Cluster of offices with thick concrete walls
    generator.add_room(100, 100, 200, 150, 'office')  # Office 1
    generator.add_room(100, 300, 200, 150, 'office')  # Office 2
    generator.add_room(100, 500, 200, 150, 'office')  # Office 3
    
    # Large meeting room with metal walls (high signal attenuation)
    meeting_room_x = 400
    meeting_room_y = 100
    meeting_room_width = 400
    meeting_room_height = 300
    generator.add_room(meeting_room_x, meeting_room_y, 
                      meeting_room_width, meeting_room_height, 'meeting')
    
    # Add metal walls to meeting room (high signal attenuation)
    generator.walls.extend([
        Wall(meeting_room_x, meeting_room_y, 
             meeting_room_x + meeting_room_width, meeting_room_y, 
             BuildingMaterials.METAL),  # Top wall
        Wall(meeting_room_x + meeting_room_width, meeting_room_y,
             meeting_room_x + meeting_room_width, meeting_room_y + meeting_room_height,
             BuildingMaterials.METAL),  # Right wall
        Wall(meeting_room_x, meeting_room_y + meeting_room_height,
             meeting_room_x + meeting_room_width, meeting_room_y + meeting_room_height,
             BuildingMaterials.METAL),  # Bottom wall
        Wall(meeting_room_x, meeting_room_y,
             meeting_room_x, meeting_room_y + meeting_room_height,
             BuildingMaterials.METAL)  # Left wall
    ])
    
    # Large open space far from APs
    generator.add_room(800, 100, 300, 400, 'open_space')
    
    # Add corridor
    generator.add_corridor(50, 250, 1100, 250, width=60)
    
    # Save floor plan
    floor_plan_path = os.path.join(results_manager.current_run['path'], 
                                  'floor_plans', 'poor_deployment.png')
    generator.draw_floor_plan(floor_plan_path)
    
    # Save floor plan info
    results_manager.current_run['files']['floor_plans'].append({
        'filename': 'poor_deployment.png',
        'description': 'Poor WiFi deployment with common mistakes'
    })
    
    # Run WiFi analysis
    from src.data_collection.collector import WiFiDataCollector
    from src.preprocessing.preprocessor import WiFiDataPreprocessor
    from src.models.wifi_models import WiFiModelTrainer
    from src.visualization.visualizer import WiFiVisualizer
    from src.visualization.building_visualizer import BuildingVisualizer
    
    # Create building visualizations
    building_viz = BuildingVisualizer(
        floor_plan_path,
        output_dir=os.path.join(results_manager.current_run['path'], 'visualizations')
    )
    
    # Add poorly placed access points (all clustered together)
    ap_locations = [
        (15, 20, 'AP1_Ch1'),     # Three APs too close together
        (18, 22, 'AP2_Ch6'),     # with overlapping channels
        (20, 18, 'AP3_Ch11'),
    ]
    
    for x_percent, y_percent, ssid in ap_locations:
        building_viz.add_access_point(x_percent, y_percent, ssid)
    
    building_viz.create_all_visualizations()
    
    # Generate report
    report_path = results_manager.generate_report()
    print(f"\nPoor deployment analysis finished!")
    print(f"Report generated: {report_path}")
    print(f"Results saved in: {results_manager.current_run['path']}")
    
    return results_manager.current_run['path']

if __name__ == "__main__":
    run_poor_deployment()
