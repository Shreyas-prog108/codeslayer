from pricing_agent import run_pricing_agent
import json

if __name__ == "__main__":
    print("\n🚀 Starting Pricing Agent...\n")

    with open("data/sample_input.json", "r") as f:
        input_json = json.load(f)

    result = run_pricing_agent(input_json)

    print("\n✅ Final pricing summary written to pricing_summary.json")
