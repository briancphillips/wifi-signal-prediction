import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.floor_plan_generator import FloorPlanGenerator, BuildingMaterials, Window
from src.utils.results_manager import ResultsManager

def run_optimal_deployment():
    """Run a simulation of an optimal WiFi deployment with best practices:
    1. Proper number of access points
    2. Strategic AP placement for coverage
    3. Non-overlapping channels
    4. Material considerations
    5. Coverage optimization for high-density areas
    """
    
    # Initialize results manager
    results_manager = ResultsManager()
    results_manager.start_new_run(description="Optimal WiFi Deployment Example")
    
    # Create floor plan generator
    generator = FloorPlanGenerator(width=1200, height=1000, pixels_per_meter=20)
    
    # Add rooms with optimal layout
    # Office area with standard drywall (low signal attenuation)
    generator.add_room(100, 100, 200, 150, 'office')  # Office 1
    generator.add_room(100, 300, 200, 150, 'office')  # Office 2
    generator.add_room(100, 500, 200, 150, 'office')  # Office 3
    
    # Meeting room with strategic window placement
    meeting_room_x = 400
    meeting_room_y = 100
    meeting_room_width = 400
    meeting_room_height = 300
    generator.add_room(meeting_room_x, meeting_room_y, 
                      meeting_room_width, meeting_room_height, 'meeting')
    
    # Add windows to meeting room for better signal propagation
    window_width = 100
    generator.windows.extend([
        Window(meeting_room_x + meeting_room_width/2 - window_width/2, meeting_room_y),  # Top
        Window(meeting_room_x + meeting_room_width, meeting_room_y + meeting_room_height/2),  # Right
        Window(meeting_room_x + meeting_room_width/2 - window_width/2, meeting_room_y + meeting_room_height),  # Bottom
        Window(meeting_room_x, meeting_room_y + meeting_room_height/2)  # Left
    ])
    
    # Large open space with optimized coverage
    generator.add_room(800, 100, 300, 400, 'open_space')
    
    # Add corridor
    generator.add_corridor(50, 250, 1100, 250, width=60)
    
    # Save floor plan
    floor_plan_path = os.path.join(results_manager.current_run['path'], 
                                  'floor_plans', 'optimal_deployment.png')
    generator.draw_floor_plan(floor_plan_path)
    
    # Save floor plan info
    results_manager.current_run['files']['floor_plans'].append({
        'filename': 'optimal_deployment.png',
        'description': 'Optimal WiFi deployment following best practices'
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
    
    # Add strategically placed access points
    ap_locations = [
        (20, 30, 'AP1_Ch1'),    # Office area coverage
        (50, 25, 'AP2_Ch6'),    # Meeting room coverage
        (80, 30, 'AP3_Ch11'),   # Open space coverage
        (20, 70, 'AP4_Ch1'),    # Additional office coverage
        (50, 75, 'AP5_Ch6'),    # Additional meeting room coverage
        (80, 70, 'AP6_Ch11'),   # Additional open space coverage
    ]
    
    for x_percent, y_percent, ssid in ap_locations:
        building_viz.add_access_point(x_percent, y_percent, ssid)
    
    building_viz.create_all_visualizations()
    
    # Generate report
    report_path = results_manager.generate_report()
    print(f"\nOptimal deployment analysis finished!")
    print(f"Report generated: {report_path}")
    print(f"Results saved in: {results_manager.current_run['path']}")
    
    return results_manager.current_run['path']

if __name__ == "__main__":
    run_optimal_deployment()
