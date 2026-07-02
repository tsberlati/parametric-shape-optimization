# Parametric Aerodynamic Shape Optimization Framework

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenFOAM](https://img.shields.io/badge/OpenFOAM-Tested-orange)

> **Note:** Developed during a research internship at the CICLoPE Laboratory.

## Overview
This repository contains a generalized orchestration framework for parameter-driven aerodynamic shape optimization and computational fluid dynamics (CFD) analysis. It integrates parametric CAD engines (SALOME, Blender) and analytical surface generators with OpenFOAM solvers to execute Surrogate-Based Optimization (SBO) and Direct Optimization workflows across arbitrary fluid domains.

---

## Software Environment
The framework has been tested and validated with the following software stack:
* **OpenFOAM:** v2406
* **Blender:** 4.1 (for surface morphing)
* **SALOME:** 9.15.0 (for B-Rep construction)

### Python Environment Setup
Execution logic requires dependency resolution prior to launching the framework. The virtual environment is **not** included in the repository and must be created locally by the user.

1. **Create and activate a new virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```
2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## Repository Structure
The framework architecture is modular and reflects sequential operational phases:

* **`run.sh`**: Main Bash orchestrator for optional workspace cleanup and Python router execution.
* **`clear_case.sh`**: Utility script to purge transient simulation directories (`case_*`), STLs, and CSV matrices.
* **`01_Geometry/`**: Contains CAD interface scripts defining the aerodynamic shape:
  * `export_blender.py`: Headless surface morphing via Shape Keys and `bmesh` topology sanitization.
  * `export_salome.py`: B-Rep geometry manipulation handling `.xao` parallelization via PID injection.
  * `genSTR.py`: Example of an analytical surface generation script and OpenFOAM dictionary integration.
* **`02_Simulation/`**: Contains the OpenFOAM `baseline/` template (hosting standard `0/`, `constant/`, `system/` directories) and serves as the working directory for generated `case_*/` folders. **The included baseline is pre-configured for the simulation of a conical converging-diverging nozzle.**
* **`03_Data/`**: Central repository for variable bounds (`design_space.json`), Design of Experiments matrices (`design_points.csv`), and extracted performance metrics (`design_results.csv`).
* **`scripts/`**: Contains the core Python logic:
  * `main.py`: CLI router and entry point.
  * `config.py`: Executable autodiscovery and global path definitions.
  * `core_geometry.py`: Geometric engine routing Subprocess calls to the active CAD tool.
  * `pipeline_sbo.py`: Decoupled Surrogate-Based Optimization orchestrator (LHS sampling, geometry cloning, MPI parallel CFD execution).
  * `pipeline_opt.py`: Direct iterative optimization architecture.
  * `extract_result.py`: Convergence validation and time-averaged output data extraction based on defined metrics in `config.py`.

---

## Execution Guide
The primary entry point is the main bash wrapper. The virtual environment must be active prior to execution.

```bash
./run.sh
```

The interactive terminal interface presents three operational modes:

### Mode 1: Surrogate-Based Optimization (DOE Batch / LHS)
Executes a decoupled architecture for generating a Design of Experiments via `scripts/pipeline_sbo.py`.
* **Generation:** Utilizes Latin Hypercube Sampling (LHS) based on geometric boundaries defined in `design_space.json`. Supports parsing of manually provided CSV matrices.
* **Phase 1 (Setup):** Instantiates physical dimensions, calls the selected CAD engine for STL generation, and sets up discrete OpenFOAM cases.
* **Phase 2 (Execution):** Automates the meshing process and executes the configured fluid dynamic solver. Supports parallel execution via MPI.
* **Data Extraction:** Parses OpenFOAM logs to extract and time-average target metrics (e.g., forces, mass flow, aerodynamic coefficients), saving consolidated data to `design_results.csv`.
* **Optimization:** *Under active development.*

### Mode 2: Direct Optimization (Iterative Search)
*Under active development.* Managed via `scripts/pipeline_opt.py`. Connects external numerical optimization algorithms directly to the geometric engine to evaluate spatial parameters dynamically against a defined cost function.

### Mode 3: Single Geometry Generation (Test Mode)
Diagnostic tool for validating CAD engine connectivity. Isolates `core_geometry.py` to generate a single `.stl` file using nominal parameter values without initiating the full CFD sequence.

---
