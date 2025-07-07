import pandas as pd
from pathlib import Path

# Set paths
EXCEL_FILE = Path("tlms_dummy_data.xlsx")  # Place your Excel file in project root
JSON_OUTPUT = Path("data/tools_dataset.json") 

# Read and convert
try:
    df = pd.read_excel(EXCEL_FILE)
    json_data = df.to_json(orient='records', indent=2)
    
    # Ensure data directory exists
    JSON_OUTPUT.parent.mkdir(exist_ok=True)
    
    # Write formatted JSON
    with open(JSON_OUTPUT, 'w') as f:
        f.write('{"tools": ')
        f.write(json_data)
        f.write('}')
        
    print(f"Success! JSON saved to {JSON_OUTPUT}")

except FileNotFoundError:
    print(f"Error: Excel file not found at {EXCEL_FILE}")
except Exception as e:
    print(f"Conversion failed: {str(e)}")