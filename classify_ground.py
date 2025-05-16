#!/usr/bin/env python

import argparse
import pdal
import json

def classify_ground(input_file, output_file, max_window_size, slope, threshold):
    """
    Classify ground points in a LAS file using Progressive Morphological Filter (PMF).
    
    Parameters:
        input_file (str): Path to the input LAS file.
        output_file (str): Path to save the classified LAS file.
        max_window_size (int): Max window size for PMF.
        slope (float): Slope threshold for ground classification.
        threshold (float): Threshold value for ground points.
    """
    # Define PDAL pipeline in JSON format
    pipeline_json = {
        "pipeline": [
            {
                "type": "readers.las",  # Read LAS file
                "filename": input_file
            },
            {
                "type": "filters.pmf",  # Apply Progressive Morphological Filter
                "max_window_size": max_window_size,  # Use provided max window size
                "slope": slope,  # Use provided slope threshold
                "threshold": threshold  # Use provided threshold
            },
            {
                "type": "writers.las",  # Write output LAS with classification
                "filename": output_file
            }
        ]
    }

    # Create a PDAL pipeline from JSON
    pipeline = pdal.Pipeline(json.dumps(pipeline_json))

    # Execute the pipeline
    pipeline.execute()

    print(f"Ground classification completed. Output saved to: {output_file}")

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Classify ground points in a LAS file using PDAL.")
    parser.add_argument("input_file", help="Path to input LAS file.")
    parser.add_argument("output_file", help="Path to save the output LAS file.")
    
    # Add optional arguments for PMF parameters with default values
    parser.add_argument("--max_window_size", type=int, default=33, help="Max window size for PMF (default: 33).")
    parser.add_argument("--slope", type=float, default=0.2, help="Slope threshold for ground classification (default: 0.2).")
    parser.add_argument("--threshold", type=float, default=0.1, help="Threshold for ground points (default: 0.1).")

    # Parse arguments
    args = parser.parse_args()
    
    # Call the function to classify the ground points
    classify_ground(args.input_file, args.output_file, args.max_window_size, args.slope, args.threshold)

if __name__ == "__main__":
    main()
