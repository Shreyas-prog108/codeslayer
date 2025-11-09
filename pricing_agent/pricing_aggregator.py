import json

def build_output_json(rfp_id, pricing_table, matched_tests, total_material_cost, total_test_cost):
    overall_project_cost = total_material_cost + total_test_cost
    return {
        "rfp_id": rfp_id,
        "pricing_table": pricing_table,
        "matched_tests": matched_tests,
        "summary": {
            "total_material_cost": total_material_cost,
            "total_test_cost": total_test_cost,
            "overall_project_cost": overall_project_cost
        }
    }

def save_output(output, path="pricing_summary.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
