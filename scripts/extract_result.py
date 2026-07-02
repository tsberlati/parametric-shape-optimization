import os
import pandas as pd
import glob
import config
import numpy as np

def is_case_converged(case_dir):
    """Verifies simulation convergence by checking OpenFOAM log files."""
    log_files = glob.glob(os.path.join(case_dir, "log.*"))
    # Exclude mesh generation and domain decomposition logs
    exclude = ["blockMesh", "decomposePar", "reconstructPar", "surfaceFeatureExtract", "snappyHexMesh"]
    
    for lf in log_files:
        if not any(ex in os.path.basename(lf) for ex in exclude):
            if os.path.exists(lf):
                with open(lf, 'r') as f:
                    content = f.read()
                    # Check for normal termination and absence of fatal errors
                    if "End" in content and "FOAM FATAL ERROR" not in content:
                        return True
    return False

def get_averaged_value(filepath, target_idx, t_start, t_stop):
    """Calculates the time-averaged value based on a certified exact domain."""
    if not os.path.exists(filepath): return np.nan
    with open(filepath, 'r') as f:
        # Ignore commented lines
        lines = [l for l in f.readlines() if not l.startswith('#') and l.strip()]
    
    if not lines: return np.nan
    
    values = []
    for line in lines:
        parts = line.replace('(', '').replace(')', '').split()
        try:
            time_val = float(parts[0]) # Column 0 in OpenFOAM .dat files represents Time
            if time_val >= t_start and time_val <= t_stop:
                values.append(float(parts[target_idx]))
        except (IndexError, ValueError): 
            continue
    
    return float(np.mean(values)) if values else np.nan

def extract_results(): 
    """Main execution entry point for data extraction."""
    df = pd.read_csv(config.CSV_FILE, comment='#')
    
    # Pre-fill DataFrame columns with NaN
    for key in config.POST_PROCESSING.keys():
        df[key] = np.nan
    
    for i in range(1, len(df) + 1):
        case_id = f"case_{i:03d}"
        case_dir = os.path.join(config.DIRS["simulation"], case_id)
        
        # Guard clause: process only converged simulations
        if not is_case_converged(case_dir):
            continue
            
        for key, params in config.POST_PROCESSING.items():
            folder, filename, idx = params
            path = os.path.join(case_dir, "postProcessing", folder)
            
            # Find the most recent time directory
            time_dirs = sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))], key=float)
            if not time_dirs: continue
            
            target = os.path.join(path, time_dirs[-1], filename)
            df.loc[i-1, key] = get_averaged_value(target, idx, config.T_START_AVG, config.T_STOP_AVG)
            
    # Apply dynamic derived metrics if specified in config
    if hasattr(config, 'DERIVED_METRICS'):
        for new_col, func in config.DERIVED_METRICS.items():
            df[new_col] = df.apply(func, axis=1)

    df.to_csv(os.path.join(config.DIRS["data"], "design_results.csv"), index=False)
    print("Workflow: Extraction complete.")
    return df