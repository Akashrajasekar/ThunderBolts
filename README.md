# Supply Chain Space Sharing Recommender

An intelligent supply chain optimization system that helps find the best trucks with available space matching your shipment requirements.

## Setup and Deployment

### Local Development

1. Clone the repository
2. Ensure dataset file is in the correct location: `dataset/cargo_sharing_dataset.csv`
3. Run the application:
   ```
   streamlit run app.py
   ```

### Deployment Preparation

Before deploying to a cloud service, run the setup script to ensure all files are in their correct locations:

```
python setup_deployment.py
```

This will copy the dataset file to multiple locations that the app checks during startup, ensuring it can be found regardless of the working directory in the deployment environment.

### Debugging

If you're experiencing issues with the app finding the dataset, you can run in debug mode:

```
streamlit run app.py debug
```

This will show additional information about where the app is looking for the dataset file.

### File Structure

- `app.py` - Main Streamlit application
- `backend_model/supply_chain_algorithm.py` - Core algorithms and functions
- `dataset/cargo_sharing_dataset.csv` - Main dataset location
- `setup_deployment.py` - Helper script for deployment preparation

## Features

- Intelligent matching of shipments based on multiple criteria
- Carbon footprint reduction calculations
- Intuitive user interface with dynamic visualizations
- Comprehensive analysis of available trucks and compatibility

## Deployment Troubleshooting

If the deployed version cannot find the dataset:

1. Run `python setup_deployment.py` locally before deploying
2. Ensure the deployment service includes the dataset file in the deployed package
3. Check if the deployment service has specific requirements for file paths
4. Try adding the dataset file to multiple locations within the project structure 