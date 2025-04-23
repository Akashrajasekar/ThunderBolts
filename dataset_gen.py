import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import uuid

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

# Generate coordinates for cities
CITY_COORDINATES = {city: (fake.latitude(), fake.longitude()) for city in CITIES}

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

def generate_shipment_data(num_shipments=100):
    shipments = []
    
    current_time = datetime.now()
    
    for _ in range(num_shipments):
        company = random.choice(COMPANIES)
        goods_type = random.choice(list(GOODS_TYPES.keys()))
        source = random.choice(CITIES)
        
        # Ensure destination is different from source
        possible_destinations = [city for city in CITIES if city != source]
        destination = random.choice(possible_destinations)
        
        goods_temp_range = GOODS_TYPES[goods_type]["temp_range"]
        
        # Choose an appropriate truck type based on goods temperature requirements
        eligible_trucks = [
            truck_type for truck_type, specs in TRUCK_TYPES.items()
            if specs["min_temp"] <= goods_temp_range[0] and specs["max_temp"] >= goods_temp_range[1]
        ]
        truck_type = random.choice(eligible_trucks if eligible_trucks else list(TRUCK_TYPES.keys()))
        
        # Calculate max capacity for this truck type
        max_capacity = TRUCK_TYPES[truck_type]["capacity"]
        
        # Generate a random units of goods between 10% and 90% of the truck's capacity
        units_of_goods = random.randint(int(max_capacity * 0.1), int(max_capacity * 0.9))
        
        # Calculate remaining storage space
        storage_left = max_capacity - units_of_goods
        
        # Generate a random timestamp within the last 7 days
        random_days = random.randint(0, 7)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        timestamp = current_time - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        
        # Generate a unique ID for the shipment
        shipment_id = str(uuid.uuid4())[:8]
        
        shipments.append({
            "shipment_id": shipment_id,
            "timestamp": timestamp,
            "company": company,
            "goods_type": goods_type,
            "source": source,
            "destination": destination,
            "units": units_of_goods,
            "truck_type": truck_type,
            "storage_left": storage_left,
            "source_lat": CITY_COORDINATES[source][0],
            "source_lon": CITY_COORDINATES[source][1],
            "dest_lat": CITY_COORDINATES[destination][0],
            "dest_lon": CITY_COORDINATES[destination][1],
            "temp_min": goods_temp_range[0],
            "temp_max": goods_temp_range[1]
        })
    
    return pd.DataFrame(shipments)

# Create the dataset
df_shipments = generate_shipment_data(500)

# Save to CSV
df_shipments.to_csv("shipments_data.csv", index=False)

print(f"Generated {len(df_shipments)} shipment records")
print(df_shipments.head())