import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from geopy.distance import geodesic

# Import the algorithm functions - update the import path based on your file structure
from supply_chain_algorithm import (
    load_data, recommend_best_matches, are_goods_compatible, 
    is_temp_compatible, calculate_distance, calculate_carbon_impact
)

# Set page configuration
st.set_page_config(page_title="Supply Chain Space Sharing Recommender", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #f5f7f9;
    }
    
    /* Header styling */
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #2c3e50;
        text-align: center;
        padding: 0.5rem;
        margin-bottom: 1rem;
        border-radius: 10px;
    }
    
    /* Card styling */
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-bottom: 0.2rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    /* Status colors */
    .status-available {
        color: #00cc44;
    }
    
    .status-filling {
        color: #ffcc00;
    }
    
    .status-full {
        color: #ff3300;
    }
    
    /* Section headers */
    .section-header {
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 1rem;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #3498db;
    }
    
    /* Info text */
    .info-text {
        background-color: #eaf2f8;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">Supply Chain Space Sharing Recommender</h1>', unsafe_allow_html=True)
st.markdown('<p class="info-text">This system helps find the best trucks with available space that match your shipment requirements.</p>', unsafe_allow_html=True)

# Check if the dataset exists or generate it
try:
    df_shipments = load_data("cargo_sharing_dataset.csv")
    st.success(f"Loaded dataset with {len(df_shipments)} shipment records")
except Exception as e:
    st.error(f"Dataset error: {e}")
    st.info("Please ensure 'cargo_sharing_dataset.csv' is in the current directory.")

# Import GOODS_TYPES from file or define here
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

# Get unique companies, goods types, cities, etc. from the loaded dataset
if 'df_shipments' in locals():
    COMPANIES = sorted(df_shipments['company'].unique().tolist())
    CITIES = sorted(df_shipments['source'].unique().tolist())
    available_goods_types = sorted(df_shipments['goods_type'].unique().tolist())
    
    # Create city coordinates dictionary from the data
    CITY_COORDINATES = {}
    for city in CITIES:
        city_data = df_shipments[df_shipments['source'] == city].iloc[0]
        CITY_COORDINATES[city] = (city_data['source_lat'], city_data['source_lon'])
else:
    # Fallback values if dataset isn't loaded
    COMPANIES = ["LogiTech Shipping", "FastTrack Logistics", "EcoTrans", "GlobalMove"]
    CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
    available_goods_types = list(GOODS_TYPES.keys())
    CITY_COORDINATES = {city: (0, 0) for city in CITIES}

# Sidebar for input parameters
st.sidebar.markdown('<h2 class="section-header">📦 Your Shipment Details</h2>', unsafe_allow_html=True)

# Input for shipment details
selected_company = st.sidebar.selectbox("Your Company", options=COMPANIES)
selected_goods_type = st.sidebar.selectbox("Type of Goods", options=available_goods_types)
selected_source = st.sidebar.selectbox("Source Location", options=CITIES)
selected_destination = st.sidebar.selectbox("Destination Location", options=[city for city in CITIES if city != selected_source])
units_of_goods = st.sidebar.number_input("Units of Goods", min_value=1, max_value=500, value=25)

# Get temperature range for selected goods type
if selected_goods_type in GOODS_TYPES:
    temp_min, temp_max = GOODS_TYPES[selected_goods_type]["temp_range"]
else:
    # If not in our predefined dictionary, estimate from the dataset
    goods_data = df_shipments[df_shipments['goods_type'] == selected_goods_type]
    if not goods_data.empty:
        temp_min = goods_data['temp_min'].iloc[0]
        temp_max = goods_data['temp_max'].iloc[0]
    else:
        temp_min, temp_max = (10, 25)  # default values

st.sidebar.markdown(f'<div class="info-text">Temperature requirements: {temp_min}°C to {temp_max}°C</div>', unsafe_allow_html=True)

# Remove carbon footprint input - using static calculations
st.sidebar.markdown('<div class="info-text">💡 Carbon savings will be calculated automatically for all matching shipments.</div>', unsafe_allow_html=True)

# Scheduled delivery time
delivery_dates = pd.date_range(start=datetime.now(), periods=14, freq='D')
selected_delivery_date = st.sidebar.date_input("Scheduled Delivery Date", value=delivery_dates[7])
selected_delivery_time = st.sidebar.time_input("Scheduled Delivery Time", value=datetime.now().replace(hour=12, minute=0))
scheduled_delivery_time = datetime.combine(selected_delivery_date, selected_delivery_time)

# Additional constraints
st.sidebar.markdown('<h2 class="section-header">⚙️ Additional Constraints</h2>', unsafe_allow_html=True)
dest_threshold_km = st.sidebar.slider("Max Distance Between Destinations (km)", 10, 200, 100)
time_threshold_hours = st.sidebar.slider("Max Time Difference (hours)", 6, 168, 72)

# Get coordinates
source_lat, source_lon = CITY_COORDINATES[selected_source]
dest_lat, dest_lon = CITY_COORDINATES[selected_destination]

# Create the shipment info dictionary
current_timestamp = datetime.now()
shipment_info = {
    "shipment_id": "NEW" + str(hash(current_timestamp) % 10000),
    "timestamp": current_timestamp,
    "company": selected_company,
    "goods_type": selected_goods_type,
    "source": selected_source,
    "destination": selected_destination,
    "units": units_of_goods,
    "source_lat": source_lat,
    "source_lon": source_lon,
    "dest_lat": dest_lat,
    "dest_lon": dest_lon,
    "temp_min": temp_min,
    "temp_max": temp_max,
    "scheduled_delivery_time": scheduled_delivery_time
}

# Function to get status info based on utilization
def get_status_info(utilization):
    if utilization < 50:
        return "🟢", "#00cc44", "Available"
    elif utilization < 90:
        return "🟡", "#ffcc00", "Filling Up"
    else:
        return "🔴", "#ff3300", "Full"

# Function to create styled truck card
def create_truck_card(company, truck_type, score, storage_left, carbon_savings):
    # Calculate utilization for color coding
    utilization = (units_of_goods / storage_left * 100)
    symbol, card_color, status = get_status_info(min(utilization, 99))
    
    card = f"""
    <div style="padding:20px; margin:10px 0; border-radius:15px; 
         background:white; 
         border:1px solid #e0e0e0; 
         box-shadow: 0 6px 12px rgba(0,0,0,0.08);
         transition: transform 0.3s ease, box-shadow 0.3s ease;">
        <div style="display:flex; align-items:center; margin-bottom:15px;">
            <div style="font-size:2.5rem; margin-right:15px; color:{card_color};">🚚</div>
            <div>
                <h3 style="margin:0; color:#2c3e50; font-size:1.4rem;">{company}</h3>
                <p style="margin:0; color:#7f8c8d;">{truck_type}</p>
            </div>
            <div style="margin-left:auto; text-align:right;">
                <div style="font-size:1.8rem; font-weight:bold; color:#3498db;">{score:.1f}</div>
                <div style="color:#7f8c8d; font-size:0.8rem;">Match Score</div>
            </div>
        </div>
        <div style="background:#f8f9fa; border-radius:10px; padding:15px; margin-bottom:15px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:#7f8c8d;"><b>Available Space:</b></span>
                <span style="color:#2c3e50; font-weight:500;">{storage_left:.1f} units</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:#7f8c8d;"><b>Your Shipment:</b></span>
                <span style="color:#2c3e50; font-weight:500;">{units_of_goods} units ({utilization:.1f}%)</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#7f8c8d;"><b>Carbon Savings:</b></span>
                <span style="color:#00cc44; font-weight:bold;">{carbon_savings}%</span>
            </div>
        </div>
        <div style="background:#f0f3f6; height:12px; border-radius:6px; overflow:hidden; margin-bottom:12px;">
            <div style="background:{card_color}; width:{min(utilization, 100)}%; height:100%;"></div>
        </div>
        <div style="text-align:center; font-size:0.9em; color:#7f8c8d;">
            {symbol} <span style="color:{card_color}; font-weight:500;">{status}</span>
        </div>
    </div>
    """
    return card

# Button to find recommendations
if st.sidebar.button("Find Best Matches"):
    # Make sure df_shipments is defined
    if 'df_shipments' not in locals():
        st.error("Dataset not loaded. Please ensure the dataset file exists.")
    else:
        # Get recommendations
        with st.spinner("Finding the best matches..."):
            recommendations = recommend_best_matches(
                shipment_info, 
                df_shipments, 
                GOODS_TYPES, 
                num_recommendations=10,
                dest_threshold_km=dest_threshold_km,
                time_threshold_hours=time_threshold_hours
            )
        
        # Display recommendations
        if recommendations:
            st.markdown('<h2 class="section-header">🎯 Top Recommendations for Your Shipment</h2>', unsafe_allow_html=True)
            
            # Check if any recommendation exceeds threshold
            any_exceeds_threshold = any(rec.get("exceeds_threshold", False) for rec in recommendations)
            if any_exceeds_threshold:
                st.markdown('<div class="info-text" style="border-left-color: #ff9800;">⚠️ Some recommendations exceed your distance threshold but are shown as they\'re the closest available matches.</div>', unsafe_allow_html=True)
            
            # Create columns for layout
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create a DataFrame from recommendations for display
                rec_df = pd.DataFrame(recommendations)
                
                # Convert delivery time to a more readable format if it exists
                if "scheduled_delivery_time" in rec_df.columns:
                    rec_df["Delivery Time"] = rec_df["scheduled_delivery_time"].dt.strftime("%Y-%m-%d %H:%M")
                
                # Add some extra info for display
                rec_df["Space Usage"] = (units_of_goods / rec_df["storage_left"] * 100).round(1).astype(str) + "%"
                
                # Display columns that should be shown
                display_columns = ["company", "truck_type", "source", "destination", 
                                  "storage_left", "Space Usage"]
                
                # Add delivery time if available
                if "Delivery Time" in rec_df.columns:
                    display_columns.append("Delivery Time")
                
                # Add score
                display_columns.append("score")
                
                # Add carbon columns if available
                if "carbon_savings_percent" in rec_df.columns:
                    rec_df["Carbon Savings"] = rec_df["carbon_savings_percent"].astype(str) + "%"
                    display_columns.append("Carbon Savings")
                
                # Format threshold exceed notes
                if "exceeds_threshold" in rec_df.columns:
                    rec_df["Note"] = ""
                    for idx, row in rec_df.iterrows():
                        if row.get("exceeds_threshold", False):
                            rec_df.at[idx, "Note"] = f"⚠️ {row['distance']:.1f} km"
                    
                    display_columns.append("Note")
                
                # Define styling function
                def highlight_rows(row):
                    styles = [''] * len(row)
                    
                    # Highlight top 3 recommendations
                    if row.name < 3:
                        styles = ['background-color: rgba(75, 192, 192, 0.2)'] * len(row)
                    
                    # Add warning style for exceeded threshold
                    if "exceeds_threshold" in row and row["exceeds_threshold"]:
                        for i, col in enumerate(row.index):
                            if col == "Note":
                                styles[i] = 'background-color: #FFEEEE; color: #CC0000; font-weight: bold'
                    
                    return styles
                
                # Display styled dataframe
                st.markdown('<h3 class="section-header">📋 Matching Trucks</h3>', unsafe_allow_html=True)
                st.dataframe(
                    rec_df[display_columns].style.apply(
                        highlight_rows, axis=1
                    ).format({
                        "score": "{:.1f}",
                        "storage_left": "{:.0f}"
                    }),
                    height=400,
                    use_container_width=True
                )
                
                # Show top 3 as cards
                st.markdown('<h3 class="section-header">🏆 Top Matches</h3>', unsafe_allow_html=True)
                st.markdown('<div class="info-text">These are your best matches based on compatibility score</div>', unsafe_allow_html=True)
                
                for i, rec in enumerate(recommendations[:3]):
                    carbon_savings = rec.get("carbon_savings_percent", 30.0)  # Default to 30% if not available
                    st.components.v1.html(
                        create_truck_card(
                            rec["company"], 
                            rec["truck_type"], 
                            rec["score"], 
                            rec["storage_left"],
                            carbon_savings
                        ),
                        height=250
                    )
            
            with col2:
                # Create tabs for different visualizations
                tab1, tab2, tab3 = st.tabs(["Score Comparison", "Carbon Savings", "Delivery Times"])
                
                with tab1:
                    # Create a bar chart of top recommendations
                    st.markdown('<h3 class="section-header">📊 Match Score Comparison</h3>', unsafe_allow_html=True)
                    top_recs = recommendations[:5]
                    labels = [f"{r['company']} - {r['truck_type']}" for r in top_recs]
                    scores = [r['score'] for r in top_recs]
                    
                    # Using Plotly instead of Matplotlib
                    fig = px.bar(
                        x=scores,
                        y=labels,
                        orientation='h',
                        title="Top 5 Recommendations by Score",
                        labels={"x": "Match Score (out of 100)", "y": ""},
                        color=scores,
                        color_continuous_scale="Blues",
                        text=[f"{score:.1f}" for score in scores]
                    )
                    
                    fig.update_traces(textposition='outside')
                    fig.update_layout(height=400)
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    # Create carbon savings visualization
                    st.markdown('<h3 class="section-header">🌿 Carbon Reduction Analysis</h3>', unsafe_allow_html=True)
                    
                    # Sort by carbon savings for this chart
                    carbon_data = rec_df.head(5)  # Use top 5 by score since we're using static carbon savings
                    labels = [f"{r['company']} - {r['truck_type']}" for _, r in carbon_data.iterrows()]
                    savings = [30.0] * len(labels)  # Static 30% savings
                    
                    # Using Plotly instead of Matplotlib
                    fig = px.bar(
                        x=savings,
                        y=labels,
                        orientation='h',
                        title="Carbon Reduction from Space Sharing",
                        labels={"x": "Carbon Savings (%)", "y": ""},
                        color=savings,
                        color_continuous_scale="Greens",
                        text=[f"{saving:.1f}%" for saving in savings]
                    )
                    
                    fig.update_traces(textposition='outside')
                    fig.update_layout(height=400)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add potential carbon savings info
                    if "carbon_footprint_per_km" in rec_df.columns:
                        avg_footprint = rec_df["carbon_footprint_per_km"].mean()
                        distance = calculate_distance(source_lat, source_lon, dest_lat, dest_lon)
                        total_savings = avg_footprint * 0.3 * distance  # 30% of total emissions for the journey
                        
                        # Create styled metrics
                        st.markdown("""
                        <div style="display:flex; gap:20px; margin-top:20px;">
                            <div class="metric-card" style="flex:1">
                                <div class="metric-icon" style="color:#00cc44;">🌿</div>
                                <div class="metric-label">POTENTIAL CARBON REDUCTION</div>
                                <div class="metric-value">{:.2f} kg CO₂</div>
                            </div>
                            <div class="metric-card" style="flex:1">
                                <div class="metric-icon" style="color:#00cc44;">🔄</div>
                                <div class="metric-label">AVERAGE REDUCTION PER TRIP</div>
                                <div class="metric-value">30%</div>
                            </div>
                        </div>
                        """.format(total_savings), unsafe_allow_html=True)
                        
                        st.markdown('<p class="info-text">Sharing cargo space significantly reduces carbon emissions by eliminating redundant trips.</p>', unsafe_allow_html=True)
                
                with tab3:
                    # Create delivery time visualization if available
                    st.markdown('<h3 class="section-header">🕒 Delivery Schedule Alignment</h3>', unsafe_allow_html=True)
                    
                    if "scheduled_delivery_time" in rec_df.columns:
                        # Format delivery times for display
                        delivery_dates = rec_df["scheduled_delivery_time"].dt.strftime("%m-%d").tolist()
                        companies = rec_df["company"].tolist()
                        
                        # Create a plot showing delivery times in relation to requested time
                        requested_date = scheduled_delivery_time.strftime("%m-%d")
                        
                        # Create data for the visualization
                        delivery_data = pd.DataFrame({
                            "Company": companies[:5],  # Top 5 for clarity
                            "Delivery Date": delivery_dates[:5],
                            "Value": [1] * min(5, len(companies))
                        })
                        
                        # fig = px.timeline(
                        #     delivery_data, 
                        #     x="Value", 
                        #     y="Company", 
                        #     text="Delivery Date",
                        #     color_discrete_sequence=["lightgray"],
                        #     title="Delivery Schedule Comparison"
                        # )
                        
                        # Add annotation for requested date
                        fig.add_vline(x=0.5, line_dash="dash", line_color="red")
                        fig.add_annotation(
                            x=0.55, 
                            y=-0.5, 
                            text=f"Your requested date: {requested_date}",
                            showarrow=False, 
                            font=dict(color="red")
                        )
                        
                        fig.update_traces(textposition='inside', insidetextanchor='middle')
                        fig.update_layout(
                            xaxis=dict(showticklabels=False, showgrid=False),
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Delivery time data not available.")
                
                # Add explanatory text
                st.markdown('<h3 class="section-header">ℹ️ How Match Scores Work</h3>', unsafe_allow_html=True)
                st.markdown("""
                <div class="info-text">
                <strong>Match score calculation (out of 100):</strong><br>
                • <b>Storage space</b> (up to 35 points): Higher available space gets higher score<br>
                • <b>Destination proximity</b> (up to 20 points): Closer destinations get higher score<br>
                • <b>Source proximity</b> (up to 15 points): Closer pickup locations get higher score<br>
                • <b>Timing</b> (up to 10 points): Shipments closer in time get higher score<br>
                • <b>Scheduled delivery compatibility</b> (up to 15 points): Better aligned deliveries get higher score<br>
                • <b>Different company bonus</b> (5 points): Encourages cross-company collaboration
                </div>
                """, unsafe_allow_html=True)
                
                # Carbon impact information
                st.markdown('<h3 class="section-header">🌿 Environmental Impact</h3>', unsafe_allow_html=True)
                st.markdown("""
                <div class="info-text">
                Sharing cargo space between shipments reduces the total number of vehicles on the road,
                which directly leads to reduced carbon emissions and environmental impact.<br><br>
                <b>Note:</b> Based on industry averages, we estimate a 30% carbon reduction for each shared shipment.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-text" style="border-left-color: #ff9800;">⚠️ No matching trucks found. Try adjusting your constraints.</div>', unsafe_allow_html=True)

# Create tabs for additional data views
tab1, tab2 = st.tabs(["Dataset Overview", "About the System"])

with tab1:
    st.markdown('<h2 class="section-header">📊 Dataset Overview</h2>', unsafe_allow_html=True)
    
    if 'df_shipments' in locals():
        # Create metric summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">📦</div>
                <div class="metric-label">TOTAL SHIPMENTS</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(len(df_shipments)), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">🏢</div>
                <div class="metric-label">UNIQUE COMPANIES</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(len(df_shipments['company'].unique())), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">🚚</div>
                <div class="metric-label">AVAILABLE TRUCKS</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(len(df_shipments)), unsafe_allow_html=True)
            
        # Show distribution of goods types
        st.markdown('<h3 class="section-header">📊 Distribution of Goods Types</h3>', unsafe_allow_html=True)
        goods_counts = df_shipments["goods_type"].value_counts().head(10)  # Show top 10 for large datasets
        
        fig = px.bar(
            goods_counts,
            x=goods_counts.index,
            y=goods_counts.values,
            title="Top 10 Goods Types",
            labels={"x": "Goods Type", "y": "Count"},
            color=goods_counts.values,
            color_continuous_scale="Blues"
        )
        fig.update_layout(xaxis_tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show available storage distribution
        st.markdown('<h3 class="section-header">📈 Available Storage Distribution</h3>', unsafe_allow_html=True)
        
        fig = px.histogram(
            df_shipments.sample(min(1000, len(df_shipments))), 
            x="storage_left",
            nbins=20,
            title="Distribution of Available Storage Space",
            labels={"storage_left": "Available Storage Units"},
            color_discrete_sequence=["#3498db"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show carbon footprint data if available
        if "carbon_footprint_per_km" in df_shipments.columns:
            st.markdown('<h3 class="section-header">🌍 Carbon Footprint Distribution</h3>', unsafe_allow_html=True)
            
            fig = px.histogram(
                df_shipments.sample(min(1000, len(df_shipments))),
                x="carbon_footprint_per_km",
                nbins=15,
                title="Carbon Footprint Distribution",
                labels={"carbon_footprint_per_km": "Carbon Footprint (kg CO₂/km)"},
                color_discrete_sequence=["#2ecc71"]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        # Show delivery time distribution if available
        if "scheduled_delivery_time" in df_shipments.columns:
            st.markdown('<h3 class="section-header">🕒 Delivery Time Distribution</h3>', unsafe_allow_html=True)
            
            # Convert to hour of day for visualization
            if isinstance(df_shipments["scheduled_delivery_time"].iloc[0], pd.Timestamp):
                delivery_hours = df_shipments["scheduled_delivery_time"].dt.hour
                
                fig = px.histogram(
                    delivery_hours.sample(min(1000, len(df_shipments))),
                    nbins=24,
                    title="Delivery Hour Distribution",
                    labels={"value": "Delivery Hour of Day"},
                    color_discrete_sequence=["#9b59b6"]
                )
                
                fig.update_layout(
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(0, 24, 3)),
                        ticktext=[f"{h}:00" for h in range(0, 24, 3)]
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<div class="info-text">Load the dataset to view summary statistics and visualizations.</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<h2 class="section-header">ℹ️ About the System</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-text">
    <h3>How the Supply Chain Space Sharing Recommender Works</h3>
    
    This system helps optimize logistics operations by identifying opportunities for sharing cargo space between shipments.
    Key benefits include:
    
    <ul>
        <li><b>Cost Reduction:</b> Share transportation costs with compatible shipments</li>
        <li><b>Environmental Impact:</b> Reduce carbon emissions by optimizing truck capacity</li>
        <li><b>Efficiency:</b> Improve supply chain efficiency through better capacity utilization</li>
        <li><b>Collaboration:</b> Foster collaboration between companies with compatible shipping needs</li>
    </ul>
    
    The matching algorithm considers multiple factors including location proximity, temperature requirements,
    goods compatibility, delivery timing, and available space.
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="height: 100%;">
            <div class="metric-icon" style="color:#3498db;">🔍</div>
            <div class="metric-label">MATCHING CRITERIA</div>
            <div style="text-align: left; padding: 10px;">
                • Goods compatibility<br>
                • Temperature requirements<br>
                • Source proximity<br>
                • Destination proximity<br>
                • Delivery timing<br>
                • Available space
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="metric-card" style="height: 100%;">
            <div class="metric-icon" style="color:#2ecc71;">🌿</div>
            <div class="metric-label">ENVIRONMENTAL BENEFITS</div>
            <div style="text-align: left; padding: 10px;">
                • Reduced carbon emissions<br>
                • Lower fuel consumption<br>
                • Fewer vehicles on roads<br>
                • Optimized transportation<br>
                • Smaller environmental footprint<br>
                • Sustainable logistics
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-text" style="margin-top: 20px;">
    <h3>How to Use</h3>
    1. Enter your shipment details in the sidebar<br>
    2. Set any additional constraints<br>
    3. Click "Find Best Matches" to see recommended trucks<br>
    4. Review the match score, available space, and carbon savings for each option<br>
    5. Select the best match for your shipping needs
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: #7f8c8d;">Supply Chain Space Sharing Recommender System • Developed for Sustainable Logistics</div>', unsafe_allow_html=True)