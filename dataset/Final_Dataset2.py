import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import uuid

# Initialize faker
fake = Faker()

# Constants
COMPANIES = ["LogiTech Shipping", "FastTrack Logistics", "EcoTrans", "GlobalMove", 
             "Prime Carriers", "Express Freight", "Delta Logistics", "BlueSky Transport",
             "Rapid Shipping", "GreenLine Carriers"]

GOODS_TYPES = {
    "Garments": {"temp_range": (15, 25), "compatibility": ["Footwear", "Accessories", "Textiles"]},
    "Footwear": {"temp_range": (15, 25), "compatibility": ["Garments", "Accessories", "Textiles"]},
    "Electronics": {"temp_range": (10, 30), "compatibility": ["Appliances", "Accessories"]},
    "Pharmaceuticals": {"temp_range": (2, 8), "compatibility": ["Medical Supplies"]},
    "Frozen Food": {"temp_range": (-25, -15), "compatibility": ["Refrigerated Food"]},
    "Refrigerated Food": {"temp_range": (0, 5), "compatibility": ["Frozen Food"]},
    "Dry Food": {"temp_range": (10, 25), "compatibility": ["Beverages", "Packaged Goods"]},
    "Beverages": {"temp_range": (5, 25), "compatibility": ["Dry Food", "Packaged Goods"]},
    "Furniture": {"temp_range": (10, 35), "compatibility": ["Home Decor", "Building Materials"]},
    "Automotive Parts": {"temp_range": (0, 35), "compatibility": ["Industrial Equipment", "Machinery"]},
    "Medical Supplies": {"temp_range": (2, 25), "compatibility": ["Pharmaceuticals"]},
    "Hazardous Materials": {"temp_range": (5, 30), "compatibility": []},
    "Building Materials": {"temp_range": (0, 40), "compatibility": ["Furniture", "Home Decor"]},
    "Industrial Equipment": {"temp_range": (0, 40), "compatibility": ["Machinery", "Automotive Parts"]},
    "Textiles": {"temp_range": (15, 30), "compatibility": ["Garments", "Accessories"]},
    "Accessories": {"temp_range": (15, 30), "compatibility": ["Garments", "Footwear", "Textiles"]},
    "Machinery": {"temp_range": (0, 40), "compatibility": ["Industrial Equipment", "Automotive Parts"]},
    "Packaged Goods": {"temp_range": (10, 25), "compatibility": ["Dry Food", "Beverages"]},
    "Home Decor": {"temp_range": (10, 35), "compatibility": ["Furniture", "Building Materials"]},
    "Appliances": {"temp_range": (10, 35), "compatibility": ["Electronics"]}
}

# Replace real cities with fictional ones
CITIES = [
    "Azureville", "Meadowbrook", "Ironridge", "Sunhaven", "Crystalpoint", "Pinecrest", 
    "Riverdale", "Cobalt Bay", "Oakvale", "Silvertown", "Greenfield", "Stormhold", 
    "Westport", "Northridge", "Lakeview", "Elmshadow", "Goldengate",
    "Maplewood", "Mountainpeak", "Bayside", "Frostholm", "Harmony Hills", "Seaside", 
    "Cedarville", "Starlight", "Willowbrook", "Sandstone", "Mistyridge", "Emberfall"
]

# Generate coordinates for fictional cities (similar latitude/longitude ranges as original)
CITY_COORDINATES = {
    "Azureville": (40.8123, -74.1060),
    "Meadowbrook": (34.1522, -118.3437),
    "Ironridge": (41.9781, -87.7298),
    "Sunhaven": (29.8604, -95.4698),
    "Crystalpoint": (33.5484, -112.1740),
    "Pinecrest": (39.8526, -75.2652),
    "Riverdale": (29.5241, -98.5936),
    "Cobalt Bay": (32.8157, -117.2611),
    "Oakvale": (32.6767, -96.8970),
    "Silvertown": (37.4382, -121.9863),
    "Greenfield": (30.3672, -97.8431),
    "Stormhold": (30.4322, -81.7557),
    "Westport": (32.8555, -97.4308),
    "Northridge": (39.8612, -83.0988),
    "Lakeview": (39.6684, -86.2581),
    "Elmshadow": (35.3271, -80.9431),
    "Goldengate": (37.8749, -122.5194),
    "Maplewood": (47.7062, -122.4321),
    "Mountainpeak": (39.8392, -105.0903),
    "Bayside": (38.8072, -77.1369),
    "Frostholm": (42.4601, -71.1589),
    "Harmony Hills": (36.2627, -86.8816),
    "Seaside": (39.3904, -76.7122),
    "Cedarville": (45.6051, -122.7750),
    "Starlight": (36.2699, -115.2398),
    "Willowbrook": (43.1389, -88.0065),
    "Sandstone": (35.1844, -106.7504),
    "Mistyridge": (32.3226, -110.8747),
    "Emberfall": (36.8378, -119.8871)
}

# Truck types and their capacities
TRUCK_TYPES = {
    "Small Van": {"capacity": 100, "min_temp": -5, "max_temp": 30},
    "Medium Truck": {"capacity": 250, "min_temp": -10, "max_temp": 35},
    "Large Truck": {"capacity": 500, "min_temp": -15, "max_temp": 40},
    "Refrigerated Small": {"capacity": 80, "min_temp": -30, "max_temp": 10},
    "Refrigerated Medium": {"capacity": 200, "min_temp": -30, "max_temp": 10},
    "Refrigerated Large": {"capacity": 400, "min_temp": -30, "max_temp": 10},
    "Flatbed": {"capacity": 450, "min_temp": -5, "max_temp": 45},
    "Tanker": {"capacity": 350, "min_temp": -5, "max_temp": 35}
}

# Priority levels
PRIORITY_LEVELS = ["Low", "Medium", "High"]

def generate_enhanced_dataset(num_rows=25000):
    """
    Generate an enhanced dataset for cargo sharing with specified columns
    """
    data = []
    
    # Set a reference date for shipment timestamps
    reference_date = datetime.now()
    
    for i in range(num_rows):
        # Generate a timestamp within the last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        timestamp = reference_date - timedelta(days=days_ago, hours=hours_ago)
        
        # Select company
        company = random.choice(COMPANIES)
        
        # Select goods type and get temperature requirements
        goods_type = random.choice(list(GOODS_TYPES.keys()))
        temp_min, temp_max = GOODS_TYPES[goods_type]["temp_range"]
        
        # Select source and destination cities
        source = random.choice(CITIES)
        possible_destinations = [city for city in CITIES if city != source]
        destination = random.choice(possible_destinations)
        
        # Get coordinates
        source_lat, source_lon = CITY_COORDINATES[source]
        dest_lat, dest_lon = CITY_COORDINATES[destination]
        
        # Calculate straight-line distance between cities
        distance_km = np.sqrt(
            (dest_lat - source_lat)**2 + (dest_lon - source_lon)**2
        ) * 111  # Rough conversion to km
        
        # Generate units (number of items)
        units = random.randint(1, 50)
        
        # Calculate volume and weight based on units
        volume_per_unit = random.uniform(0.5, 2.0)
        weight_per_unit = random.uniform(5, 20)
        total_volume = units * volume_per_unit
        total_weight = units * weight_per_unit
        
        # Select appropriate truck type based on volume and temperature
        eligible_trucks = [
            truck_type for truck_type, specs in TRUCK_TYPES.items()
            if (specs["capacity"] >= total_volume and 
                specs["min_temp"] <= temp_min and 
                specs["max_temp"] >= temp_max)
        ]
        
        if eligible_trucks:
            truck_type = random.choice(eligible_trucks)
        else:
            # If no eligible truck, choose the largest capacity that matches temperature
            temp_compatible_trucks = [
                truck_type for truck_type, specs in TRUCK_TYPES.items()
                if (specs["min_temp"] <= temp_min and specs["max_temp"] >= temp_max)
            ]
            
            if temp_compatible_trucks:
                truck_type = max(temp_compatible_trucks, 
                                key=lambda t: TRUCK_TYPES[t]["capacity"])
            else:
                # If still no match, just pick a truck type
                truck_type = random.choice(list(TRUCK_TYPES.keys()))
        
        # Get truck capacity as integer
        truck_capacity = int(TRUCK_TYPES[truck_type]["capacity"])
        
        # Calculate storage left in the truck
        storage_left = float(truck_capacity - total_volume)
        
        # Generate priority level
        priority = random.choice(PRIORITY_LEVELS)
        
        # Generate shipment ID
        shipment_id = f"SHIP-{i+1000:04d}"
        
        # Calculate estimated time of arrival
        # Base travel time: 1 hour per 80 km
        base_travel_hours = distance_km / 80
        
        # Add random variations for traffic, stops, etc.
        travel_variation = random.uniform(0.8, 1.5)
        total_travel_hours = base_travel_hours * travel_variation
        
        # Calculate ETA and scheduled delivery time
        eta = timestamp + timedelta(hours=total_travel_hours)
        scheduled_delivery_time = eta + timedelta(hours=random.randint(6, 48))
        
        # Calculate carbon footprint per km (larger trucks have higher footprint)
        base_carbon = 0.8 + (TRUCK_TYPES[truck_type]["capacity"] / 500) * 0.7
        carbon_footprint = base_carbon * (1 + random.uniform(-0.2, 0.2))
        
        # Calculate total carbon emissions for the trip
        total_emissions = carbon_footprint * distance_km
        
        # Generate historical shared success (frequency of successful shared transportation)
        historical_shared_success = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.2, 0.3, 0.2, 0.15, 0.1, 0.05])
        
        # Calculate capacity available (same as storage_left but with a different name)
        capacity_available = float(storage_left)
        
        # Create row with specified columns and data types
        row = {
            "shipment_id": shipment_id,                                      # object
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),            # object
            "company": company,                                              # object
            "goods_type": goods_type,                                        # object
            "source": source,                                                # object
            "destination": destination,                                      # object
            "units": int(units),                                             # int64
            "truck_type": truck_type,                                        # object
            "storage_left": float(storage_left),                             # float64
            "source_lat": float(source_lat),                                 # float64
            "source_lon": float(source_lon),                                 # float64
            "dest_lat": float(dest_lat),                                     # float64
            "dest_lon": float(dest_lon),                                     # float64
            "temp_min": int(temp_min),                                       # int64
            "temp_max": int(temp_max),                                       # int64
            "total_volume": float(total_volume),                             # float64
            "total_weight": float(total_weight),                             # float64
            "distance_km": float(distance_km),                               # float64
            "eta": eta.strftime("%Y-%m-%d %H:%M:%S"),                        # object
            "priority": priority,                                            # object
            "carbon_footprint_per_km": float(carbon_footprint),              # float64
            "total_emissions": float(total_emissions),                       # float64
            "historical_shared_success": int(historical_shared_success),     # int64
            "scheduled_delivery_time": scheduled_delivery_time.strftime("%Y-%m-%d %H:%M:%S"), # object
            "truck_capacity": int(truck_capacity),                           # int64
            "capacity_available": float(capacity_available)                  # float64
        }
        
        data.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Create compatibility matrix for goods types
    goods_compatibility = {}
    for gtype in GOODS_TYPES:
        compatibles = GOODS_TYPES[gtype]["compatibility"]
        goods_compatibility[gtype] = {other: 1 if other in compatibles else 0 for other in GOODS_TYPES}
    
    return df, goods_compatibility

if __name__ == "__main__":
    # Generate dataset
    df, compatibility = generate_enhanced_dataset(25000)
    
    # Save to CSV
    df.to_csv('cargo_sharing_dataset.csv', index=False)
    
    # Print column information
    print(f"Dataset created with {len(df)} rows")
    print("\nColumn information:")
    for col in df.columns:
        print(f"- {col}: {df[col].dtype}")
    
    print("\nSample data:")
    print(df.head(3))
    
    # Print some statistics
    print("\nStorage left statistics:")
    print(f"Average storage left: {df['storage_left'].mean():.2f} units")
    print(f"Percentage of trailers with >50 units left: {(df['storage_left'] > 50).mean()*100:.2f}%")
    
    print("\nGoods type distribution:")
    print(df['goods_type'].value_counts().head())