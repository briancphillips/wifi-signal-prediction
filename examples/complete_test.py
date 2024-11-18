import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.floor_plan_generator import FloorPlanGenerator, BuildingMaterials
from src.utils.results_manager import ResultsManager

def run_complete_test():
    """Run a complete test of the WiFi signal prediction system with enhanced floor plans."""
    
    # Initialize results manager
    results_manager = ResultsManager()
    results_manager.start_new_run(description="Complete test with enhanced floor plans")
    
    # Create floor plan generator
    generator = FloorPlanGenerator(width=1200, height=1000, pixels_per_meter=20)
    
    # Add rooms with different types and materials
    # Office area
    generator.add_room(100, 100, 200, 150, 'office')  # Standard office
    generator.add_room(100, 300, 200, 150, 'office')  # Another office
    
    # Meeting rooms
    generator.add_room(400, 100, 300, 200, 'meeting')  # Large meeting room
    generator.add_room(400, 350, 250, 150, 'meeting')  # Small meeting room
    
    # Open space
    generator.add_room(800, 100, 300, 400, 'open_space')  # Open office area
    
    # Add corridor
    generator.add_corridor(50, 250, 1100, 250, width=60)
    
    # Save floor plan
    floor_plan_path = os.path.join(results_manager.current_run['path'], 'floor_plans', 'enhanced_floor_plan.png')
    generator.draw_floor_plan(floor_plan_path)
    
    # Save floor plan info
    results_manager.current_run['files']['floor_plans'].append({
        'filename': 'enhanced_floor_plan.png',
        'description': 'Enhanced office layout with furniture and materials'
    })
    
    # Run WiFi analysis
    from src.data_collection.collector import WiFiDataCollector
    from src.preprocessing.preprocessor import WiFiDataPreprocessor
    from src.models.wifi_models import WiFiModelTrainer
    from src.visualization.visualizer import WiFiVisualizer
    from src.visualization.building_visualizer import BuildingVisualizer
    
    # Collect simulated data
    collector = WiFiDataCollector()
    data = collector.collect_training_data(duration_minutes=1, interval_seconds=1)
    results_manager.save_data(data, 'wifi_data.csv')
    
    # Preprocess data
    preprocessor = WiFiDataPreprocessor()
    processed_data = preprocessor.preprocess(data)
    
    # Train models
    trainer = WiFiModelTrainer()
    results = trainer.train_all_models(processed_data)
    
    # Save model results
    for model_name, model_results in results.items():
        results_manager.save_metrics({
            'rmse': model_results['metrics']['rmse'],
            'r2': model_results['metrics']['r2'],
            'cv_rmse_mean': model_results['cv_results']['mean_rmse'],
            'cv_rmse_std': model_results['cv_results']['std_rmse']
        }, model_name)
    
    # Create visualizations
    visualizer = WiFiVisualizer(output_dir=os.path.join(results_manager.current_run['path'], 'visualizations'))
    visualizer.create_dashboard(data, results)
    
    # Create building visualizations
    building_viz = BuildingVisualizer(
        floor_plan_path,
        output_dir=os.path.join(results_manager.current_run['path'], 'visualizations')
    )
    
    # Add access points at strategic locations
    ap_locations = [
        (20, 30, 'AP_Office_1'),    # Office area
        (50, 40, 'AP_Meeting_1'),   # Meeting room area
        (80, 20, 'AP_OpenSpace_1')  # Open space area
    ]
    
    for x_percent, y_percent, ssid in ap_locations:
        building_viz.add_access_point(x_percent, y_percent, ssid)
    
    building_viz.create_all_visualizations()
    
    # Save visualizations info
    for viz_file in os.listdir(visualizer.output_dir):
        if viz_file.endswith('.png'):
            results_manager.current_run['files']['visualizations'].append({
                'filename': viz_file,
                'description': viz_file.replace('.png', '').replace('_', ' ').title()
            })
    
    # Generate report
    report_path = results_manager.generate_report()
    print(f"\nComplete test finished!")
    print(f"Report generated: {report_path}")
    print(f"Results saved in: {results_manager.current_run['path']}")
    
    return results_manager.current_run['path']

if __name__ == "__main__":
    run_complete_test()
