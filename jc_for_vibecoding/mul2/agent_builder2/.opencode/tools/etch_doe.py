"""
Etch DOE local tool — Python backend for design matrix generation.
Called by .opencode/tools/etch-doe.ts via Bun subprocess.
"""

import argparse
import csv
import json
import os
import random


def generate_full_factorial(factor_count: int, levels: dict) -> dict:
    """Generate a 2-level full factorial design matrix with coded values (-1, +1)."""
    if factor_count < 1:
        return {"success": False, "error": "factor_count must be >= 1"}
    n_runs = 2 ** factor_count
    matrix = []
    factor_names = [chr(65 + i) for i in range(factor_count)]
    for run in range(n_runs):
        row = {}
        for i in range(factor_count):
            # bit i determines level: 0 -> -1, 1 -> +1
            row[factor_names[i]] = -1 if (run >> i) & 1 == 0 else 1
        row["run_order"] = run + 1
        row["std_order"] = run + 1
        matrix.append(row)
    # randomize run order
    std_orders = list(range(1, n_runs + 1))
    random.shuffle(std_orders)
    for i, row in enumerate(matrix):
        row["run_order"] = std_orders[i]
    return {
        "success": True,
        "design_type": "full_factorial",
        "factor_count": factor_count,
        "factor_names": factor_names,
        "total_runs": n_runs,
        "matrix": matrix,
    }


def generate_fractional_factorial(factor_count: int, levels: dict) -> dict:
    """Generate a 2^(k-p) fractional factorial design placeholder."""
    if factor_count < 3:
        return generate_full_factorial(factor_count, levels)
    # For now use a simple 2^(k-1) half-fraction
    n_runs = 2 ** (factor_count - 1)
    full_factor_names = [chr(65 + i) for i in range(factor_count)]
    # Generate full matrix for k-1 factors, then assign the last factor as product of the first k-2
    base_count = factor_count - 1
    matrix = []
    for run in range(2 ** base_count):
        row = {}
        for i in range(base_count):
            row[full_factor_names[i]] = -1 if (run >> i) & 1 == 0 else 1
        # generator: product of first base_count-1 factors
        product = 1
        for i in range(base_count - 1):
            product *= row[full_factor_names[i]]
        row[full_factor_names[-1]] = product
        row["run_order"] = run + 1
        row["std_order"] = run + 1
        matrix.append(row)
    std_orders = list(range(1, n_runs + 1))
    random.shuffle(std_orders)
    for i, row in enumerate(matrix):
        row["run_order"] = std_orders[i]
    return {
        "success": True,
        "design_type": "fractional_factorial",
        "factor_count": factor_count,
        "factor_names": full_factor_names,
        "total_runs": n_runs,
        "matrix": matrix,
    }


def generate_taguchi_placeholder(factor_count: int, levels: dict) -> dict:
    """Return a placeholder for Taguchi orthogonal array design."""
    return {
        "success": True,
        "design_type": "taguchi_placeholder",
        "factor_count": factor_count,
        "message": "Taguchi orthogonal array generation not yet implemented. Use full factorial or fractional factorial for now.",
        "note": "L9(3^4), L18(2^1x3^7), L27(3^13) etc. will be supported in Phase 2.",
    }


def generate_response_surface_placeholder(factor_count: int, levels: dict) -> dict:
    """Return a placeholder for CCD / Box-Behnken design."""
    return {
        "success": True,
        "design_type": "response_surface_placeholder",
        "factor_count": factor_count,
        "message": "CCD / Box-Behnken design generation not yet implemented. Use full factorial for screening first.",
        "note": "Response surface designs will be supported in Phase 3.",
    }


def analyze_results(results_csv_path: str) -> dict:
    """Placeholder for DOE results analysis."""
    if not os.path.exists(results_csv_path):
        return {"success": False, "error": f"File not found: {results_csv_path}"}
    return {
        "success": True,
        "message": "DOE results analysis not yet fully implemented.",
        "file_read": results_csv_path,
        "planned_analyses": ["main_effects", "interaction_effects", "Pareto", "ANOVA", "linear_model_fit"],
        "note": "Full statistical analysis will be available in Phase 3.",
    }


def write_csv(matrix: list, output_path: str) -> str:
    """Write design matrix to CSV file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if not matrix:
        return "No data to write."
    fieldnames = list(matrix[0].keys())
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matrix)
    return f"Written {len(matrix)} rows to {output_path}"


ACTIONS = {
    "generate_full_factorial": generate_full_factorial,
    "generate_fractional_factorial": generate_fractional_factorial,
    "generate_taguchi_placeholder": generate_taguchi_placeholder,
    "generate_response_surface_placeholder": generate_response_surface_placeholder,
    "analyze_results": analyze_results,
}


def main():
    parser = argparse.ArgumentParser(description="Etch DOE local tool")
    parser.add_argument("--action", required=True, choices=list(ACTIONS.keys()))
    parser.add_argument("--factor-count", type=int, default=2)
    parser.add_argument("--levels-json", type=str, default="{}")
    parser.add_argument("--output-dir", type=str, default="outputs/doe")
    parser.add_argument("--results-csv-path", type=str, default=None)
    args = parser.parse_args()

    levels = json.loads(args.levels_json) if args.levels_json else {}

    action_fn = ACTIONS[args.action]
    if args.action == "analyze_results":
        if not args.results_csv_path:
            print(json.dumps({"success": False, "error": "results_csv_path required for analyze_results"}))
            return
        result = action_fn(args.results_csv_path)
    else:
        result = action_fn(args.factor_count, levels)

    if result.get("success") and "matrix" in result:
        csv_path = os.path.join(args.output_dir, f"{args.action}_matrix.csv")
        write_csv(result["matrix"], csv_path)
        result["csv_path"] = csv_path

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
