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

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", 
    "Fort Worth", "Columbus", "Indianapolis", "Charlotte", "San Francisco",
    "Seattle", "Denver", "Washington", "Boston", "Nashville", "Baltimore", 
    "Portland", "Las Vegas", "Milwaukee", "Albuquerque", "Tucson", "Fresno"
]

# Generate realistic coordinates for cities
CITY_COORDINATES = {
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "Houston": (29.7604, -95.3698),
    "Phoenix": (33.4484, -112.0740),
    "Philadelphia": (39.9526, -75.1652),
    "San Antonio": (29.4241, -98.4936),
    "San Diego": (32.7157, -117.1611),
    "Dallas": (32.7767, -96.7970),
    "San Jose": (37.3382, -121.8863),
    "Austin": (30.2672, -97.7431),
    "Jacksonville": (30.3322, -81.6557),
    "Fort Worth": (32.7555, -97.3308),
    "Columbus": (39.9612, -82.9988),
    "Indianapolis": (39.7684, -86.1581),
    "Charlotte": (35.2271, -80.8431),
    "San Francisco": (37.7749, -122.4194),
    "Seattle": (47.6062, -122.3321),
    "Denver": (39.7392, -104.9903),
    "Washington": (38.9072, -77.0369),
    "Boston": (42.3601, -71.0589),
    "Nashville": (36.1627, -86.7816),
    "Baltimore": (39.2904, -76.6122),
    "Portland": (45.5051, -122.6750),
    "Las Vegas": (36.1699, -115.1398),
    "Milwaukee": (43.0389, -87.9065),
    "Albuquerque": (35.0844, -106.6504),
    "Tucson": (32.2226, -110.9747),
    "Fresno": (36.7378, -119.7871)
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