# WiFi Signal Strength Prediction System

A machine learning-based system for predicting and visualizing WiFi signal strength across multiple departments in a building. This project combines data collection, machine learning, and visualization to help optimize WiFi network coverage and performance.

## Features

### Data Collection
- Simulated WiFi signal data generation for development and testing
- Support for real WiFi data collection (requires elevated privileges)
- Captures key metrics:
  - SSID (Network name)
  - BSSID (Access Point MAC address)
  - RSSI (Signal strength)
  - Channel information
  - Security settings

### Data Preprocessing
- Feature engineering for WiFi signal data
- Time-based feature extraction
- Categorical encoding for network attributes
- Signal quality metrics calculation
- Data normalization and scaling

### Machine Learning Models
- Multiple model implementations:
  - K-Nearest Neighbors (KNN)
  - Support Vector Regression (SVR)
  - Random Forest Regression
- Model evaluation metrics:
  - Mean Squared Error (MSE)
  - Root Mean Squared Error (RMSE)
  - R² Score
- Cross-validation support
- Model persistence for later use

### Visualization
- Signal strength visualizations:
  - Signal strength heatmaps
  - Signal strength over time
  - Signal distribution analysis
  - Model predictions vs actual values
  - Feature importance plots
- Building layout visualizations:
  - Floor plan signal coverage mapping
  - Individual AP coverage visualization
  - Combined coverage analysis
  - 3D signal strength mapping
  - Coverage radius indicators

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/wifi-signal-prediction.git
cd wifi-signal-prediction
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Data Collection and Model Training
```bash
# Collect new data and train models
python src/main.py --collect --duration 60 --interval 1 --train

# Use existing data file
python src/main.py --data-file path/to/data.csv --train

# Generate visualizations
python src/main.py --collect --train --visualize

# Create building layout visualizations
python src/main.py --building-layout
```

### Command-line Arguments
- `--collect`: Collect new WiFi signal data
- `--duration`: Duration to collect data (minutes)
- `--interval`: Interval between measurements (seconds)
- `--train`: Train machine learning models
- `--data-file`: Path to existing data file
- `--visualize`: Create data and model visualizations
- `--building-layout`: Create building layout visualizations

## Project Structure
```
wifi/
├── requirements.txt      # Project dependencies
├── README.md            # Project documentation
└── src/
    ├── data_collection/ # WiFi data collection module
    │   └── collector.py
    ├── preprocessing/   # Data preprocessing module
    │   └── preprocessor.py
    ├── models/         # ML models implementation
    │   └── wifi_models.py
    ├── visualization/  # Visualization modules
    │   ├── visualizer.py
    │   └── building_visualizer.py
    └── main.py         # Main execution script
```

## Development

### Adding New Models
To add a new machine learning model:
1. Add the model class in `src/models/wifi_models.py`
2. Implement required methods: `train`, `predict`, `evaluate`
3. Add model to the training pipeline in `main.py`

### Customizing Visualizations
- Modify `src/visualization/visualizer.py` for data visualizations
- Adjust `src/visualization/building_visualizer.py` for layout visualizations
- Configure visualization parameters in respective modules

### Real Data Collection
For real WiFi data collection:
1. Set `simulation_mode=False` in `WiFiDataCollector`
2. Run with appropriate permissions
3. Configure data collection parameters as needed

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Inspired by research in WiFi signal prediction and optimization
- Uses scikit-learn for machine learning implementations
- Visualization powered by matplotlib and seaborn
