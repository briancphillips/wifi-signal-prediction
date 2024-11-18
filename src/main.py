import os
import argparse
from data_collection.collector import WiFiDataCollector
from preprocessing.preprocessor import WiFiDataPreprocessor
from models.wifi_models import WiFiModelTrainer
from visualization.visualizer import WiFiVisualizer
from visualization.building_visualizer import BuildingVisualizer
import pandas as pd
import numpy as np
from utils.results_manager import ResultsManager
from utils.floor_plan_generator import FloorPlanGenerator

def collect_training_data(duration_minutes=60, interval_seconds=1):
    """Collect WiFi signal strength data for training.
    
    Args:
        duration_minutes (int): Duration to collect data in minutes
        interval_seconds (int): Interval between measurements in seconds
        
    Returns:
        pd.DataFrame: Collected WiFi data
    """
    collector = WiFiDataCollector()
    print(f"Collecting WiFi data for {duration_minutes} minutes...")
    data = collector.collect_data(duration_seconds=duration_minutes*60, 
                                interval_seconds=interval_seconds)
    print(f"Collected {len(data)} data points")
    return data

def train_and_evaluate_models(data, target_column='rssi'):
    """Train and evaluate all models on the collected data.
    
    Args:
        data (pd.DataFrame): Processed WiFi data
        target_column (str): Name of the target column to predict
        
    Returns:
        dict: Dictionary containing evaluation metrics for each model
    """
    # Prepare features and target
    preprocessor = WiFiDataPreprocessor()
    processed_data = preprocessor.prepare_features(data)
    
    feature_names = preprocessor.get_feature_names()
    X = processed_data[feature_names].values
    y = processed_data[target_column].values
    
    # Initialize model trainer
    trainer = WiFiModelTrainer()
    
    # Split data
    X_train, X_test, y_train, y_test = trainer.prepare_data(X, y)
    
    # Train and evaluate each model
    results = {}
    for model_name in ['knn', 'svr', 'rf']:
        print(f"\nTraining {model_name.upper()} model...")
        
        # Train model
        model = trainer.train_model(model_name, X_train, y_train)
        
        # Make predictions
        y_pred = trainer.predict(model_name, X_test)
        
        # Evaluate model
        metrics = trainer.evaluate_model(model_name, X_test, y_test)
        
        # Cross-validate
        cv_results = trainer.cross_validate(model_name, X, y)
        
        results[model_name] = {
            'metrics': metrics,
            'cv_results': cv_results,
            'model': model,
            'predictions': y_pred,
            'actual': y_test,
            'feature_names': feature_names
        }
        
        print(f"{model_name.upper()} Results:")
        print(f"RMSE: {metrics['rmse']:.2f}")
        print(f"R2 Score: {metrics['r2']:.2f}")
        print(f"Cross-validation RMSE: {cv_results['mean_rmse']:.2f} (+/- {cv_results['std_rmse']:.2f})")
    
    return results, processed_data

def parse_arguments():
    parser = argparse.ArgumentParser(description='WiFi Signal Strength Prediction')
    parser.add_argument('--collect', action='store_true',
                      help='Collect new training data')
    parser.add_argument('--duration', type=int, default=60,
                      help='Duration to collect data (minutes)')
    parser.add_argument('--interval', type=int, default=1,
                      help='Interval between measurements (seconds)')
    parser.add_argument('--train', action='store_true',
                      help='Train models on collected data')
    parser.add_argument('--data-file', type=str,
                      help='Path to existing data file (if not collecting new data)')
    parser.add_argument('--visualize', action='store_true',
                      help='Create visualizations of the data and model results')
    parser.add_argument('--building-layout', action='store_true',
                      help='Create building layout visualizations')
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Initialize results manager
    results_manager = ResultsManager()
    run_description = f"WiFi Signal Prediction - {'Data Collection' if args.collect else 'Analysis'}"
    results_manager.start_new_run(description=run_description)
    
    # Collect or load data
    if args.collect:
        data = collect_training_data(args.duration, args.interval)
        results_manager.save_data(data, 'wifi_data.csv')
    elif args.data_file:
        if not os.path.exists(args.data_file):
            print(f"Error: Data file {args.data_file} not found")
            return
        data = pd.read_csv(args.data_file)
        results_manager.save_data(data, 'input_data.csv')
    elif not args.building_layout:
        print("Error: Must either collect new data (--collect) or provide existing data file (--data-file)")
        return
    
    # Train and evaluate models if data is available
    if args.train and data is not None:
        results, processed_data = train_and_evaluate_models(data)
        
        # Save model results
        for model_name, model_results in results.items():
            results_manager.save_metrics({
                'rmse': model_results['metrics']['rmse'],
                'r2': model_results['metrics']['r2'],
                'cv_rmse_mean': model_results['cv_results']['mean_rmse'],
                'cv_rmse_std': model_results['cv_results']['std_rmse']
            }, model_name)
        
        # Print summary of best model
        best_model = min(results.items(), key=lambda x: x[1]['metrics']['rmse'])[0]
        print(f"\nBest performing model: {best_model}")
        print(f"RMSE: {results[best_model]['metrics']['rmse']:.2f}")
        print(f"R2 Score: {results[best_model]['metrics']['r2']:.2f}")
        
        # Create visualizations if requested
        if args.visualize:
            visualizer = WiFiVisualizer(output_dir=os.path.join(results_manager.current_run['path'], 'visualizations'))
            visualizer.create_dashboard(data, results)
            
            # No need to copy visualizations since they're already in the right place
            for viz_file in os.listdir(visualizer.output_dir):
                if viz_file.endswith('.png'):
                    results_manager.current_run['files']['visualizations'].append({
                        'filename': viz_file,
                        'description': viz_file.replace('.png', '').replace('_', ' ').title()
                    })
            results_manager._save_run_info()
    
    if args.building_layout:
        # Generate a floor plan first
        generator = FloorPlanGenerator(width=1000, height=800)
        generator.generate_office_layout(num_rooms=10)
        
        # Save floor plan to results directory
        floor_plan_path = os.path.join(results_manager.current_run['path'], 'floor_plans', 'generated_floor_plan.png')
        generator.draw_floor_plan(floor_plan_path)
        
        # Use the generated floor plan for building visualization
        building_viz = BuildingVisualizer(
            floor_plan_path,
            output_dir=os.path.join(results_manager.current_run['path'], 'visualizations')
        )
        
        # Add access points at room centers
        ap_locations = []
        for i, room in enumerate(generator.rooms):
            if i < 3:  # Add APs to first 3 rooms
                x_percent = (room['x'] + room['width']/2) / generator.width * 100
                y_percent = (room['y'] + room['height']/2) / generator.height * 100
                ssid = f"AP_{room['type']}_{i+1}"
                ap_locations.append((x_percent, y_percent, ssid))
        
        # Add access points and create visualizations
        for x_percent, y_percent, ssid in ap_locations:
            building_viz.add_access_point(x_percent, y_percent, ssid)
        
        building_viz.create_all_visualizations()
        
        # Save floor plan info
        results_manager.current_run['files']['floor_plans'].append({
            'filename': 'generated_floor_plan.png',
            'description': 'Synthetically generated office layout'
        })
        
        # Save visualizations info
        for viz_file in os.listdir(building_viz.output_dir):
            if viz_file.endswith('.png'):
                results_manager.current_run['files']['visualizations'].append({
                    'filename': viz_file,
                    'description': viz_file.replace('.png', '').replace('_', ' ').title()
                })
        results_manager._save_run_info()
    
    # Generate run report
    report_path = results_manager.generate_report()
    print(f"\nRun report generated: {report_path}")
    print(f"Results saved in: {results_manager.current_run['path']}")

if __name__ == "__main__":
    main()
