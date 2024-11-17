import subprocess
import re
import time
import pandas as pd
from datetime import datetime
import json
import os
import numpy as np
import random

class WiFiDataCollector:
    def __init__(self, output_dir="data", simulation_mode=True):
        """Initialize the WiFi data collector.
        
        Args:
            output_dir (str): Directory to store collected data
            simulation_mode (bool): If True, generate synthetic data instead of real measurements
        """
        self.output_dir = output_dir
        self.simulation_mode = simulation_mode
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Simulation parameters
        self.simulated_aps = [
            {
                'ssid': 'AP_Floor1_Room101',
                'bssid': '00:11:22:33:44:55',
                'base_rssi': -45,
                'channel': '36',
                'security': 'WPA2'
            },
            {
                'ssid': 'AP_Floor1_Room102',
                'bssid': '00:11:22:33:44:56',
                'base_rssi': -55,
                'channel': '40',
                'security': 'WPA2'
            },
            {
                'ssid': 'AP_Floor2_Room201',
                'bssid': '00:11:22:33:44:57',
                'base_rssi': -65,
                'channel': '44',
                'security': 'WPA2'
            }
        ]
    
    def generate_synthetic_data(self):
        """Generate synthetic WiFi data for simulation purposes."""
        networks = []
        
        for ap in self.simulated_aps:
            # Add random variation to RSSI
            rssi_variation = np.random.normal(0, 3)  # 3 dB standard deviation
            rssi = ap['base_rssi'] + rssi_variation
            
            network = {
                'ssid': ap['ssid'],
                'bssid': ap['bssid'],
                'rssi': int(rssi),
                'channel': ap['channel'],
                'security': ap['security']
            }
            networks.append(network)
            
        return networks
    
    def get_wifi_info(self):
        """Collect WiFi information."""
        if self.simulation_mode:
            return self.generate_synthetic_data()
            
        try:
            # Note: Real data collection requires elevated privileges
            # This is left as a placeholder for systems where it's possible
            cmd = ["wdutil", "info"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            
            if error:
                print(f"Error running wdutil: {error.decode()}")
                return None
                
            return self.parse_wifi_data(output.decode())
        except Exception as e:
            print(f"Error collecting WiFi data: {e}")
            return None

    def parse_wifi_data(self, raw_data):
        """Parse raw WiFi data into structured format.
        
        Args:
            raw_data (str): Raw output from wdutil command
            
        Returns:
            list: List of dictionaries containing WiFi information
        """
        if not raw_data:
            return []

        try:
            # Split the output into sections
            sections = raw_data.split('\n\n')
            
            # Find the WiFi scan results section
            scan_section = None
            for section in sections:
                if 'Scan Results:' in section or 'Available Networks:' in section:
                    scan_section = section
                    break
            
            if not scan_section:
                return []
            
            networks = []
            current_network = {}
            
            # Parse the scan results
            for line in scan_section.split('\n'):
                line = line.strip()
                if not line:
                    if current_network:
                        networks.append(current_network)
                        current_network = {}
                    continue
                
                # Try to extract key-value pairs
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if key == 'ssid':
                        if current_network:
                            networks.append(current_network)
                        current_network = {'ssid': value}
                    elif key == 'bssid':
                        current_network['bssid'] = value
                    elif key == 'rssi':
                        try:
                            current_network['rssi'] = int(value.split()[0])
                        except (ValueError, IndexError):
                            continue
                    elif key == 'channel':
                        current_network['channel'] = value
                    elif key == 'security':
                        current_network['security'] = value
            
            # Add the last network if exists
            if current_network:
                networks.append(current_network)
            
            return networks
            
        except Exception as e:
            print(f"Error parsing WiFi data: {e}")
            return []

    def collect_data(self, duration_seconds=60, interval_seconds=1):
        """Collect WiFi data over a specified duration.
        
        Args:
            duration_seconds (int): How long to collect data
            interval_seconds (int): Interval between measurements
            
        Returns:
            pd.DataFrame: Collected WiFi data
        """
        all_data = []
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            networks = self.get_wifi_info()
            if networks:
                timestamp = datetime.now()
                for network in networks:
                    network['timestamp'] = timestamp
                all_data.extend(networks)
            time.sleep(interval_seconds)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        if len(df) > 0:
            # Save data
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"wifi_data_{timestamp_str}.csv")
            df.to_csv(filename, index=False)
            print(f"Data saved to {filename}")
        
        return df

if __name__ == "__main__":
    collector = WiFiDataCollector(simulation_mode=True)
    print("Starting WiFi data collection (simulation mode)...")
    data = collector.collect_data(duration_seconds=60)
    print(f"Collected {len(data)} data points")
    print("\nSample of collected data:")
    print(data.head())
