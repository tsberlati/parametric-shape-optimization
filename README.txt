# OptiFOAM: Multidisciplinary Design Optimization Framework

## Overview
OptiFOAM is an orchestration framework for parameter-driven geometric synthesis and computational fluid dynamics (CFD) analysis of rocket nozzles. Developed during a research internship at the CICLoPE Laboratory, it integrates parametric CAD engines (SALOME, Blender) with OpenFOAM solvers to execute Surrogate-Based Optimization (SBO) and Direct Optimization workflows.

## Prerequisites and System Requirements
The framework operates on Linux/WSL environments. System requirements include:
* **Python 3.8+**
* **OpenFOAM** (Baseline cases must be configured for the active environment)
* **SALOME** or **Blender** (Dynamic autodiscovery searches in standard system paths: `~/Salome`, `/opt/salome`, `/usr/bin/blender`)

## Python Environment Setup
The execution logic requires an isolated virtual environment to ensure deterministic dependency resolution.

1. **Initialize the virtual environment:**
   `python3 -m venv env_local`
2. **Activate the environment:**
   `source env_local/bin/activate`
3. **Install dependencies:**
   `pip install -r requirements.txt`

## Repository Structure
The framework architecture reflects the sequential operational phases:

* **`run.sh`**: Main Bash orchestrator for environment setup, cleanup, and Python execution.
* **`clear_case.sh`**: Utility script to purge simulation directories and geometric variants.
* **`01_Geometry/`**: Contains CAD interface scripts (`salome_geo.py`, `export_blender.py`) and stores generated `stl_variants/`.
* **`02_Simulation/`**: Contains the OpenFOAM `baseline/` template and hosts the transient `case_*/` execution directories.
* **`03_Data/`**: Central repository for parametric matrices (`design_points.csv`, `design_space.json`) and extracted results.
* **`scripts/`**: Contains the core Python logic (`main.py`, `config.py`, orchestrators, and data extraction modules).

## Execution Guide
The primary entry point is the main bash wrapper. The virtual environment must be active prior to execution.

`./run.sh`

This script executes optional workspace cleanup and invokes the Python Main Router (`scripts/main.py`), presenting an interactive terminal interface with three operational modes:

### Mode 1: Surrogate-Based Optimization (DOE Batch / LHS)
Executes a decoupled architecture for generating a Design of Experiments (DOE).
* **Generation:** Utilizes Latin Hypercube Sampling (LHS) based on boundaries defined in `design_space.json`. It supports parsing of manually provided `design_points.csv` matrices.
* **Phase 1 (Setup):** Instantiates physical dimensions, morphs the CAD geometry, and generates discrete OpenFOAM cases by duplicating the baseline template.
* **Phase 2 (Execution):** Automates the meshing process (`blockMesh`, `snappyHexMesh`) and executes the fluid dynamic solver (`rhoCentralFoam`). Supports parallel execution via MPI.
* **Data Extraction:** Parses log files of converged cases to extract time-averaged boundary metrics, outputting consolidated data to `03_Data/design_results.csv`.

### Mode 2: Direct Optimization (Iterative Search)
*Under active development.* Connects external gradient-based or evolutionary algorithms (e.g., SLSQP, NSGA-II) directly to the geometric engine. Analyzes spatial parameters dynamically, evaluating the cost function iteratively.

### Mode 3: Single Geometry Generation (Test Mode)
Diagnostic tool for validating CAD engine connectivity. It isolates the geometric core (`core_geometry.py`) to generate a single `.stl` file using nominal values from configuration files, without initiating the CFD sequence.

## External CLI Execution
For unsupervised execution or integration with scheduling tools, the Python router supports command-line arguments:

* **SBO Batch:** 
  `python3 scripts/main.py --mode sbo --ncases 50 --seed 42 --parallel --cores 8`
* **Data Extraction:** 
  `python3 scripts/main.py --mode extract`
