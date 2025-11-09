def process_tests(test_list, test_df):
    matched_tests = []
    total_test_cost = 0

    for test_name in test_list:
        row = test_df.loc[test_df["Test_Name"] == test_name]
        if not row.empty:
            info = {
                "test_name": test_name,
                "test_type": row["Test_Type"].values[0],
                "unit_cost": float(row["Unit_Cost"].values[0]),
                "duration_days": int(row["Duration (days)"].values[0])
            }
            matched_tests.append(info)
            total_test_cost += info["unit_cost"]

    return matched_tests, total_test_cost
