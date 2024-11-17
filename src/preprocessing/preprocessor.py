import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from datetime import datetime

class WiFiDataPreprocessor:
    def __init__(self):
        """Initialize the WiFi data preprocessor."""
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def extract_features(self, df):
        """Extract and engineer features from raw WiFi data.
        
        Args:
            df (pd.DataFrame): Raw WiFi data
            
        Returns:
            pd.DataFrame: Processed data with engineered features
        """
        # Convert timestamp to datetime if it's not already
        if isinstance(df['timestamp'].iloc[0], str):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        # Extract time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Extract channel information
        df['channel_number'] = df['channel'].str.extract(r'(\d+)').astype(float)
        
        # Convert RSSI to positive scale (optional)
        df['rssi_positive'] = df['rssi'].abs()
        
        # Calculate signal quality (example metric)
        df['signal_quality'] = (df['rssi_positive'] - df['rssi_positive'].min()) / \
                             (df['rssi_positive'].max() - df['rssi_positive'].min()) * 100
                             
        return df
    
    def encode_categorical(self, df):
        """Encode categorical variables.
        
        Args:
            df (pd.DataFrame): DataFrame with categorical variables
            
        Returns:
            pd.DataFrame: DataFrame with encoded categorical variables
        """
        categorical_columns = ['ssid', 'bssid', 'security']
        
        for col in categorical_columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col])
        
        return df
    
    def scale_features(self, df):
        """Scale numerical features.
        
        Args:
            df (pd.DataFrame): DataFrame with numerical features
            
        Returns:
            pd.DataFrame: DataFrame with scaled features
        """
        numerical_columns = ['rssi', 'channel_number', 'hour', 'minute', 
                           'day_of_week', 'rssi_positive', 'signal_quality']
        
        # Create a copy of the dataframe
        df_scaled = df.copy()
        
        # Scale numerical features
        features_to_scale = [col for col in numerical_columns if col in df.columns]
        if features_to_scale:
            df_scaled[features_to_scale] = self.scaler.fit_transform(df[features_to_scale])
        
        return df_scaled
    
    def prepare_features(self, df):
        """Prepare features for model training.
        
        Args:
            df (pd.DataFrame): Raw WiFi data
            
        Returns:
            pd.DataFrame: Processed data ready for model training
        """
        # Extract features
        df = self.extract_features(df)
        
        # Encode categorical variables
        df = self.encode_categorical(df)
        
        # Scale numerical features
        df = self.scale_features(df)
        
        return df
    
    def get_feature_names(self):
        """Get list of feature names used for model training.
        
        Returns:
            list: List of feature names
        """
        feature_names = [
            'rssi', 'channel_number', 'hour', 'minute', 'day_of_week',
            'rssi_positive', 'signal_quality'
        ]
        
        # Add encoded categorical features
        for col in self.label_encoders.keys():
            feature_names.append(f'{col}_encoded')
            
        return feature_names
