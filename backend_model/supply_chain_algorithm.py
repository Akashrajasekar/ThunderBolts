import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from geopy.distance import geodesic
import math
import os

# Load the data (assuming the data was generated using the previous script)
def load_data(file_path="cargo_sharing_dataset.csv"):
    """Load shipment data from CSV file"""
    # Ensure file path exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")
        
    df = pd.read_csv(file_path)
    
    # Convert timestamp and scheduled_delivery_time to datetime if they are strings
    if 'timestamp' in df.columns and isinstance(df['timestamp'].iloc[0], str):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if 'scheduled_delivery_time' in df.columns and isinstance(df['scheduled_delivery_time'].iloc[0], str):
        df['scheduled_delivery_time'] = pd.to_datetime(df['scheduled_delivery_time'])
        
    return df

# Define compatibility checker based on goods type
def are_goods_compatible(goods_type1, goods_type2, goods_types_dict):
    """Check if two types of goods are compatible for shipment together"""
    # Same type is always compatible
    if goods_type1 == goods_type2:
        return True
    
    # Check if goods_type2 is in the compatibility list of goods_type1
    if goods_type1 in goods_types_dict and goods_type2 in goods_types_dict[goods_type1]["compatibility"]:
        return True
    
    return False

# Define temperature compatibility checker
def is_temp_compatible(temp_range1, temp_range2, overlap_threshold=2):
    """
    Check if temperature ranges are compatible
    temp_range1, temp_range2: tuples of (min_temp, max_temp)
    overlap_threshold: minimum overlap required in degrees
    """
    min1, max1 = temp_range1
    min2, max2 = temp_range2
    
    # Calculate overlap
    overlap_min = max(min1, min2)
    overlap_max = min(max1, max2)
    
    # Check if there's sufficient overlap
    if overlap_max - overlap_min >= overlap_threshold:
        return True
    
    return False

# Calculate distance between two locations
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

# Check if destinations are close enough
def are_destinations_close(lat1, lon1, lat2, lon2, threshold_km=50):
    """Check if two destinations are within the threshold distance"""
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= threshold_km

# Calculate a score for each potential match based on multiple factors
def calculate_match_score(shipment, potential_match, dest_threshold_km=50):
    """
    Calculate a score indicating how good a match is
    Higher score = better match (out of 100 points total)
    """
    score = 0
    
    # 1. Storage space - higher available space gets higher score (max 35 points)
    storage_ratio = potential_match["storage_left"] / shipment["units"]
    if storage_ratio >= 1:  # Can fit the entire shipment
        score += min(35, 20 + 15 * (storage_ratio - 1))  # More space = higher score up to a point
    else:
        score += 20 * storage_ratio  # Partial fit gets proportional score
    
    # 2. Destination proximity - closer destinations get higher score (max 20 points)
    dest_distance = calculate_distance(
        shipment["dest_lat"], shipment["dest_lon"],
        potential_match["dest_lat"], potential_match["dest_lon"]
    )
    if dest_distance <= dest_threshold_km:
        # Maximum points for very close destinations, decreasing linearly
        score += max(0, 20 * (1 - dest_distance / dest_threshold_km))
    
    # 3. Source proximity - closer pickup locations get higher score (max 15 points)
    source_distance = calculate_distance(
        shipment["source_lat"], shipment["source_lon"],
        potential_match["source_lat"], potential_match["source_lon"]
    )
    source_threshold_km = 30  # Adjust as needed
    if source_distance <= source_threshold_km:
        score += max(0, 15 * (1 - source_distance / source_threshold_km))
    
    # 4. Timing - shipments closer in time get higher score (max 10 points)
    time_diff = abs((shipment["timestamp"] - potential_match["timestamp"]).total_seconds() / 3600)  # hours
    time_threshold = 48  # 48 hours threshold
    if time_diff <= time_threshold:
        score += max(0, 10 * (1 - time_diff / time_threshold))
    
    # 5. Different company bonus (encouraging cross-company collaboration) - 5 points
    if shipment["company"] != potential_match["company"]:
        score += 5
    
    # 6. Scheduled delivery time compatibility (max 15 points)
    if "scheduled_delivery_time" in shipment and "scheduled_delivery_time" in potential_match:
        # Calculate time difference between scheduled deliveries
        delivery_diff = abs((shipment["scheduled_delivery_time"] - 
                           potential_match["scheduled_delivery_time"]).total_seconds() / 3600)  # hours
        delivery_threshold = 24  # 24 hours threshold for delivery time
        if delivery_diff <= delivery_threshold:
            score += max(0, 15 * (1 - delivery_diff / delivery_threshold))
    
    # Note: Carbon emission reduction has been removed from the scoring calculation
    # But will still be calculated and displayed in the results
    
    return score

# Main recommendation function
def recommend_best_matches(shipment_info, all_shipments, goods_types_dict, num_recommendations=5, 
                           dest_threshold_km=50, time_threshold_hours=48):
    """
    Find the best matching trucks for a given shipment using a greedy approach
    
    Parameters:
    - shipment_info: dict with details of the shipment needing space
    - all_shipments: DataFrame containing all available shipments
    - goods_types_dict: Dictionary with compatibility information
    - num_recommendations: Number of recommendations to return
    - dest_threshold_km: Maximum distance between destinations to be considered close
    - time_threshold_hours: Maximum time difference between shipments
    
    Returns:
    - List of recommended shipments with their matching scores
    """
    # Convert timestamp strings to datetime if needed
    if isinstance(shipment_info["timestamp"], str):
        shipment_info["timestamp"] = pd.to_datetime(shipment_info["timestamp"])
    
    if "scheduled_delivery_time" in shipment_info and isinstance(shipment_info["scheduled_delivery_time"], str):
        shipment_info["scheduled_delivery_time"] = pd.to_datetime(shipment_info["scheduled_delivery_time"])
    
    if isinstance(all_shipments["timestamp"].iloc[0], str):
        all_shipments["timestamp"] = pd.to_datetime(all_shipments["timestamp"])
    
    # Filter out shipments that don't meet basic criteria
    potential_matches = all_shipments[
        # Must have enough storage space left
        (all_shipments["storage_left"] >= shipment_info["units"]) &
        # Must not be the same shipment
        (all_shipments["shipment_id"] != shipment_info.get("shipment_id", "")) &
        # Time difference should be within threshold
        (abs((all_shipments["timestamp"] - shipment_info["timestamp"]).dt.total_seconds() / 3600) <= time_threshold_hours)
    ].copy()
    
    if potential_matches.empty:
        return []
    
    # Check goods compatibility and temperature compatibility
    compatible_matches = []
    
    # Keep track of the nearest match (even if it exceeds destination threshold)
    nearest_match = None
    nearest_distance = float('inf')
    
    for _, match in potential_matches.iterrows():
        # Check goods type compatibility
        if not are_goods_compatible(shipment_info["goods_type"], match["goods_type"], goods_types_dict):
            continue
        
        # Check temperature compatibility
        shipment_temp_range = (shipment_info["temp_min"], shipment_info["temp_max"])
        match_temp_range = (match["temp_min"], match["temp_max"])
        
        if not is_temp_compatible(shipment_temp_range, match_temp_range):
            continue
        
        # Calculate destination distance
        dest_distance = calculate_distance(
            shipment_info["dest_lat"], shipment_info["dest_lon"],
            match["dest_lat"], match["dest_lon"]
        )
        
        # Check if this is the nearest match so far
        if dest_distance < nearest_distance:
            nearest_distance = dest_distance
            nearest_match = match.copy()
            nearest_match["distance"] = dest_distance
        
        # Check if destinations are close enough for a normal match
        if dest_distance <= dest_threshold_km:
            # If all constraints are satisfied, add to compatible matches
            compatible_matches.append(match)
    
    if not compatible_matches:
        # If no compatible matches within threshold, but we have a nearest match
        if nearest_match is not None:
            # Add a flag to indicate this is beyond the typical threshold
            nearest_match["exceeds_threshold"] = True
            compatible_matches = [nearest_match]
        else:
            return []
    
    # Convert list to DataFrame for easier handling
    compatible_df = pd.DataFrame(compatible_matches)
    
    # Calculate match score for each compatible match
    scores = []
    for _, match in compatible_df.iterrows():
        match_score = calculate_match_score(shipment_info, match, dest_threshold_km)
        
        result = {
            "shipment_id": match["shipment_id"],
            "company": match["company"],
            "truck_type": match["truck_type"],
            "source": match["source"],
            "destination": match["destination"],
            "storage_left": match["storage_left"],
            "goods_type": match["goods_type"],
            "score": match_score,
        }
        
        # Add scheduled delivery time if available
        if "scheduled_delivery_time" in match:
            result["scheduled_delivery_time"] = match["scheduled_delivery_time"]
        
        # Add carbon footprint data if available (static calculation)
        if "carbon_footprint_per_km" in match:
            result["carbon_footprint_per_km"] = match["carbon_footprint_per_km"]
            
            # Calculate static carbon savings (assuming 30% savings from sharing)
            # This is a simplified model that avoids dynamic calculations
            base_emissions = match["carbon_footprint_per_km"]
            carbon_savings_percent = 30.0  # Fixed 30% savings
            carbon_savings = base_emissions * 0.3  # 30% of the base emissions
            
            result["carbon_savings_percent"] = carbon_savings_percent
            result["carbon_savings"] = round(carbon_savings, 2)
        
        # Add distance info if this is the nearest match that exceeds threshold
        if "exceeds_threshold" in match and match["exceeds_threshold"]:
            result["exceeds_threshold"] = True
            result["distance"] = match["distance"]
            
        scores.append(result)
    
    # Sort by score (descending)
    sorted_matches = sorted(scores, key=lambda x: x["score"], reverse=True)
    
    # Return top N recommendations
    return sorted_matches[:num_recommendations]

# Calculate carbon impact of a shipment sharing (static calculation)
def calculate_carbon_impact(shipment1, shipment2):
    """
    Calculate the carbon impact of sharing a shipment using a fixed savings percentage
    
    Parameters:
    - shipment1, shipment2: Dictionaries containing shipment information
    
    Returns:
    - Dictionary with carbon savings information
    """
    if "carbon_footprint_per_km" not in shipment1 or "carbon_footprint_per_km" not in shipment2:
        return None
    
    # Calculate emissions if shipped separately
    separate_emissions = (shipment1["carbon_footprint_per_km"] + shipment2["carbon_footprint_per_km"])
    
    # Static calculation - assume 30% savings from shared shipping
    carbon_savings_percent = 30.0
    carbon_savings = separate_emissions * 0.3
    shared_emissions = separate_emissions - carbon_savings
    
    # Calculate approximate distance
    distance = calculate_distance(
        shipment1["source_lat"], shipment1["source_lon"],
        shipment1["dest_lat"], shipment1["dest_lon"]
    )
    
    # Total savings across the journey
    total_savings = carbon_savings * distance
    
    return {
        "separate_emissions": round(separate_emissions, 2),
        "shared_emissions": round(shared_emissions, 2),
        "carbon_savings_per_km": round(carbon_savings, 2),
        "savings_percent": carbon_savings_percent,
        "approximate_distance": round(distance, 1),
        "total_carbon_savings": round(total_savings, 1)
    }

# Example usage
if __name__ == "__main__":
    # Load data
    df_shipments = load_data()
    
    # Import GOODS_TYPES from the data generation script or define it here
    # This is a simplified version for the example
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
    
    # Example shipment
    sample_shipment = df_shipments.iloc[0].to_dict()
    # Modify some values to make it a new shipment
    sample_shipment["shipment_id"] = "NEW001"
    sample_shipment["units"] = 50  # The amount of goods we need to ship
    
    # Get recommendations
    recommendations = recommend_best_matches(sample_shipment, df_shipments, GOODS_TYPES)
    
    # Print recommendations
    print(f"Top recommendations for shipment {sample_shipment['shipment_id']}:")
    for i, rec in enumerate(recommendations, 1):
        base_info = f"{i}. {rec['company']} - {rec['truck_type']} - {rec['source']} to {rec['destination']} - Score: {rec['score']:.2f}/100"
        
        # Add carbon information if available
        carbon_info = ""
        if "carbon_savings_percent" in rec:
            carbon_info = f" - Carbon reduction: {rec['carbon_savings_percent']}%"
            
        # Add scheduled delivery time if available
        delivery_info = ""
        if "scheduled_delivery_time" in rec:
            delivery_info = f" - Delivery: {rec['scheduled_delivery_time']}"
            
        # Add threshold warning if applicable
        threshold_info = ""
        if rec.get("exceeds_threshold", False):
            threshold_info = f" (NOTE: Distance of {rec['distance']:.1f} km exceeds threshold)"
            
        print(base_info + carbon_info + delivery_info + threshold_info)