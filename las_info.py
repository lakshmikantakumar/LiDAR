#!/usr/bin/env python3

import laspy
import numpy as np
import pandas as pd
import os
import argparse
from collections import Counter
from datetime import datetime

def process_las_file(file_path, output_csv):
    """
    Processes a LAS/LAZ file and exports its metadata and point statistics 
    to a vertical CSV format (key-value per row), with file_name and timestamp shown once.
    """
    # Load the LAS file
    try:
        las = laspy.read(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"Processing: {file_path}")

    # Extract header information
    header = las.header
    x_min, y_min, z_min = header.mins
    x_max, y_max, z_max = header.maxs
    area_m2 = (x_max - x_min) * (y_max - y_min)
    num_points = len(las.points)
    point_density = num_points / area_m2 if area_m2 > 0 else 0

    # Classification counts
    classification_data = {}
    if "classification" in las.point_format.dimension_names:
        class_counts = Counter(las.classification)
        for class_id, count in class_counts.items():
            classification_data[f"class_{class_id}"] = count

    # Return number data
    return_data = {}
    if "return_number" in las.point_format.dimension_names:
        return_counts = Counter(las.return_number)
        for return_num, count in return_counts.items():
            return_data[f"return_{return_num}"] = count

    if "number_of_returns" in las.point_format.dimension_names:
        num_returns = Counter(las.number_of_returns)
        for n, count in num_returns.items():
            return_data[f"returns_per_pulse_{n}"] = count

    # Metadata and summary info
    summary = {
        "file_path": os.path.abspath(file_path),
        "version": str(header.version),
        "point_format": header.point_format.id,
        "num_points": num_points,
        "area_m2": area_m2,
        "point_density_m2": point_density,
        "system_identifier": header.system_identifier.strip(),
        "generating_software": header.generating_software.strip(),
        "creation_date": header.creation_date,
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
        "z_min": z_min,
        "z_max": z_max,
        "scale_x": header.scales[0],
        "scale_y": header.scales[1],
        "scale_z": header.scales[2],
        "offset_x": header.offsets[0],
        "offset_y": header.offsets[1],
        "offset_z": header.offsets[2],
    }

    # Combine all into one dictionary
    all_data = {**summary, **classification_data, **return_data}

    # Create DataFrame for key-value rows
    kv_df = pd.DataFrame(all_data.items(), columns=["property", "value"])

    # Prepare output lines
    output_lines = []

    # First: write file name and timestamp as separate header-like rows
    output_lines.append(["file_name", os.path.basename(file_path)])
    output_lines.append(["timestamp", datetime.now().isoformat()])
    
    # Then: add property-value header
    output_lines.append(["property", "value"])

    # Then: extend with actual property-value pairs
    output_lines.extend(kv_df.values.tolist())

    # Convert all to DataFrame
    final_df = pd.DataFrame(output_lines)

    # Save or append to CSV
    if not os.path.exists(output_csv):
        final_df.to_csv(output_csv, index=False, header=False)
    else:
        with open(output_csv, 'a', newline='') as f:
            final_df.to_csv(f, index=False, header=False)

    print(f"Summary saved to: {output_csv}")


def main():
    """
    Parse command-line arguments and process the LAS file.
    """
    parser = argparse.ArgumentParser(description="Export LAS/LAZ file info to vertical CSV format")
    parser.add_argument("input_file", help="Input LAS/LAZ file")
    parser.add_argument("-o", "--output", help="Output CSV file", default="las_summary.csv")

    args = parser.parse_args()
    process_las_file(args.input_file, args.output)


if __name__ == "__main__":
    main()
