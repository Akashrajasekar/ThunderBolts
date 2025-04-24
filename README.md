# Supply Chain Space Sharing Recommender

An intelligent supply chain optimization system that helps find the best trucks with available space matching your shipment requirements.

## Algorithm Overview

The core of this system is built around a sophisticated matching algorithm that evaluates compatibility between shipments using multiple factors:

- **Compatibility Matching**: Ensures goods types can be shipped together based on predefined compatibility rules
- **Temperature Range Validation**: Checks that temperature requirements for different goods overlap sufficiently
- **Destination Proximity**: Prioritizes shipments going to nearby destinations (configurable threshold, default 50km)
- **Source Proximity**: Considers pickup location proximity for efficient logistics
- **Timing Alignment**: Matches shipments with similar timestamps and delivery schedules
- **Storage Capacity**: Verifies sufficient remaining capacity for the shipment
- **Carbon Reduction**: Calculates approximate carbon savings from shared shipping (static 30% model)

The scoring system assigns points across these dimensions, with the final score out of 100 determining the best matches.

## Setup and Deployment

### Local Development
1. Clone the repository
2. Ensure dataset file is in the correct location: `dataset/cargo_sharing_dataset.csv`
3. Run the application:

streamlit run app.py

### Deployment Preparation
Before deploying to a cloud service, run the setup script to ensure all files are in their correct locations:

python setup_deployment.py

This will copy the dataset file to multiple locations that the app checks during startup, ensuring it can be found regardless of the working directory in the deployment environment.

### Debugging
If you're experiencing issues with the app finding the dataset, you can run in debug mode:

streamlit run app.py debug

This will show additional information about where the app is looking for the dataset file.

## File Structure
* `app.py` - Main Streamlit application
* `backend_model/supply_chain_algorithm.py` - Core algorithms and functions
* `dataset/cargo_sharing_dataset.csv` - Main dataset location
* `setup_deployment.py` - Helper script for deployment preparation
* `style.css` - Application styling (keep in the main directory)

## Algorithm Details

### Match Score Calculation
The recommendation algorithm calculates a match score (0-100) based on:
- Storage space availability (35 points max)
- Destination proximity (20 points max)
- Source proximity (15 points max)
- Timing compatibility (10 points max)
- Cross-company collaboration bonus (5 points)
- Delivery schedule alignment (15 points max)

### Recommendation Process
1. Filters potential matches based on basic criteria (storage, timing)
2. Validates goods compatibility using the goods types dictionary
3. Checks temperature range compatibility
4. Calculates match scores for all compatible shipments
5. Returns top-N recommendations sorted by score
6. Includes nearest match even if it exceeds destination threshold when no better options exist

### Carbon Impact Calculation
The system uses a simplified model for carbon impact:
- Assumes 30% emissions reduction from shared shipping
- Calculates per-kilometer and total journey savings
- Compares emissions between separate vs. shared shipping

## Features
* Intelligent matching of shipments based on multiple criteria
* Carbon footprint reduction calculations
* Intuitive user interface with dynamic visualizations
* Comprehensive analysis of available trucks and compatibility

## Deployment Troubleshooting
If the deployed version cannot find the dataset or CSS:
1. Run `python setup_deployment.py` locally before deploying
2. Ensure the deployment service includes all required files in the deployed package
3. Check if the deployment service has specific requirements for file paths
4. Try adding the dataset file to multiple locations within the project structure

## Styling Customization
To customize the appearance of the application, edit the `style.css` file in the main directory. The application will automatically load these styles at startup.

## Configuration Options
The algorithm provides several configurable parameters:
- `dest_threshold_km`: Maximum distance between destinations (default: 50km)
- `time_threshold_hours`: Maximum time difference between shipments (default: 48 hours)
- `overlap_threshold`: Minimum temperature range overlap required (default: 2°C)
- `num_recommendations`: Number of recommendations to return (default: 5)
