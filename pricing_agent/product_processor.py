def process_products(technical_table, product_df):
    pricing_table = []
    total_material_cost = 0

    for line in technical_table:
        line_id = line["line_id"]
        scope_item = line["scope_item"]
        quantity = line["quantity"]
        recommended = line["recommended"]

        line_entry = {
            "line_id": line_id,
            "scope_item": scope_item,
            "quantity": quantity,
            "recommended_pricing": []
        }

        best_match = None
        highest_spec = -1

        for rec in recommended:
            sku = rec["sku"]
            spec_match = rec["spec_match"]
            row = product_df.loc[product_df["SKU_ID"] == sku]

            if row.empty:
                continue

            base_price = float(row["Base_Price"].values[0])
            product_name = row["Product_Name"].values[0]
            unit = row["Unit_of_Measure"].values[0]
            product_type = row["Product_Type"].values[0]
            total_price = base_price * quantity

            line_entry["recommended_pricing"].append({
                "sku": sku,
                "spec_match": spec_match,
                "product_name": product_name,
                "base_price": base_price,
                "unit": unit,
                "product_type": product_type,
                "total_price": total_price
            })

            if spec_match > highest_spec:
                highest_spec = spec_match
                best_match = {"sku": sku, "total_price": total_price}

        if best_match:
            line_entry["included_sku"] = best_match["sku"]
            line_entry["included_total_price"] = best_match["total_price"]
            total_material_cost += best_match["total_price"]

        pricing_table.append(line_entry)

    return pricing_table, total_material_cost
