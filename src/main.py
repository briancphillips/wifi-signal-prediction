import os
import argparse
from data_collection.collector import WiFiDataCollector
from preprocessing.preprocessor import WiFiDataPreprocessor
from models.wifi_models import WiFiModelTrainer
from visualization.visualizer import WiFiVisualizer
from visualization.building_visualizer import BuildingVisualizer
import pandas as pd
import numpy as np

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

def main():
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
    
    args = parser.parse_args()
    
    # Collect or load data
    if args.collect:
        data = collect_training_data(args.duration, args.interval)
    elif args.data_file:
        if not os.path.exists(args.data_file):
            print(f"Error: Data file {args.data_file} not found")
            return
        data = pd.read_csv(args.data_file)
    elif not args.building_layout:
        print("Error: Must either collect new data (--collect) or provide existing data file (--data-file)")
        return
    
    # Train and evaluate models if data is available
    if args.train and data is not None:
        results, processed_data = train_and_evaluate_models(data)
        
        # Print summary of best model
        best_model = min(results.items(), 
                        key=lambda x: x[1]['metrics']['rmse'])[0]
        print(f"\nBest performing model: {best_model.upper()}")
        print(f"RMSE: {results[best_model]['metrics']['rmse']:.2f}")
        print(f"R2 Score: {results[best_model]['metrics']['r2']:.2f}")
        
        # Create visualizations if requested
        if args.visualize:
            visualizer = WiFiVisualizer()
            visualizer.create_dashboard(data, results)
            
    if args.building_layout:
        # Create building layout visualizations
        floor_plan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'download-4.png')
        building_viz = BuildingVisualizer(floor_plan_path)
        
        # Add access points using percentage coordinates
        ap_locations = [
            (20, 30, 'AP_Floor1_Room101'),  # 20% from left, 30% from top
            (50, 40, 'AP_Floor1_Room102'),  # Center horizontally, 40% from top
            (80, 20, 'AP_Floor2_Room201')   # 80% from left, 20% from top
        ]
        
        for x_percent, y_percent, ssid in ap_locations:
            building_viz.add_access_point(x_percent, y_percent, ssid)
        
        building_viz.create_all_visualizations()

if __name__ == "__main__":
    main()