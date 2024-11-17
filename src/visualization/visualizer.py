import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os

class WiFiVisualizer:
    def __init__(self, output_dir="visualizations"):
        """Initialize the WiFi data visualizer.
        
        Args:
            output_dir (str): Directory to store visualizations
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def plot_signal_heatmap(self, data):
        """Create a heatmap of signal strengths across access points.
        
        Args:
            data (pd.DataFrame): WiFi signal strength data
        """
        # Pivot the data to create a matrix of RSSI values
        pivot_data = data.pivot_table(
            values='rssi',
            index='timestamp',
            columns='ssid',
            aggfunc='mean'
        )
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_data, cmap='RdYlBu_r', center=-65)
        plt.title('WiFi Signal Strength Heatmap')
        plt.xlabel('Access Points')
        plt.ylabel('Time')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'signal_heatmap.png'))
        plt.close()
        
    def plot_signal_over_time(self, data):
        """Plot signal strength over time for each access point.
        
        Args:
            data (pd.DataFrame): WiFi signal strength data
        """
        plt.figure(figsize=(12, 6))
        
        # Plot each access point
        for ssid in data['ssid'].unique():
            ap_data = data[data['ssid'] == ssid]
            plt.plot(ap_data['timestamp'], ap_data['rssi'], label=ssid, alpha=0.7)
        
        plt.title('WiFi Signal Strength Over Time')
        plt.xlabel('Time')
        plt.ylabel('Signal Strength (dBm)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'signal_over_time.png'))
        plt.close()
        
    def plot_predictions_vs_actual(self, y_true, y_pred, model_name):
        """Plot predicted vs actual signal strengths.
        
        Args:
            y_true (np.array): Actual signal strength values
            y_pred (np.array): Predicted signal strength values
            model_name (str): Name of the model used for predictions
        """
        plt.figure(figsize=(8, 8))
        
        # Plot the scatter plot
        plt.scatter(y_true, y_pred, alpha=0.5)
        
        # Plot the perfect prediction line
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')
        
        plt.title(f'{model_name} - Predicted vs Actual Signal Strength')
        plt.xlabel('Actual Signal Strength (dBm)')
        plt.ylabel('Predicted Signal Strength (dBm)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'{model_name.lower()}_predictions.png'))
        plt.close()
        
    def plot_feature_importance(self, model, feature_names):
        """Plot feature importance for tree-based models.
        
        Args:
            model: Trained model with feature_importances_ attribute
            feature_names (list): List of feature names
        """
        if not hasattr(model, 'feature_importances_'):
            return
            
        plt.figure(figsize=(10, 6))
        
        # Get feature importance
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Plot feature importance
        plt.bar(range(len(importances)), importances[indices])
        plt.title('Feature Importance')
        plt.xlabel('Features')
        plt.ylabel('Importance')
        
        # Add feature names to x-axis
        plt.xticks(range(len(importances)), 
                  [feature_names[i] for i in indices],
                  rotation=45,
                  ha='right')
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'feature_importance.png'))
        plt.close()
        
    def plot_signal_distribution(self, data):
        """Plot the distribution of signal strengths.
        
        Args:
            data (pd.DataFrame): WiFi signal strength data
        """
        plt.figure(figsize=(10, 6))
        
        # Plot distribution for each access point
        for ssid in data['ssid'].unique():
            ap_data = data[data['ssid'] == ssid]
            sns.kdeplot(data=ap_data['rssi'], label=ssid, alpha=0.7)
        
        plt.title('Distribution of WiFi Signal Strengths')
        plt.xlabel('Signal Strength (dBm)')
        plt.ylabel('Density')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'signal_distribution.png'))
        plt.close()
        
    def plot_model_comparison(self, models_results):
        """Create a comparison plot of model performances.
        
        Args:
            models_results (dict): Dictionary containing results for each model
        """
        plt.figure(figsize=(12, 6))
        
        # Prepare data for plotting
        models = list(models_results.keys())
        rmse_scores = [results['metrics']['rmse'] for results in models_results.values()]
        r2_scores = [results['metrics']['r2'] for results in models_results.values()]
        cv_rmse = [results['cv_results']['mean_rmse'] for results in models_results.values()]
        cv_std = [results['cv_results']['std_rmse'] for results in models_results.values()]
        
        # Plot settings
        x = np.arange(len(models))
        width = 0.25
        
        # Create grouped bar plot
        plt.bar(x - width, rmse_scores, width, label='RMSE', color='skyblue')
        plt.bar(x, r2_scores, width, label='R² Score', color='lightgreen')
        plt.bar(x + width, cv_rmse, width, label='CV RMSE', color='salmon')
        
        # Add error bars for cross-validation
        plt.errorbar(x + width, cv_rmse, yerr=cv_std, fmt='none', color='black', capsize=5)
        
        # Customize plot
        plt.xlabel('Models')
        plt.ylabel('Score')
        plt.title('Model Performance Comparison')
        plt.xticks(x, [model.upper() for model in models])
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'model_comparison.png'))
        plt.close()
        
    def create_performance_table(self, models_results):
        """Create a detailed performance metrics table.
        
        Args:
            models_results (dict): Dictionary containing results for each model
            
        Returns:
            pd.DataFrame: Table of performance metrics
        """
        metrics = []
        for model_name, results in models_results.items():
            metrics.append({
                'Model': model_name.upper(),
                'RMSE': f"{results['metrics']['rmse']:.4f}",
                'R² Score': f"{results['metrics']['r2']:.4f}",
                'CV RMSE (mean)': f"{results['cv_results']['mean_rmse']:.4f}",
                'CV RMSE (std)': f"{results['cv_results']['std_rmse']:.4f}"
            })
        
        return pd.DataFrame(metrics)

    def create_dashboard(self, data, models_results=None):
        """Create all visualizations for the data.
        
        Args:
            data (pd.DataFrame): WiFi signal strength data
            models_results (dict): Dictionary containing model results
        """
        print("Creating visualizations...")
        
        # Create basic data visualizations
        self.plot_signal_heatmap(data)
        self.plot_signal_over_time(data)
        self.plot_signal_distribution(data)
        
        # Create model-specific visualizations if available
        if models_results:
            # Create model comparison plot
            self.plot_model_comparison(models_results)
            
            # Create and save performance table
            performance_table = self.create_performance_table(models_results)
            performance_table.to_csv(os.path.join(self.output_dir, 'model_performance.csv'), index=False)
            
            for model_name, results in models_results.items():
                if 'predictions' in results:
                    self.plot_predictions_vs_actual(
                        results['actual'],
                        results['predictions'],
                        model_name
                    )
                    
                if 'model' in results and model_name.lower() == 'rf':
                    self.plot_feature_importance(
                        results['model'],
                        results.get('feature_names', [f'Feature_{i}' for i in range(len(results['model'].feature_importances_))])
                    )
        
        print(f"Visualizations saved in {self.output_dir}/")
