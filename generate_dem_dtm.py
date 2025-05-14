import argparse
import laspy
import numpy as np
import rasterio
from rasterio.transform import from_origin
from scipy.interpolate import griddata
import os

def read_las_points(las_path, class_number=None):
    """Reads LAS file and optionally filters by class number."""
    print(f"Reading LAS file: {las_path}")
    las = laspy.read(las_path)
    x, y, z = las.x, las.y, las.z
    cls = las.classification

    if class_number is not None:
        mask = cls == class_number
        x, y, z = x[mask], y[mask], z[mask]
        print(f"Filtered to class {class_number}: {np.count_nonzero(mask)} points")

    return x, y, z

def interpolate_to_grid(x, y, z, resolution):
    """Interpolates scattered points onto a grid."""
    print("Interpolating points to grid...")
    xmin, xmax = np.min(x), np.max(x)
    ymin, ymax = np.min(y), np.max(y)

    xi = np.arange(xmin, xmax, resolution)
    yi = np.arange(ymin, ymax, resolution)
    xi, yi = np.meshgrid(xi, yi)

    zi = griddata((x, y), z, (xi, yi), method='linear')

    return xi, yi, zi

def write_raster(output_path, xi, yi, zi, nodata_val=-9999):
    """Writes interpolated data to a GeoTIFF raster."""
    print(f"Writing output raster: {output_path}")
    transform = from_origin(np.min(xi), np.max(yi), xi[1, 0] - xi[0, 0], yi[0, 0] - yi[1, 0])
    zi_filled = np.where(np.isnan(zi), nodata_val, zi)

    new_dataset = rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=zi.shape[0],
        width=zi.shape[1],
        count=1,
        dtype=zi_filled.dtype,
        crs="EPSG:32633",  # ⚠️ Adjust CRS accordingly
        transform=transform,
        nodata=nodata_val
    )
    new_dataset.write(zi_filled, 1)
    new_dataset.close()

def main():
    parser = argparse.ArgumentParser(description="Generate DEM or DTM from LAS file.")
    parser.add_argument("las_file", help="Input LAS/LAZ file path")
    parser.add_argument("output_tif", help="Output raster file path (DEM/DTM)")
    parser.add_argument("--class", dest="cls", type=int, default=None,
                        help="Optional: specify classification number (e.g. 2 for ground)")

    parser.add_argument("--res", dest="resolution", type=float, default=1.0,
                        help="Grid resolution (default: 1 meter)")

    args = parser.parse_args()

    # Step 1: Read points
    x, y, z = read_las_points(args.las_file, class_number=args.cls)

    # Step 2: Interpolate
    xi, yi, zi = interpolate_to_grid(x, y, z, args.resolution)

    # Step 3: Write output
    write_raster(args.output_tif, xi, yi, zi)

if __name__ == "__main__":
    main()
