# WiFi Signal Strength Prediction

This project implements machine learning models to predict WiFi signal strength across multiple departments in complex environments. It uses various ML approaches including KNN, SVM, and ensemble methods to provide accurate signal strength predictions.

## Features
- Multi-model approach (KNN, SVM) for signal strength prediction
- Real-time signal strength data collection
- Feature engineering for WiFi metrics (RSSI, SNR)
- Model evaluation and comparison framework
- Support for multiple access points

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure
- `src/`
  - `data_collection/`: Scripts for collecting WiFi signal data
  - `preprocessing/`: Data cleaning and feature engineering
  - `models/`: Implementation of ML models
  - `utils/`: Utility functions and helpers
- `config/`: Configuration files
- `notebooks/`: Jupyter notebooks for analysis
- `tests/`: Unit tests

## Usage
1. Configure data collection parameters in `config/config.yaml`
2. Run data collection:
```bash
python src/data_collection/collector.py
```
3. Train models:
```bash
python src/models/train.py
```
4. Make predictions:
```bash
python src/models/predict.py
```

## Contributing
Contributions are welcome! Please read the contributing guidelines before making any changes.

## License
MIT License
