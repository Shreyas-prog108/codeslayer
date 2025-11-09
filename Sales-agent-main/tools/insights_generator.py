def generate_sales_insight(region: str = "India"):
    insights = {
        "India": "Detergent sales are up 12% this month.",
        "South": "Shampoo sales dropped slightly due to seasonality."
    }
    return insights.get(region, "No insights available for this region.")
