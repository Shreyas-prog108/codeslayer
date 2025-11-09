import time
from cli_logger import CLIPrinter
from load_data import load_reference_data
from product_processor import process_products
from test_processor import process_tests
from pricing_aggregator import build_output_json, save_output

def run_pricing_agent(input_json):
    cli = CLIPrinter()
    cli.info("Loading RFP data...")
    rfp_id = input_json.get("rfp_id", "Unknown")
    cli.success(f"Loaded input: {rfp_id}")

    cli.section("Loading product and test price sheets...")
    product_df, test_df = load_reference_data("Pricing_Data_FMCG.xlsx")
    cli.success("Reference sheets loaded.")

    cli.section(f"Processing {len(input_json['technical_table'])} scope items...")
    pricing_table, total_material_cost = process_products(input_json["technical_table"], product_df)
    cli.success("Calculated product pricing for all recommendations.")

    cli.section("Processing required tests...")
    matched_tests, total_test_cost = process_tests(input_json["rfp_summary"]["tests"], test_df)
    cli.success("Test costs computed and added.")

    final_output = build_output_json(rfp_id, pricing_table, matched_tests, total_material_cost, total_test_cost)
    cli.save("pricing_summary.json")
    save_output(final_output)
    cli.done("Pricing computation completed successfully!")
    return final_output
