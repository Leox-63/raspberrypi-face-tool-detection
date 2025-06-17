"""
LwM2M Standard Objects Implementation
"""
import logging
import math
import random
import time
from typing import Dict, Any
from datetime import datetime


class LwM2MObject:
    """Base class for LwM2M objects."""
    
    def __init__(self, object_id: int, name: str = None):
        self.object_id = object_id
        self.name = name or f"Object{object_id}"
        self.instances: Dict[int, Dict[int, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.resource_definitions = {}  # Resource ID -> metadata
    
    def get_available_resources(self, instance_id: int = 0) -> list:
        """Get list of available resource IDs for an instance."""
        if instance_id in self.instances:
            return list(self.instances[instance_id].keys())
        return []
    
    def get_resource_metadata(self, resource_id: int) -> dict:
        """Get metadata for a resource."""
        return self.resource_definitions.get(resource_id, {})
    
    def read_resource(self, instance_id: int, resource_id: int) -> Any:
        """Read a resource value."""
        if instance_id in self.instances:
            return self.instances[instance_id].get(resource_id)
        return None
    
    def write_resource(self, instance_id: int, resource_id: int, value: Any) -> bool:
        """Write a resource value."""
        if instance_id not in self.instances:
            self.instances[instance_id] = {}
        
        self.instances[instance_id][resource_id] = value
        return True
    
    def update_simulated_data(self):
        """Update simulated data for dynamic objects. Override in subclasses."""
        pass


class SecurityObject(LwM2MObject):
    """LwM2M Security Object (Object ID: 0)."""
    
    def __init__(self, config):
        super().__init__(0, "Security")
        self.config = config
        
        # Define resource metadata
        self.resource_definitions = {
            0: {"name": "LwM2M Server URI", "type": "string", "operations": "R"},
            1: {"name": "Bootstrap Server", "type": "boolean", "operations": "R"},
            2: {"name": "Security Mode", "type": "integer", "operations": "R"},
            10: {"name": "Short Server ID", "type": "integer", "operations": "R"},
        }
        
        # Create default security instance
        self.instances[0] = {
            0: config.server_uri,      # LwM2M Server URI
            1: False,                  # Bootstrap Server
            2: 3,                      # Security Mode (No Security)
            10: 1,                     # Short Server ID
        }


class DeviceObject(LwM2MObject):
    """LwM2M Device Object (Object ID: 3)."""
    
    def __init__(self):
        super().__init__(3, "Device")
        
        # Define resource metadata
        self.resource_definitions = {
            0: {"name": "Manufacturer", "type": "string", "operations": "R"},
            1: {"name": "Model Number", "type": "string", "operations": "R"},
            2: {"name": "Serial Number", "type": "string", "operations": "R"},
            3: {"name": "Firmware Version", "type": "string", "operations": "R"},
            9: {"name": "Battery Level", "type": "integer", "operations": "R", "units": "%"},
            10: {"name": "Memory Free", "type": "integer", "operations": "R", "units": "KB"},
            11: {"name": "Error Code", "type": "integer", "operations": "R"},
            13: {"name": "Current Time", "type": "time", "operations": "RW"},
            16: {"name": "Binding Mode", "type": "string", "operations": "R"},
        }
        
        # Create default device instance
        self.instances[0] = {
            0: "Python LwM2M Client",     # Manufacturer
            1: "PyLwM2M-v1.0",            # Model Number
            2: "001",                      # Serial Number
            3: "1.0.0",                    # Firmware Version
            9: 100,                        # Battery Level (%)
            10: 512000,                    # Memory Free (KB)
            11: 0,                         # Error Code
            13: datetime.now(),            # Current Time
            16: "U",                       # Binding Mode
        }
    
    def read_resource(self, instance_id: int, resource_id: int) -> Any:
        """Read device resource with dynamic values."""
        # Update dynamic resources
        if resource_id == 13:  # Current Time
            self.instances[0][13] = datetime.now()
        elif resource_id == 9:  # Battery Level (simulate drain)
            current = self.instances[0].get(9, 100)
            # Simulate slow battery drain
            self.instances[0][9] = max(20, current - random.uniform(0, 0.1))
        
        return super().read_resource(instance_id, resource_id)
    
    def update_simulated_data(self):
        """Update simulated device data."""
        # Update current time
        self.instances[0][13] = datetime.now()
        
        # Simulate battery drain
        current_battery = self.instances[0].get(9, 100)
        drain = random.uniform(0, 0.1)  # Slow battery drain
        new_battery = max(20, current_battery - drain)  # Don't go below 20%
        self.instances[0][9] = int(new_battery)
        
        # Simulate memory usage variation
        base_memory = 512000
        variation = random.randint(-50000, 10000)  # Memory can decrease with usage
        new_memory = max(100000, base_memory + variation)  # Don't go below 100MB
        self.instances[0][10] = new_memory
        
        # self.logger.debug(f"Device updated: Battery {new_battery}%, Memory {new_memory//1000}MB")


class TemperatureObject(LwM2MObject):
    """LwM2M Temperature Sensor Object (Object ID: 3303) - IPSO Smart Object."""
    
    def __init__(self):
        super().__init__(3303, "Temperature")
        self.base_temp = 22.0  # Base temperature in Celsius
        
        # Define resource metadata for IPSO Temperature Sensor (IPSO Alliance v1.1)
        self.resource_definitions = {
            5700: {"name": "Sensor Value", "type": "float", "operations": "R", "units": "Cel", "mandatory": True},
            5701: {"name": "Sensor Units", "type": "string", "operations": "R", "mandatory": False},
            5601: {"name": "Min Measured Value", "type": "float", "operations": "R", "units": "Cel", "mandatory": False},
            5602: {"name": "Max Measured Value", "type": "float", "operations": "R", "units": "Cel", "mandatory": False},
            5603: {"name": "Min Range Value", "type": "float", "operations": "R", "units": "Cel", "mandatory": False},
            5604: {"name": "Max Range Value", "type": "float", "operations": "R", "units": "Cel", "mandatory": False},
            5605: {"name": "Reset Min and Max Measured Values", "type": "none", "operations": "E", "mandatory": False},
            5750: {"name": "Application Type", "type": "string", "operations": "RW", "mandatory": False},
        }
        
        # Create temperature sensor instance with all mandatory and common optional resources
        self.instances[0] = {
            5700: self.base_temp,          # Sensor Value (MANDATORY)
            5701: "Cel",                   # Sensor Units (recommended for proper display)
            5601: 18.0,                    # Min Measured Value
            5602: 28.0,                    # Max Measured Value
            5603: -40.0,                   # Min Range Value (sensor capability)
            5604: 85.0,                    # Max Range Value (sensor capability)
            5750: "Temperature Sensor",    # Application Type
        }
    
    def read_resource(self, instance_id: int, resource_id: int) -> Any:
        """Read temperature with realistic simulation."""
        if resource_id == 5700:  # Sensor Value
            # Simulate realistic temperature variation
            time_factor = time.time() / 3600  # Hour-based cycle
            daily_variation = math.sin(time_factor * 2 * math.pi / 24) * 5  # ±5°C daily
            noise = random.gauss(0, 0.5)  # Small random noise
            
            new_temp = self.base_temp + daily_variation + noise
            new_temp = round(new_temp, 1)
            
            self.instances[0][5700] = new_temp
            
            # Update min/max if needed
            current_min = self.instances[0].get(5601, new_temp)
            current_max = self.instances[0].get(5602, new_temp)
            
            if new_temp < current_min:
                self.instances[0][5601] = new_temp
            if new_temp > current_max:
                self.instances[0][5602] = new_temp
        
        return super().read_resource(instance_id, resource_id)
    
    def update_simulated_data(self):
        """Update simulated temperature data."""
        # Simulate realistic temperature variation
        time_factor = time.time() / 3600  # Hour-based cycle
        daily_variation = math.sin(time_factor * 2 * math.pi / 24) * 5  # ±5°C daily
        noise = random.gauss(0, 0.5)  # Small random noise
        
        new_temp = self.base_temp + daily_variation + noise
        new_temp = round(new_temp, 1)
        
        self.instances[0][5700] = new_temp
        
        # Update min/max if needed
        current_min = self.instances[0].get(5601, new_temp)
        current_max = self.instances[0].get(5602, new_temp)
        
        if new_temp < current_min:
            self.instances[0][5601] = new_temp
        if new_temp > current_max:
            self.instances[0][5602] = new_temp
            
        # self.logger.debug(f"Temperature updated: {new_temp}°C")


class LocationObject(LwM2MObject):
    """LwM2M Location Object (Object ID: 6)."""
    
    def __init__(self):
        super().__init__(6, "Location")
        
        # Define resource metadata
        self.resource_definitions = {
            0: {"name": "Latitude", "type": "float", "operations": "R", "units": "lat"},
            1: {"name": "Longitude", "type": "float", "operations": "R", "units": "lon"},
            2: {"name": "Altitude", "type": "float", "operations": "R", "units": "m"},
            5: {"name": "Timestamp", "type": "integer", "operations": "R", "units": "s"},
        }
        
        # Simulated location (example: Madrid, Spain area)
        self.base_lat = 40.4168
        self.base_lon = -3.7038
        
        self.instances[0] = {
            0: self.base_lat,              # Latitude
            1: self.base_lon,              # Longitude
            2: 650.0,                      # Altitude (meters)
            3: 10.0,                       # Radius (uncertainty in meters)
            5: int(time.time()),           # Timestamp
            6: 2.5,                        # Speed (m/s)
        }
    
    def read_resource(self, instance_id: int, resource_id: int) -> Any:
        """Read location with slight movement simulation."""
        if resource_id in [0, 1]:  # Latitude or Longitude
            # Simulate small GPS drift (±0.0001 degrees ≈ ±10 meters)
            drift = random.gauss(0, 0.0001)
            
            if resource_id == 0:  # Latitude
                new_lat = self.base_lat + drift
                self.instances[0][0] = round(new_lat, 6)
            else:  # Longitude
                new_lon = self.base_lon + drift
                self.instances[0][1] = round(new_lon, 6)
        
        elif resource_id == 5:  # Timestamp
            self.instances[0][5] = int(time.time())
        
        return super().read_resource(instance_id, resource_id)
    
    def update_simulated_data(self):
        """Update simulated location data with GPS drift."""
        # Simulate small GPS drift (±0.0001 degrees ≈ ±10 meters)
        lat_drift = random.gauss(0, 0.0001)
        lon_drift = random.gauss(0, 0.0001)
        
        new_lat = self.base_lat + lat_drift
        new_lon = self.base_lon + lon_drift
        
        self.instances[0][0] = round(new_lat, 6)  # Latitude
        self.instances[0][1] = round(new_lon, 6)  # Longitude
        self.instances[0][5] = int(time.time())   # Timestamp
        
        self.logger.debug(f"Location updated: {new_lat:.6f}, {new_lon:.6f}")


class ConnectivityMonitoringObject(LwM2MObject):
    """LwM2M Connectivity Monitoring Object (Object ID: 4)."""
    
    def __init__(self):
        super().__init__(4, "Connectivity Monitoring")
        
        # Define resource metadata
        self.resource_definitions = {
            0: {"name": "Network Bearer", "type": "integer", "operations": "R"},
            1: {"name": "Available Network Bearer", "type": "integer", "operations": "R", "multiple": True},
            2: {"name": "Radio Signal Strength", "type": "integer", "operations": "R", "units": "dBm"},
            4: {"name": "IP Addresses", "type": "string", "operations": "R", "multiple": True},
            5: {"name": "Router IP Addresses", "type": "string", "operations": "R", "multiple": True},
            8: {"name": "Cell ID", "type": "integer", "operations": "R"},
            9: {"name": "SMNC", "type": "integer", "operations": "R"},
            10: {"name": "SMCC", "type": "integer", "operations": "R"},
            11: {"name": "Link Quality", "type": "integer", "operations": "R", "units": "%"},
            12: {"name": "Link Utilization", "type": "integer", "operations": "R", "units": "%"},
        }
        
        self.instances[0] = {
            0: 1,                          # Network Bearer (Ethernet)
            1: [50, 75, 90],              # Available Network Bearer
            2: -45,                        # Radio Signal Strength (dBm)
            4: ["192.168.0.100"],         # IP Addresses
            5: ["router.local"],           # Router IP Addresses
            8: 6,                          # Cell ID
            9: 0,                          # SMNC
            10: 0,                         # SMCC
            11: 95,                        # Link Quality (%)
            12: 1,                         # Link Utilization (%)
        }
    
    def read_resource(self, instance_id: int, resource_id: int) -> Any:
        """Read connectivity with dynamic signal simulation."""
        if resource_id == 2:  # Radio Signal Strength
            # Simulate signal strength variation
            base_signal = -45
            variation = random.gauss(0, 5)  # ±5 dBm variation
            new_signal = int(base_signal + variation)
            self.instances[0][2] = max(-100, min(-20, new_signal))
        
        elif resource_id == 11:  # Link Quality
            # Link quality based on signal strength
            signal = self.instances[0].get(2, -45)
            quality = max(0, min(100, int(100 + (signal + 30) * 2)))
            self.instances[0][11] = quality
        
        return super().read_resource(instance_id, resource_id)
    
    def update_simulated_data(self):
        """Update simulated connectivity data."""
        # Update signal strength
        base_signal = -45
        variation = random.gauss(0, 5)  # ±5 dBm variation
        new_signal = int(base_signal + variation)
        self.instances[0][2] = max(-100, min(-20, new_signal))
        
        # Update link quality based on signal strength
        signal = self.instances[0][2]
        quality = max(0, min(100, int(100 + (signal + 30) * 2)))
        self.instances[0][11] = quality
        
        # Simulate link utilization
        utilization = random.randint(1, 15)  # 1-15% utilization
        self.instances[0][12] = utilization
        
        self.logger.debug(f"Connectivity updated: Signal {signal}dBm, Quality {quality}%")


class HumidityObject(LwM2MObject):
    """LwM2M Humidity Sensor Object (Object ID: 3304) - IPSO Smart Object."""
    
    def __init__(self):
        super().__init__(3304, "Humidity")
        self.base_humidity = 45.0  # Base humidity in %
        
        # Define resource metadata for IPSO Humidity Sensor (IPSO Alliance v1.1)
        self.resource_definitions = {
            5700: {"name": "Sensor Value", "type": "float", "operations": "R", "units": "%RH", "mandatory": True},
            5701: {"name": "Sensor Units", "type": "string", "operations": "R", "mandatory": False},
            5601: {"name": "Min Measured Value", "type": "float", "operations": "R", "units": "%RH", "mandatory": False},
            5602: {"name": "Max Measured Value", "type": "float", "operations": "R", "units": "%RH", "mandatory": False},
            5603: {"name": "Min Range Value", "type": "float", "operations": "R", "units": "%RH", "mandatory": False},
            5604: {"name": "Max Range Value", "type": "float", "operations": "R", "units": "%RH", "mandatory": False},
            5605: {"name": "Reset Min and Max Measured Values", "type": "none", "operations": "E", "mandatory": False},
            5750: {"name": "Application Type", "type": "string", "operations": "RW", "mandatory": False},
        }
        
        # Create humidity sensor instance with correct units and application type
        self.instances[0] = {
            5700: self.base_humidity,      # Sensor Value (MANDATORY)
            5701: "%RH",                   # Sensor Units (% Relative Humidity)
            5601: 30.0,                    # Min Measured Value
            5602: 80.0,                    # Max Measured Value
            5603: 0.0,                     # Min Range Value
            5604: 100.0,                   # Max Range Value
            5750: "Humidity Sensor",       # Application Type
        }
    
    def update_simulated_data(self):
        """Update simulated humidity data."""
        # Simulate realistic humidity variation (complementary to temperature)
        time_factor = time.time() / 3600  # Hour-based cycle
        # Humidity typically inversely correlates with temperature
        daily_variation = -math.sin(time_factor * 2 * math.pi / 24) * 15  # ±15% daily variation
        noise = random.gauss(0, 2.0)  # Random noise
        
        new_humidity = self.base_humidity + daily_variation + noise
        new_humidity = max(20.0, min(90.0, new_humidity))  # Clamp between 20-90%
        new_humidity = round(new_humidity, 1)
        
        self.instances[0][5700] = new_humidity
        
        # Update min/max if needed
        current_min = self.instances[0].get(5601, new_humidity)
        current_max = self.instances[0].get(5602, new_humidity)
        
        if new_humidity < current_min:
            self.instances[0][5601] = new_humidity
        if new_humidity > current_max:
            self.instances[0][5602] = new_humidity
            
        # self.logger.debug(f"Humidity updated: {new_humidity}%RH")

    def read_resource(self, instance_id: int, resource_id: int) -> Any:
        """Read humidity resource with dynamic data generation."""
        # Update the sensor value when read
        if resource_id == 5700:  # Sensor Value
            # Simulate realistic humidity variation (complementary to temperature)
            time_factor = time.time() / 3600  # Hour-based cycle
            # Humidity typically inversely correlates with temperature
            daily_variation = -math.sin(time_factor * 2 * math.pi / 24) * 15  # ±15% daily variation
            noise = random.gauss(0, 2.0)  # Random noise
            
            new_humidity = self.base_humidity + daily_variation + noise
            new_humidity = max(20.0, min(90.0, new_humidity))  # Clamp between 20-90%
            new_humidity = round(new_humidity, 1)
            
            self.instances[0][5700] = new_humidity
            
            # Update min/max if needed
            current_min = self.instances[0].get(5601, new_humidity)
            current_max = self.instances[0].get(5602, new_humidity)
            
            if new_humidity < current_min:
                self.instances[0][5601] = new_humidity
            if new_humidity > current_max:
                self.instances[0][5602] = new_humidity
        
        return super().read_resource(instance_id, resource_id)