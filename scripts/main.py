import sys
import argparse
import config
import os
import glob
from pipeline_sbo import run_sbo_workflow
from pipeline_opt import run_optimization_workflow
from core_geometry import GeometryEngine
import extract_result

class Col:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    WHITE_BOLD = '\033[1;37m'
    END = '\033[0m'

def print_header():
    print(f"\n{Col.BOLD}{Col.CYAN}======================================================{Col.END}")
    print(f"{Col.BOLD}{Col.CYAN}      OPTIMIZATION FRAMEWORK - MAIN ROUTER            {Col.END}")
    print(f"{Col.BOLD}{Col.CYAN}======================================================{Col.END}")

def interactive_menu():
    """Text-based menu for manual execution via terminal."""
    print_header()
    print("Select operating mode:")
    print(f"  {Col.BOLD}[1]{Col.END} Surrogate-Based Optimization (DOE Batch / LHS)")
    print(f"  {Col.BOLD}[2]{Col.END} Direct Optimization (Iterative Search)")
    print(f"  {Col.BOLD}[3]{Col.END} Single Geometry Generation (Test Mode)")
    
    choice = input(f"\n{Col.YELLOW}Choice [1-3]: {Col.END}").strip()
    
    if choice == '1':
        use_manual = False
        
        if os.path.exists(config.CSV_FILE):
            print(f"\n{Col.YELLOW}[FILE FOUND]{Col.END} Database '{os.path.basename(config.CSV_FILE)}' detected.")
            csv_choice = input(" > Use existing file (Manual DOE) [M] or overwrite with new LHS [O]? ").strip().upper()
            if csv_choice == 'M':
                use_manual = True

        try:
            n_cases = 0
            seed = 42
            if not use_manual:
                n_cases = int(input(" > How many cases for the DOE? "))
                seed = int(input(" > Enter the Seed for LHS: "))
                
            # Request parallel execution parameters
            parallel_choice = input(f" > Execute CFD simulations in parallel? [y/N]: ").strip().lower()
            parallel_mode = parallel_choice == 'y'
            n_cores = 1
            if parallel_mode:
                n_cores = int(input(f" > Number of cores to use: "))
                
            run_sbo_workflow(n_cases, seed, use_manual=use_manual, parallel=parallel_mode, cores=n_cores)
            
        except ValueError:
            print(f"{Col.RED}[ERROR] Please enter valid integers.{Col.END}")
            sys.exit(1)
            
    elif choice == '2':
        print("\nAvailable Optimization Algorithms:")
        print("  [1] Genetic Algorithm (NSGA-II)")
        print("  [2] Gradient Descent (SLSQP)")
        
        algo_choice = input(f"{Col.YELLOW}Select algorithm [1-2]: {Col.END}").strip()
        algo_map = {'1': 'NSGA-II', '2': 'SLSQP'}
        
        if algo_choice in algo_map:
            run_optimization_workflow(algo_map[algo_choice])
        else:
            print(f"{Col.RED}[ERROR] Invalid choice.{Col.END}")
            sys.exit(1)
            
    elif choice == '3':
        print("\nGenerating a single geometry (Baseline/Nominal values).")
        engine = GeometryEngine()
        print(f" > Detected CAD Engine: {Col.BOLD}{Col.YELLOW}{engine.cad_mode}{Col.END}")
        
        test_params = {}
        if engine.cad_mode == "SALOME":
            for k, v in config.CAD_PARAMETERS.items():
                if v["type"] == "perturbation":
                    test_params[k] = float(v["nominal"])
                elif v["type"] == "range":
                    test_params[k] = round((v["min"] + v["max"]) / 2.0, 3)
        elif engine.cad_mode == "BLENDER":
            keys = engine.get_parameters_keys()
            test_params = {k: 0.5 for k in keys}
                
        print(f" > Test parameters generated: {test_params}")
        
        success, path, log = engine.generate_single_stl("geom_test_001", test_params)
        if success:
            print(f"{Col.GREEN}Geometry generated successfully: {path}{Col.END}\n")
        else:
            print(f"{Col.RED}Generation error: {log}{Col.END}\n")
            
    else:
        print(f"{Col.RED}Invalid choice. Exiting.{Col.END}")
        sys.exit(1)

def parse_arguments():
    """
    Command Line Interface (CLI) parser. 
    Allows unsupervised execution by external optimizers.
    """
    parser = argparse.ArgumentParser(description="MDO Geometry & Optimization Framework")
    
    parser.add_argument('--mode', type=str, choices=['sbo', 'opt', 'single', 'extract'], 
                        help="Execution mode (sbo=Batch DOE, opt=Direct Optimization, single=Single Geometry, extract=Extract Results)")
    parser.add_argument('--ncases', type=int, help="Number of geometries to generate (for mode=sbo)")
    parser.add_argument('--seed', type=int, default=42, help="Seed for LHS sampling (for mode=sbo)")
    
    parser.add_argument('--parallel', action='store_true', help="Enable parallel CFD execution")
    parser.add_argument('--cores', type=int, default=1, help="Number of cores for parallel computing")
    
    parser.add_argument('--algo', type=str, default='SLSQP', help="Optimization algorithm (for mode=opt)")
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    if len(sys.argv) == 1:
        interactive_menu()
    else:
        if args.mode == 'sbo':
            if not args.ncases:
                print(f"{Col.RED}[ERROR] --ncases is mandatory in SBO mode.{Col.END}")
                sys.exit(1)
            run_sbo_workflow(args.ncases, args.seed, parallel=args.parallel, cores=args.cores)
            
        elif args.mode == 'opt':
            run_optimization_workflow(args.algo)
            
        elif args.mode == 'single':
            print("Single CLI mode is not yet wired to accept complex spatial parameters via terminal.")
            sys.exit(0)
            
        elif args.mode == 'extract':
            print(f"\n{Col.BOLD}{Col.CYAN}--- RESULTS EXTRACTION PHASE ---{Col.END}")
            search_pattern = os.path.join(config.DIRS["simulation"], "case_*")
            n_cases_found = len(glob.glob(search_pattern))

            if n_cases_found > 0:
                print(f" > Detected {n_cases_found} cases. Starting data aggregation and post-processing...")
                try:
                    df_results = extract_result.extract_results()
                    print(f"{Col.GREEN}Consolidated database saved in: {config.DIRS['data']}/design_results.csv{Col.END}\n")
                except Exception as e:
                    print(f"{Col.RED}[ERROR] Processing failed: {e}{Col.END}\n")
                    sys.exit(1)
            else:
                print(f"{Col.RED}[ERROR] No simulation directory detected.{Col.END}\n")
                sys.exit(1)

if __name__ == "__main__":
    main()