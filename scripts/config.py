import os
import glob
import shutil
import json
import pandas as pd

# --- PORTABLE EXECUTABLE AUTODISCOVERY ---
def auto_detect_salome():
    """Dynamically searches for the Salome executable in the system."""
    if shutil.which("salome"):
        return shutil.which("salome")
        
    home = os.path.expanduser("~")
    search_dirs = [
        os.path.join(home, "Salome"),
        os.path.join(home, "salome"),
        "/opt/salome",
        "/opt/Salome"
    ]
    
    for base_dir in search_dirs:
        if os.path.exists(base_dir):
            pattern = os.path.join(base_dir, "**", "salome")
            matches = glob.glob(pattern, recursive=True)
            valid_matches = [m for m in matches if os.path.isfile(m) and os.access(m, os.X_OK)]
            valid_matches.sort(key=len)
            if valid_matches:
                return valid_matches[0]
                
    raise FileNotFoundError("Executable 'salome' not found in standard directories.")

# --- SYSTEM EXECUTABLES ---
BLENDER_PATH = shutil.which("blender") or "/usr/bin/blender"
SALOME_PATH = auto_detect_salome()

# --- BASE PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- DIRECTORY MAPPING ---
DIRS = {
    "geometry": os.path.join(BASE_DIR, "01_Geometry"),
    "simulation": os.path.join(BASE_DIR, "02_Simulation"),
    "data": os.path.join(BASE_DIR, "03_Data"),
    "output_stl": os.path.join(BASE_DIR, "01_Geometry", "stl_variants"),
    "runs": os.path.join(BASE_DIR, "02_Simulation") 
}

# --- SPECIFIC FILES ---
FILES = {
    "design_points": os.path.join(DIRS["data"], "design_points.csv"),
    "design_space": os.path.join(DIRS["data"], "design_space.json"), 
    "export_script_blender": os.path.join(DIRS["geometry"], "export_blender.py"),
    "export_script_salome": os.path.join(DIRS["geometry"], "export_salome.py"),
    "salome_raw_dump": os.path.join(DIRS["geometry"], "salome_geo.py"), 
    "baseline": os.path.join(DIRS["simulation"], "baseline") 
}

CSV_FILE = FILES["design_points"]

# --- CAD DESIGN SPACE ---
if os.path.exists(FILES["design_space"]):
    with open(FILES["design_space"], 'r') as f:
        CAD_PARAMETERS = json.load(f)
else:
    CAD_PARAMETERS = {}

# --- PHYSICAL PARAMETERS & SCALING ---
T_START_AVG = 0.00095  # Lower limit of the static averaging window [s]
T_STOP_AVG  = 0.00150  # Upper limit of the static averaging window [s]
WEDGE_FACTOR = 72.0    # 360 deg / 5 deg total wedge
 
# --- OPENFOAM DATA EXTRACTION MAP ---
# Note: Data files already contain total integrated values (multiplied by WEDGE_FACTOR)
POST_PROCESSING = {
    "MassFlow_Total": ("exitPlaneMassFlow", "surfaceFieldValue.dat", 1),
    "Thrust_Total": ("thrustIntegral", "surfaceFieldValue.dat", 1) 
}