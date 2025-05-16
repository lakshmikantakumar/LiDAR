#!/usr/bin/env python

import os
import argparse
import laspy
import numpy as np

def split_las(input_file, output_dir, tile_width, tile_height):
    """
    Splits a LAS file into smaller rectangular tiles of given width and height.
    Handles remaining edge tiles even if they are smaller than the tile size.

    Parameters:
        input_file (str): Path to the input LAS/LAZ file.
        output_dir (str): Directory where output tiles will be saved.
        tile_width (float): Width of each tile in LAS units (e.g., meters).
        tile_height (float): Height of each tile in LAS units (e.g., meters).
    """
    
    # Load the LAS file
    las = laspy.read(input_file)

    # Extract x and y coordinates of all points
    x = las.x
    y = las.y

    # Get the bounding box of the input point cloud
    min_x, max_x = x.min(), x.max()
    min_y, max_y = y.min(), y.max()

    print(f"Input file extent: X({min_x}, {max_x}), Y({min_y}, {max_y})")

    # Determine number of tiles in X and Y directions
    # Use ceil to ensure we include the remainder/edges
    num_tiles_x = int(np.ceil((max_x - min_x) / tile_width))
    num_tiles_y = int(np.ceil((max_y - min_y) / tile_height))

    print(f"Splitting into {num_tiles_x} x {num_tiles_y} tiles...")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Loop over each tile index
    for i in range(num_tiles_x):
        for j in range(num_tiles_y):
            # Calculate tile bounds
            tile_min_x = min_x + i * tile_width
            tile_max_x = tile_min_x + tile_width
            tile_min_y = min_y + j * tile_height
            tile_max_y = tile_min_y + tile_height

            # Create a mask to extract points within the current tile bounds
            mask = (
                (x >= tile_min_x) & (x < tile_max_x) &
                (y >= tile_min_y) & (y < tile_max_y)
            )

            # Skip tiles that contain no points
            if not np.any(mask):
                continue

            # Create a new LAS object with the same header as the original
            new_las = laspy.LasData(las.header)

            # Copy all point data (x, y, z, intensity, classification, etc.) using the mask
            for dim in las.point_format.dimensions:
                new_las[dim.name] = las[dim.name][mask]

            # Construct output filename using tile indices
            out_file = os.path.join(
                output_dir,
                f"tile_{i}_{j}.las"
            )

            # Write the new LAS tile to disk
            new_las.write(out_file)
            print(f"Saved tile: {out_file}")

    print("Splitting completed.")

def main():
    parser = argparse.ArgumentParser(description="Split a LAS file into smaller rectangular tiles.")
    parser.add_argument("input_file", help="Path to input LAS/LAZ file.")
    parser.add_argument("output_dir", help="Directory to save output tiles.")
    parser.add_argument("--tile_width", type=float, required=True, help="Tile width in LAS units (e.g., meters).")
    parser.add_argument("--tile_height", type=float, required=True, help="Tile height in LAS units (e.g., meters).")

    args = parser.parse_args()
    split_las(args.input_file, args.output_dir, args.tile_width, args.tile_height)

if __name__ == "__main__":
    main()
