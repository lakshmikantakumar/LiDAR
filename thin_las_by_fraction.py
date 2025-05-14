import laspy
import numpy as np
import argparse
import os
import sys

def thin_las_file(input_las: str, output_las: str, fraction: float):
    """
    Thins a LAS file by randomly selecting a specified fraction of points.

    Parameters:
        input_las (str): Path to input LAS file.
        output_las (str): Path to write the thinned LAS file.
        fraction (float): Fraction of points to retain (between 0 and 1).
    """

    if not 0 < fraction < 1:
        raise ValueError("Fraction must be between 0 and 1 (exclusive).")

    print(f"\n Reading LAS file: {input_las}")
    las = laspy.read(input_las)
    num_points = len(las.points)
    print(f"Total points: {num_points}")

    # Determine number of points to retain
    num_keep = int(num_points * fraction)
    print(f"Retaining {num_keep} points ({fraction * 100:.2f}%)")

    # Randomly sample indices of points to keep
    keep_indices = np.random.choice(num_points, size=num_keep, replace=False)

    # Extract the points to keep
    thinned_points = las.points[keep_indices]

    # Create new LasData with same header and thinned points
    thinned_las = laspy.LasData(las.header)
    thinned_las.points = thinned_points

    # Save the thinned LAS file
    thinned_las.write(output_las)
    print(f"Thinned LAS file saved to: {output_las}\n")

    
def main():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Thin a LAS file by randomly keeping a fraction of points.")
    parser.add_argument("input_las", help="Path to input LAS file")
    parser.add_argument("output_las", help="Path to output (thinned) LAS file")
    parser.add_argument("fraction", type=float, help="Fraction of points to retain (e.g., 0.25)")

    args = parser.parse_args()
    thin_las_file(args.input_las, args.output_las, args.fraction)
    
if __name__ == "__main__":
    main()

