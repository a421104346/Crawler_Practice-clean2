import csv
import os
import sys

# Set stdout encoding to utf-8 to prevent garbled text on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

# Define input and output file paths
input_file = r"D:\projects\WebCrawler\prosetting\output\cs2_prosettings.csv"
output_file = r"D:\projects\WebCrawler\prosetting\output\player_mouse_settings.csv"

# Target column names to extract
target_columns = ["Player", "Mouse", "HZ", "DPI", "Sens", "eDPI", "Zoom Sens"]

try:
    if not os.path.exists(input_file):
        print(f"Error: Input file not found {input_file}")
        sys.exit(1)

    print(f"Reading: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        
        # Check if CSV contains all target columns
        missing_columns = [col for col in target_columns if col not in reader.fieldnames]
        if missing_columns:
            print(f"Error: Missing columns in input file: {missing_columns}")
            print(f"Available columns: {reader.fieldnames}")
            sys.exit(1)
            
        # Extract data
        extracted_data = []
        for row in reader:
            filtered_row = {col: row[col] for col in target_columns}
            extracted_data.append(filtered_row)
            
    print(f"Extracted {len(extracted_data)} rows.")

    # Write to new CSV
    if extracted_data:
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=target_columns)
            writer.writeheader()
            writer.writerows(extracted_data)
        print(f"New file saved to: {output_file}")
    else:
        print("No data extracted.")

except Exception as e:
    print(f"Error occurred: {e}")
