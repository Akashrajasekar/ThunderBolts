#!/usr/bin/env python3
"""
Deployment Setup Script for Supply Chain Space Sharing Recommender
This script helps prepare the application for deployment by ensuring 
all necessary files are in the correct locations.
"""

import os
import shutil
import sys

def ensure_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        print(f"Creating directory: {path}")
        os.makedirs(path)

def copy_file(source, destination):
    """Copy file from source to destination"""
    if os.path.exists(source):
        print(f"Copying {source} to {destination}")
        shutil.copy2(source, destination)
        return True
    else:
        print(f"Source file not found: {source}")
        return False

def setup_deployment():
    """Setup the deployment environment"""
    print("Setting up deployment environment...")
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Define file paths
    source_dataset = os.path.join(script_dir, "dataset", "cargo_sharing_dataset.csv")
    
    # List of target locations to ensure the dataset file exists
    target_locations = [
        os.path.join(script_dir, "dataset"),
        os.path.join(script_dir, "data"),
        os.path.join(script_dir)  # Root directory
    ]
    
    # Ensure dataset file exists in multiple potential locations
    for location in target_locations:
        ensure_directory(location)
        copy_file(source_dataset, os.path.join(location, "cargo_sharing_dataset.csv"))
    
    print("\nDeployment setup complete!")
    print("\nTo run the application in debug mode, use:")
    print("streamlit run app.py debug")

if __name__ == "__main__":
    setup_deployment() 