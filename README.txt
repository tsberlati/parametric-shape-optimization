# OptiFOAM: Multidisciplinary Design Optimization Framework

OptiFOAM is an automated orchestration framework designed for parameter-driven geometric synthesis and computational fluid dynamics (CFD) analysis. It couples parametric CAD engines (SALOME, Blender) with OpenFOAM solvers to enable Surrogate-Based Optimization (SBO) and Direct Optimization workflows.

## Prerequisites and System Requirements

The framework operates on Linux/WSL environments and requires the following system-level software:
* **Python 3.8+**
* **OpenFOAM** (Baseline cases must be configured for the active OpenFOAM environment)
* **SALOME** or **Blender** (Dynamic autodiscovery searches in standard system paths like `~/Salome`, `/opt/salome`, `/usr/bin/blender`)

## Python Environment Setup

The execution logic relies on an isolated virtual environment to ensure deterministic dependency resolution.

**1. Initialize the virtual environment:**
Run the following command in the project root:
`python3 -m venv env_local`

**2. Activate the environment:**
`source env_local/bin/activate`

**3. Install dependencies:**
`pip install -r requirements.txt`

## Repository Structure

The framework is strictly organized into sequential operational phases:

* `run.sh`: Main Bash orchestrator for environment setup, cleanup, and Python execution.
* `clear_case.sh`: Utility script for purging simulation directories and geometric variants.
* `01_Geometry/`: Contains CAD interface scripts (`salome_geo.py`, `export_blender.py`) and stores generated `stl_variants/`.
* `02_Simulation/`: Contains the OpenFOAM `baseline/` template and hosts the transient `case_*/` execution directories.
* `03_Data/`: Central repository for parametric matrices (`design_points.csv`, `design_space.json`) and extracted results.
* `scripts/`: Contains the core Python logic (`main.py`, `config.py`, orchestrators, and data extraction modules).

## Execution Guide

The primary entry point is the main bash wrapper. Ensure the virtual environment is activated prior to execution.

`./run.sh`

This script performs optional workspace cleanup and invokes the Python Main Router (`scripts/main.py`), presenting an interactive terminal interface with three distinct operational modes:

### Mode 1: Surrogate-Based Optimization (DOE Batch / LHS)
Executes a decoupled architecture for generating a Design of Experiments (DOE).
* **Generation:** Uses Latin Hypercube Sampling (LHS) based on boundaries defined in `design_space.json`. Alternatively, it can parse an existing manually provided `design_points.csv` matrix.
* **Phase 1 (Setup):** Instantiates physical dimensions and morphs the CAD geometry. Generates discrete OpenFOAM cases copying the baseline template.
* **Phase 2 (Execution):** Automates the meshing process (`blockMesh`, `snappyHexMesh`) and runs the fluid dynamic solver (e.g., `rhoCentralFoam`). Supports parallel execution via MPI.
* **Data Extraction:** Automatically parses the log files of converged cases to extract time-averaged boundary metrics, saving the consolidated output in `03_Data/design_results.csv`.

### Mode 2: Direct Optimization (Iterative Search)
*Under active development.* Connects external gradient-based or evolutionary algorithms (e.g., SLSQP, NSGA-II) directly to the geometric engine. Analyzes the spatial parameters dynamically, calculating a cost function iteratively.

### Mode 3: Single Geometry Generation (Test Mode)
Diagnostic tool to validate the CAD engine connectivity. It isolates the geometric core (`core_geometry.py`) and generates a single standard `.stl` file using the nominal values defined in the configuration files, without triggering the CFD sequence.

## External CLI Execution

For unsupervised execution or integration with external scheduling tools, the Python router supports command-line arguments:

* **SBO Batch:** `python3 scripts/main.py --mode sbo --ncases 50 --seed 42 --parallel --cores 8`
* **Data Extraction:** `python3 scripts/main.py --mode extract`