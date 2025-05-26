# zone2assignment: Build Traffic Assignment Ready Networks from Zone-Based Demand
![Connected Transport Network Diagram](/images/workflow.png)
Preparing traffic assignment-ready networks involves several critical steps: defining zones (e.g., TAZs, census blocks), linking zones to the physical network, and producing a valid structure for traffic assignment. While traditional tools offer built-in workflows, they vary in flexibility, transparency, and automation capabilities. The proposed zone2assignment tool addresses these needs by enabling a clean, open-source pipeline for modern planning and research.

---
### Authors

Henan Zhu, Xuesong (Simon) Zhou, Han Zheng

Email: <a href="mailto:henanzhu@asu.edu">henanzhu@asu.edu</a>, 
<a href="mailto:xzhou74@asu.edu">xzhou74@asu.edu</a>, 
<a href="mailto:hzheng73@asu.edu">hzheng73@asu.edu</a>
</sub>

---

## 🧰 Prerequisites
- Python 3.11
- Conda (Miniconda or Anaconda)
- Basic understanding of traffic assignment and [General Modeling Network Specification (GMNS)](http://github.com/zephyr-data-specs/GMNS) structure

---
## 🐍 How to Configure the Environment

If you don't have Conda already, install:
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or
- [Anaconda](https://www.anaconda.com/)

Verify the installation:
```bash
conda --version
```

Create a new environment named NetBuilder:
```bash
conda create -n NetBuilder python=3.11 numpy pandas matplotlib -y
conda activate NetBuilder
```

Install Required Packages
```bash
pip install osm2gmns==1.0.1
pip install 'geopandas[all]'
pip install DTALite
```
Verify the installations:
```bash
python -c "import osm2gmns as og"
python -c "import geopandas as gpd; print('GeoPandas version:', gpd.__version__)"
python -c "import DTALite"
```
You can run the following quick test:
```bash
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import osm2gmns as og
import DTALite

print("GeoPandas version:", gpd.__version__)
print("Pandas version:", pd.__version__)
print("NumPy:", np.__version__)

```

----
## 🚦 Usage Instructions:

This project involves three main processing steps to build a connected GMNS-compatible transport network 
from shapefiles and OpenStreetMap data.
---
### 🧭 Step-by-Step zone2assignment Workflow


| Step                                      | What Needs to Happen                                                  | Role in Pipeline | How Commercial Tools Handle It | How `zone2assignment` Handles It |
|-------------------------------------------|-----------------------------------------------------------------------|------------------|-------------------------------|----------------------------------|
| 1️⃣ Define Zones (TAZ)                    | Import TAZ shapefiles, compute centroids                              | Establish demand-side structure | ✔ Auto-import via GUI or GIS layers | ✔ Accepts shapefile or CSV with clear documentation |
| 2️⃣ Prepare Physical Network              | Build directed graph with capacities, speeds, freeflow time           | Provide supply-side topology | ✔ Often from planning base maps or OSM imports | ✔ Cleaned OSM inputs; one-way links enforced |
| 3️⃣ Generate Connected Network            | Connect zones to the physical network and structure it for assignment | Integrate demand and supply for assignment | ❌ Often hidden in proprietary tools | ✔ Rule-based method:<br>• Connect each activity node to its nearest zone centroid with **bidirectional connectors** (A ➝ B, B ➝ A)<br>• For unconnected zones, link centroids to nearest network node<br>• Build Forward-Star structure |
| 4️⃣ Readiness Validation                  | Ensure valid link length, capacity, travel time                       | Prevent assignment errors | ✔ Partially enforced (warnings only) | ✔ Explicit validation; missing fields flagged |
| 5️⃣ Traffic Assignment                    | Export inputs for DTALite, etc.                              | Support modeling tools | ✔ Format-specific built-ins | ✔ Modular output for GMNS, DTALite, or custom formats |
| 6️⃣ Accessibility Check (e.g., via NEXTA) | Confirm network connectivity, completeness, and flow feasibility      | Final usability assurance for assignment tools | ✔ Often hidden within software GUIs | ✔ Independent validation module; supports visual and programmatic inspection |

### ✅ Step 1: Extract Zone Centroid Data
### 🗺️ Prepare Zone Geometry and Centroids

This step provides instructions to locate zone data and prepare the polygon geometry and centroid information. 
The output should include each zone’s **centroid coordinates** (longitude, latitude) and polygon geometry in **Well-Known Text (WKT)** format.


You can source zone (TAZ/Census Tracts) data from the following resources:

1. **Use Census Tracts as Zones**  
   Shapefiles for U.S. census tracts are available here:  
   👉 [U.S. Census Bureau - Census Tracts Shapefiles (2021)](https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2021&layergroup=Census+Tracts)

2. **City/County-specific GIS data**  
   Some cities and counties provide public access to tract shapefiles:
   - [Phoenix Census Tracts (2010)](https://koordinates.com/layer/96425-phoenix-arizona-census-tracts-2010/)
   - [Tempe Census Tracts (2020)](https://data.tempe.gov/datasets/f278c2c622c249b0a543d9cc31dba525_0/explore)

**Script:** `Read_Zone_Data.py`     
**Input:**
- Zone (TAZ/Census Tracts) shapefiles (e.g., `Census_Tract_Boundary.shp`, .dbf, .shx, .prj, etc.)

**Output:**      
- `zone_centroid.csv`
---
### ✅ Step 2: Extract Physical Network from OSM

**Script:** `Read_OSM_File.py`  
**Input:**  
- OSM `.osm` file (e.g., `data/Tempe.osm`)

**Output:** Physical network 
- `node.csv`  
- `link.csv`  

This step extracts the **physical road network** from an OSM map file and generates a base **GMNS-style network** with `node.csv` and `link.csv`.
> ℹ️ For more information about OSM file formats, see the [OpenStreetMap Wiki](https://wiki.openstreetmap.org/wiki/OSM_file_formats).

---

### ✅ Step 3: Generate Connected Network
### 🧩 Connect Zone Centroids with the Physical Network

To streamline GMNS network creation for tools like **TransCAD**, **Cube**, **VISUM**, **DTALite**, and **path4gmns**, 
this step connects **Zone centroids** to the physical network using:

- **Activity nodes** (red dots in the diagram)  
- **Connector links** (green lines)  
- **Artificial connectors** to physical nodes

This design follows the **Forward Star Structure**, where each **zone centroid** is a central hub connected to nearby network nodes, improving performance and compatibility for traffic assignment.

![Forward Star Structure](images/forward_star.png)

🔎 **Simple way to identify activity nodes**:  
An **activity node** is any node in `node.csv` that has a non-null `zone_id` value.

📘 For detailed explanation of the Forward Star Network Structure, see the  
👉 [TAPLite Wiki: Forward Star Structure – Centroid Nodes and Connectors](https://github.com/asu-trans-ai-lab/TAPLite/wiki/Forward-Star-Network-Structure%3A-Centroid-Nodes-and-Connectors)

**Script:** `Connector_Generation.py`
**Input:**  
- `node.csv`  
- `link.csv`  
- `zone_centroid.csv`

**Output (`connected_network` folder):**
- `node_updated.csv` → **Rename to** `node.csv` for DTALite compatibility
- `link_updated.csv` → **Rename to** `link.csv` for DTALite compatibility

> ⚠️ These two files are critical outputs and must be renamed to `node.csv` and `link.csv` respectively in order to be used with the DTALite traffic assignment tool.

> ✅ Finally, your connected network consisting of the final versions of `node.csv` and `link.csv`, is ready for DTALite-based traffic assignment.

---
### ✅ Step 4: Readiness Validation  
### 📋 Lightweight Use of the GMNS+ Multi-Level Validation Tool

The multi-level readiness validation framework developed by the [GMNS Plus Dataset project](https://github.com/HanZhengIntelliTransport/GMNS_Plus_Dataset) offers a rigorous and well-structured approach to verifying network completeness, attribute consistency, and simulation readiness.

To make the tool more accessible in smaller environments or for single-network testing, users may download only the essential components rather than cloning the full repository.

#### 📦 Required Files (Download These)

| File/Folder | Description |
|-------------|-------------|
| [`GMNS_Tools/`](https://github.com/HanZhengIntelliTransport/GMNS_Plus_Dataset/tree/main/GMNS_Tools) | Folder of utility functions (e.g., file parsing, attribute checks) |
| [`GMNS_Plus_Readiness_Validator.py`](https://github.com/HanZhengIntelliTransport/GMNS_Plus_Dataset/blob/main/GMNS_Plus_Readiness_Validator.py) | Core script that performs level-by-level checks |
| [`Network_Validator_Main.py`](https://github.com/HanZhengIntelliTransport/GMNS_Plus_Dataset/blob/main/Network_Validator_Main.py) | Entry point for validating one or multiple networks |

> 📁 Place these in a folder alongside your own test network folder (e.g., `test_network/`).

Your directory structure should look like this:
```text
validator_workspace/
├── GMNS_Tools/
├── GMNS_Plus_Readiness_Validator.py
├── Network_Validator_Main.py
└── test_network/
    ├── node.csv
    ├── link.csv
    ├── demand.csv
    └── settings.csv
```
---
**Run the Validator**
```bash
python Network_Validator_Main.py
```
By default, this command will scan all subdirectories (including your network folder) and validate them across Levels 1–8.

---
**To validate only a specific folder:**
Open the `Network_Validator_Main.py` file and find the following line:
```bash
subdirectories = get_all_directories('.')
```
Change it to:
```bash
subdirectories = get_all_directories('test_network')
```
This will limit the validation to the folder named `test_network/`.

**Output:**
After validation, a detailed report will be generated for each network, including:

- Console messages during the run  
- A structured summary in `validation_report.json`



> 📌 **Note:** If you have not yet created the `demand.csv` and `settings.csv` files, here are the required formats:

#### 📄 `demand.csv`

This file defines the origin-destination (OD) demand between zones in your network.

| Field       | Required | Description                               |
|-------------|----------|-------------------------------------------|
| `o_zone_id` | ✅        | Origin zone ID for the OD pair            |
| `d_zone_id` | ✅        | Destination zone ID for the OD pair       |
| `volume`    | ✅        | Number of trips from origin to destination|

#### ⚙️ `settings.csv`

This file configures key parameters for the DTALite simulation, such as:

- Routing strategy
- Assignment time interval
- Number of simulation iterations
- Demand scaling

You can customize these parameters to fit your model needs.

🔗 Refer to the official DTALite documentation for a complete list of fields, expected values, and examples:

👉 [DTALite Wiki: `settings.csv` Format](https://github.com/itsfangtang/DTALite_release/wiki/DTALite-Inputs-and-Outputs#settingscsv)


---

### ✅ Step 5: Traffic Assignment: Run the DTALite Simulation
Once your `node.csv`, `link.csv`, `demand.csv`, and `settings.csv` files are ready, run the DTALite simulation using the script below:

```bash
python DTALite_Test.py
```
This script will guide the simulation through the following phases:

🧭 Trip Generation – Identify origin and destination zones

🔄 Trip Distribution – Match trip origins to destinations

🚉 Mode Choice – Assign trips across available travel modes

🛣 Route Assignment – Map trips onto network routes

📊 Performance Evaluation – Measure volume, travel time, congestion, and accessibility

**Output:**

Running `DTALite_Test.py` will generate a series of results essential for performance analysis:

| Output File                  | Description                                                                |
|-----------------------------|----------------------------------------------------------------------------|
| `od_performance.csv`        | OD-level summary including travel time, distance, and volume              |
| `link_performance.csv`      | Link-level performance metrics (volume, speed, V/C ratio, etc.)           |
| `system_performance.csv`    | Network-wide indicators (VMT, VHT, average speed)                         |
| `origin_accessibility.csv`  | Accessibility from each origin zone                                 |
| `destination_accessibility.csv` | Accessibility for each destination zone                       |
| `inaccessible_od.csv`       | OD pairs with no feasible path (if any)                                    |
| `route_assignment.csv`      | Assigned path details and link sequences for each OD pair 
---

### ✅ Step 6: Accessibility Check  
### 🔍 Identify Unreachable OD Pairs and Network Gaps

After traffic assignment, it is essential to confirm whether **all origin-destination (OD) pairs are accessible** under the simulated network.

#### 📁 Key Output Files for Accessibility Analysis

- `inaccessible_od.csv` 
- `origin_accessibility.csv` 
- `destination_accessibility.csv`

---

#### 📄 `inaccessible_od.csv` Format

Each row contains an OD pair that could not be routed for a specific mode:

| Column                 | Description                                              |
|------------------------|----------------------------------------------------------|
| `mode_type`            | Travel mode (e.g., `auto`)                               |
| `origin_zone_id`       | Origin zone ID                                           |
| `destination_zone_id`  | Destination zone ID                                      |
| `google_maps_http_link`| Link to suggested path in Google Maps for manual review  |

This file helps flag zone pairs that may be disconnected or lack a feasible route.

---

### 🛠️ Investigating Inaccessible OD Pairs

1. 🧭 **Use Google Maps Link**  
   - Click on the `google_maps_http_link` to inspect real-world routing availability.
   - This reveals whether the issue is due to network gaps in your GMNS structure (e.g., missing links or nodes).

2. 🗺 **Visualize and Validate in NEXTA**  
   Download the latest version of the [NEXTA executable](https://github.com/asu-trans-ai-lab/NeXTA4GMNS/blob/gh-pages/release/NEXTA.exe) and use it to open your `node.csv` and `link.csv` files for interactive inspection.

   To learn how to load a GMNS network, trace OD paths, and perform accessibility checks within NEXTA, refer to the official guide:  
   👉 [NEXTA4GMNS Usage Guide – Section 5: View/Edit Network](https://github.com/asu-trans-ai-lab/NeXTA4GMNS?tab=readme-ov-file#5-viewedit-gmns-network-in-nexta)

   In NEXTA, try locating the shortest path between the origin and destination zones listed in `inaccessible_od.csv`. If no valid path appears:
   - 🧱 Compare your network to the real-world routing shown in the Google Maps link
   - 🔍 Check for missing connectors or broken links in your `link.csv`
   - 🔧 Update your GMNS files accordingly and re-run the assignment

---

## 📄GMNS Format for DTALite

Before using your output files in DTALite, please review the required [GMNS file format specifications](https://docs.google.com/document/d/146Nt9y53mUibze1Z0nezgCwtkY_4Ycb1j-wp_S86wqs/edit?usp=sharing) to ensure full compatibility.

This includes required fields and formatting for:
- `node.csv`
- `link.csv`
- `demand.csv`

> ⚠️ Files must strictly follow GMNS standards for successful DTALite traffic assignment.
---
## 💡 Use Cases for `zone2assignment`

| Use Case | Why `zone2assignment` Works Well |
|----------|----------------------------------|
| **Regional traffic modeling by MPOs and agencies** | Provides a standardized, transparent pipeline for building consistent networks across multiple cities or regions, with full control over connector generation and zone definitions. |
| **Academic research on accessibility, OD estimation, or dynamic traffic assignment (DTA)** | Enables reproducible experiments with clearly documented inputs and modular outputs; supports sensitivity testing and algorithm benchmarking. |
| **Teaching traffic modeling workflows** | Offers an intuitive, stage-based process that helps students understand the connection between spatial data and network simulation; uses readable file formats and open-source tools. |
| **Integration with AI/ML models** | Outputs GMNS-style, forward-star structured networks that are fully compatible with modern Python-based machine learning pipelines (e.g., PyTorch, scikit-learn). |

---
## 🌐 Related Projects and Applications

### 🔧 [Shp2gmns](https://github.com/yuxl7/Shp2gmns)

> *Convert Shapefiles to GMNS Format*

[Shp2gmns](https://github.com/yuxl7/Shp2gmns) is a Python-based tool designed to convert road network shapefiles into GMNS (General Modeling Network Specification) format. It simplifies the preprocessing of geospatial road data for transportation modeling, making it ideal for researchers and practitioners working with GIS-based road datasets.

You can use **Shp2gmns** as a complementary tool to this 
repository when your input data is in shapefile format instead of OSM. The generated GMNS-format files (e.g., `node.csv`, `link.csv`) can then be enriched using **this tool** (`Connector_Generation.py`) to integrate with zone data and build connected networks for DTALite or other traffic assignment workflows.

---

### 🗺️ [GMNS Plus Dataset](https://github.com/HanZhengIntelliTransport/GMNS_Plus_Dataset)

> *Standardized Multimodal GMNS Network Collection*

The [GMNS Plus Dataset](https://github.com/HanZhengIntelliTransport/GMNS_Plus_Dataset) is a curated collection of GMNS-formatted transportation networks for various cities and regions (e.g., Phoenix, Bay Area, Berlin). It is designed to support reproducible, standardized research in transportation modeling.

🔗 This repository contributes to the GMNS Plus Dataset by generating clean, connected network files through [`osm2gmns`](https://github.com/jiawlu/OSM2GMNS) processing, generating connector links between zones and the physical network, and formatting outputs for DTALite-based traffic assignment workflows.

Look for networks where this tool helped preprocess and enhance spatial linkage between zones and road infrastructure.

---
### 📦 Save or Share the Environment
To save your environment to a file:
```bash
conda env export > environment.yml
```
To recreate it later or on another machine:
```bash
conda env create -f environment.yml
conda activate transport-net-builder
```

### 📝 Notes

- Ensure all shapefile components (`.shp`, `.shx`, `.dbf`, `.prj`) are inside the `data/` folder.
- For advanced GIS operations:

```bash
pip install gdal
```
- To use Jupyter Notebook:
```bash
conda install jupyter -y
```