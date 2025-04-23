import pandas as pd

# Read all CSV files
def read_csvs():
    demand_forecast = pd.read_csv('demand_forecast.csv')
    inventory = pd.read_csv('inventory.csv')
    products = pd.read_csv('products.csv')
    transport_costs = pd.read_csv('transport_costs.csv')
    warehouses = pd.read_csv('warehouses.csv')
    
    print(f"Loaded datasets:")
    print(f"- demand_forecast: {demand_forecast.shape}")
    print(f"- inventory: {inventory.shape}")
    print(f"- products: {products.shape}")
    print(f"- transport_costs: {transport_costs.shape}")
    print(f"- warehouses: {warehouses.shape}")
    
    return demand_forecast, inventory, products, transport_costs, warehouses

# Merge datasets step by step
def merge_datasets(demand_forecast, inventory, products, transport_costs, warehouses):
    # 1. Merge demand_forecast with inventory on warehouse_id and product_id
    merged_df = pd.merge(
        demand_forecast, 
        inventory,
        on=['warehouse_id', 'product_id'],
        how='outer'
    )
    print(f"After merging demand_forecast and inventory: {merged_df.shape}")
    
    # 2. Merge with products on product_id
    merged_df = pd.merge(
        merged_df,
        products,
        on='product_id',
        how='outer'
    )
    print(f"After merging with products: {merged_df.shape}")
    
    # 3. Merge with warehouses on warehouse_id
    merged_df = pd.merge(
        merged_df,
        warehouses,
        on='warehouse_id',
        how='outer'
    )
    print(f"After merging with warehouses: {merged_df.shape}")
    
    # 4. Create a cross-reference for transport costs
    # We will rename columns to better represent the transport relationship
    transport_renamed = transport_costs.rename(
        columns={
            'from_warehouse_id': 'origin_warehouse_id',
            'to_warehouse_id': 'destination_warehouse_id'
        }
    )
    
    # For each warehouse, add possible transport destinations as separate columns
    # First, pivot the transport costs table
    transport_matrix = pd.pivot_table(
        transport_costs,
        values='cost_per_unit',
        index='from_warehouse_id',
        columns='to_warehouse_id',
        fill_value=0
    )
    
    # Rename columns to reflect they are transport costs
    transport_matrix.columns = [f'transport_cost_to_{col}' for col in transport_matrix.columns]
    transport_matrix.reset_index(inplace=True)
    transport_matrix.rename(columns={'from_warehouse_id': 'warehouse_id'}, inplace=True)
    
    # 5. Merge with transport matrix
    final_df = pd.merge(
        merged_df,
        transport_matrix,
        on='warehouse_id',
        how='left'
    )
    print(f"After merging with transport costs: {final_df.shape}")
    
    return final_df

# Main function to run the entire process
def main():
    # Read all CSV files
    demand_forecast, inventory, products, transport_costs, warehouses = read_csvs()
    
    # Merge datasets
    combined_df = merge_datasets(demand_forecast, inventory, products, transport_costs, warehouses)
    
    # Save the combined dataset
    combined_df.to_csv('combined_supply_chain_data.csv', index=False)
    print("\nCombined dataset saved as 'combined_supply_chain_data.csv'")
    print(f"Final dataset shape: {combined_df.shape}")
    
    # Display column names to confirm no duplicates
    print("\nColumns in final dataset:")
    for col in combined_df.columns:
        print(f"- {col}")

if __name__ == "__main__":
    main()