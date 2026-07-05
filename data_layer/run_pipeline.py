"""
Pipeline execution script for AI Workforce Intelligence Agent.
Generates all datasets, cleans/standardizes them, and runs structural & business validation checks.
"""

import sys
from data_layer.generator import generate_datasets
from data_layer.cleaner import run_cleaner_pipeline
from data_layer.business_validator import run_business_validation

def run_pipeline() -> int:
    """Runs data generation, cleaning, structural validation, and business rules validation."""
    print("=" * 60)
    print("      AI Workforce Intelligence Agent - Data Pipeline Orchestrator  ")
    print("=" * 60)
    
    # 1. Generate Datasets
    print("\n--- Phase 1: Generating Raw Datasets ---")
    try:
        generate_datasets(seed=42)
        print("[SUCCESS] Raw datasets generated successfully.")
    except Exception as e:
        print(f"[ERROR] Error during dataset generation: {e}")
        return 1

    # 2. Clean and Standardize Datasets (includes structural verification)
    print("\n--- Phase 2: Cleaning & Standardizing Datasets ---")
    try:
        clean_success = run_cleaner_pipeline()
        if not clean_success:
            print("[WARNING] Cleaner validation checks raised alerts.")
    except Exception as e:
        print(f"[ERROR] Unexpected error during cleaning: {e}")
        return 1

    # 3. Business Validation Rules & Insights
    print("\n--- Phase 3: Running Business Rules Validation ---")
    try:
        validation_results = run_business_validation()
        status = validation_results.get("status", "FAIL")
        if status == "PASS":
            print("[SUCCESS] Business validation PASSED! No critical business errors found.")
        else:
            print(f"[FAIL] Business validation FAILED with {len(validation_results.get('errors', []))} error(s).")
            return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error during business validation: {e}")
        return 1

    print("\n" + "=" * 60)
    print("      Pipeline Orchestration Completed Successfully!  ")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(run_pipeline())
