#!/usr/bin/env python

import os
import argparse
import laspy
import numpy as np

def merge_las_tiles(input_dir, output_file):
    """
    Merges all LAS/LAZ files in a given directory into a single LAS file.

    Parameters:
        input_dir (str): Directory containing LAS/LAZ tiles to be merged.
        output_file (str): Path to the output merged LAS file.
    """
    # Find all LAS/LAZ files in the input directory
    files = [f for f in os.listdir(input_dir) if f.lower().endswith((".las", ".laz"))]

    if not files:
        print(f"No LAS/LAZ files found in: {input_dir}")
        return

    print(f"Found {len(files)} files to merge.")

    merged_las = None  # This will hold the final combined LAS

    for i, filename in enumerate(files):
        file_path = os.path.join(input_dir, filename)
        print(f"Reading file {i + 1}/{len(files)}: {file_path}")
        
        # Read the LAS file
        las = laspy.read(file_path)

        if merged_las is None:
            # Initialize merged_las with the header of the first file
            merged_las = laspy.LasData(las.header)
            for dim in las.point_format.dimensions:
                merged_las[dim.name] = las[dim.name]
        else:
            # Append data from this file to the merged_las
            for dim in las.point_format.dimensions:
                merged_las[dim.name] = np.concatenate([merged_las[dim.name], las[dim.name]])

    # Write the merged LAS file
    merged_las.write(output_file)
    print(f"Merged LAS saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Merge multiple LAS/LAZ files into a single LAS file.")
    parser.add_argument("input_dir", help="Directory containing input LAS/LAZ files.")
    parser.add_argument("output_file", help="Path to save the merged LAS file.")

    args = parser.parse_args()
    merge_las_tiles(args.input_dir, args.output_file)

if __name__ == "__main__":
    main()
