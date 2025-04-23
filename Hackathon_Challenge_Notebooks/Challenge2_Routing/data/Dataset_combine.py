import pandas as pd

# Read all CSV files
def read_csvs():
    delivery_locations = pd.read_csv('delivery_locations.csv')
    delivery_orders = pd.read_csv('delivery_orders.csv')
    distance_traffic_matrix = pd.read_csv('distance_traffic_matrix.csv')
    
    print(f"Loaded datasets:")
    print(f"- delivery_locations: {delivery_locations.shape}")
    print(f"- delivery_orders: {delivery_orders.shape}")
    print(f"- distance_traffic_matrix: {distance_traffic_matrix.shape}")
    
    return delivery_locations, delivery_orders, distance_traffic_matrix

# Merge datasets step by step
def merge_datasets(delivery_locations, delivery_orders, distance_traffic_matrix):
    # 1. Merge delivery_orders with delivery_locations
    # Link orders to their delivery locations
    merged_df = pd.merge(
        delivery_orders,
        delivery_locations,
        left_on='delivery_location_id',
        right_on='location_id',
        how='outer'
    )
    print(f"After merging delivery_orders and delivery_locations: {merged_df.shape}")
    
    # We now need to handle the distance_traffic_matrix differently since it's a many-to-many relationship
    # First, we'll pivot it to create a matrix of distances and times
    
    # 2. Create a distance matrix
    distance_matrix = pd.pivot_table(
        distance_traffic_matrix,
        values='distance_km',
        index='from_location_id',
        columns='to_location_id',
        fill_value=0
    )
    
    # Rename columns to reflect they are distances
    distance_matrix.columns = [f'distance_to_{col}_km' for col in distance_matrix.columns]
    distance_matrix.reset_index(inplace=True)
    distance_matrix.rename(columns={'from_location_id': 'location_id'}, inplace=True)
    
    # 3. Create a base time matrix
    time_matrix = pd.pivot_table(
        distance_traffic_matrix,
        values='base_time_min',
        index='from_location_id',
        columns='to_location_id',
        fill_value=0
    )
    
    # Rename columns to reflect they are travel times
    time_matrix.columns = [f'travel_time_to_{col}_min' for col in time_matrix.columns]
    time_matrix.reset_index(inplace=True)
    time_matrix.rename(columns={'from_location_id': 'location_id'}, inplace=True)
    
    # 4. Create a traffic multiplier matrix
    traffic_matrix = pd.pivot_table(
        distance_traffic_matrix,
        values='traffic_multiplier',
        index='from_location_id',
        columns='to_location_id',
        fill_value=1
    )
    
    # Rename columns to reflect they are traffic multipliers
    traffic_matrix.columns = [f'traffic_multiplier_to_{col}' for col in traffic_matrix.columns]
    traffic_matrix.reset_index(inplace=True)
    traffic_matrix.rename(columns={'from_location_id': 'location_id'}, inplace=True)
    
    # 5. Merge the merged_df with the distance matrix
    final_df = pd.merge(
        merged_df,
        distance_matrix,
        on='location_id',
        how='left'
    )
    print(f"After merging with distance matrix: {final_df.shape}")
    
    # 6. Merge with time matrix
    final_df = pd.merge(
        final_df,
        time_matrix,
        on='location_id',
        how='left'
    )
    print(f"After merging with time matrix: {final_df.shape}")
    
    # 7. Merge with traffic matrix
    final_df = pd.merge(
        final_df,
        traffic_matrix,
        on='location_id',
        how='left'
    )
    print(f"After merging with traffic matrix: {final_df.shape}")
    
    return final_df

# Main function to run the entire process
def main():
    # Read all CSV files
    delivery_locations, delivery_orders, distance_traffic_matrix = read_csvs()
    
    # Merge datasets
    combined_df = merge_datasets(delivery_locations, delivery_orders, distance_traffic_matrix)
    
    # Save the combined dataset
    combined_df.to_csv('combined_delivery_data.csv', index=False)
    print("\nCombined dataset saved as 'combined_delivery_data.csv'")
    print(f"Final dataset shape: {combined_df.shape}")
    
    # Display column names to confirm no duplicates
    print("\nColumns in final dataset:")
    for col in combined_df.columns:
        print(f"- {col}")

if __name__ == "__main__":
    main()