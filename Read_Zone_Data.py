import csv
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import sys
from shapely.geometry import Point
import os

# Get current directory
current_dir = os.getcwd()

# Path to the 'data' folder
data_folder = os.path.join(current_dir, "data")

# Automatically find the first .shp file in the data folder
shapefile_path = None
for file in os.listdir(data_folder):
    if file.endswith(".shp"):
        shapefile_path = os.path.join(data_folder, file)
        break

# Raise error if no shapefile is found
if shapefile_path is None:
    raise FileNotFoundError("No .shp file found in the 'data' folder.")

# Function to calculate centroids, store x/y, and update geometry
def calculate_centroids(gdf):
    # Reproject to WGS84 (EPSG:4326) for output
    if gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    # Project to a metric CRS for accurate centroid calculation
    gdf_projected = gdf.to_crs(epsg=3857)
    centroids = gdf_projected.geometry.centroid

    # Reproject centroids back to EPSG:4326
    centroids_latlon = gpd.GeoSeries(centroids, crs=3857).to_crs(epsg=4326)

    # Build x/y columns
    gdf = gdf.copy()
    gdf['x_coord'] = centroids_latlon.x
    gdf['y_coord'] = centroids_latlon.y

    # Replace geometry with the centroid point
    gdf['geometry'] = gdf.apply(lambda row: Point(row['x_coord'], row['y_coord']), axis=1)
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs='EPSG:4326')

    return gdf

# Function to save centroids to CSV
def save_centroids_to_csv(gdf, output_csv_path, taz_column):
    nodes = []
    node_id_counter = 1

    for idx, row in gdf.iterrows():
        if row['geometry'] is None:
            continue
        
        geometry_wkt = row['geometry'].wkt.replace("\n", " ")
        TAZ_id = str(row[taz_column])
        
        nodes.append({
            "name": TAZ_id,
            "node_id": node_id_counter,
            "osm_node_id": "",
            "x_coord": row['x_coord'],
            "y_coord": row['y_coord'],
            "zone_id": node_id_counter,
            "TAZ_ID": TAZ_id,
            "geometry": geometry_wkt,
            "notes": " "
        })
        node_id_counter += 1

    nodes_df = pd.DataFrame(nodes)
    nodes_df = nodes_df.dropna()
    nodes_df.to_csv(output_csv_path, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
    print(f"Centroid data saved to {output_csv_path}")

# Plot centroid points with labels
def plot_taz_with_centroids(gdf, taz_column):
    ax = gdf.plot(figsize=(12, 8), color='red', markersize=10)

    for idx, row in gdf.iterrows():
        plt.text(row['geometry'].x, row['geometry'].y, str(row[taz_column]),
                 fontsize=8, ha='center', color='blue')

    plt.title("TAZ Centroid Points", fontsize=16)
    plt.xlabel("Longitude", fontsize=12)
    plt.ylabel("Latitude", fontsize=12)
    plt.grid(True)
    plt.show()

# Load the shapefile
try:
    gdf = gpd.read_file(shapefile_path)
    print("Shapefile loaded successfully.")
except Exception as e:
    print(f"Failed to load shapefile: {e}")
    sys.exit()

if gdf.crs is None:
    print("CRS is missing. Setting default CRS to EPSG:2868.")
    gdf.set_crs(epsg=2868, inplace=True)

print("Current CRS:", gdf.crs)

if gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)
    print("Reprojected CRS:", gdf.crs)

print("Available columns:", gdf.columns)

taz_column = "TRACTCE"
if taz_column not in gdf.columns:
    print(f"Column '{taz_column}' not found. Please check the attribute table.")
    sys.exit()

# Now correctly calculate and assign centroid-based geometry
gdf = calculate_centroids(gdf)

# Plot and export
plot_taz_with_centroids(gdf, taz_column)

output_csv_path = "Tempe_test_results/zone_centroid.csv"
save_centroids_to_csv(gdf, output_csv_path, taz_column)
