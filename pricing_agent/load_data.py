import pandas as pd

def load_reference_data(excel_path: str):
    """Load both product and test price sheets from a single workbook."""
    try:
        product_prices = pd.read_excel(excel_path, sheet_name="Product_Prices")
        test_prices = pd.read_excel(excel_path, sheet_name="Test_Prices")

        return product_prices, test_prices

    except Exception as e:
        print(f"❌ Error loading reference data: {e}")
        raise
