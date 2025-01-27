import os
import pandas as pd

# Input folder containing the CSV files
input_folder = "match_results"

# Output folder for the combined CSV file
output_folder = "combined_match_results"
os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist

# Ensure the input folder exists
if not os.path.exists(input_folder):
    print(f"Folder '{input_folder}' does not exist.")
    exit()

# List to store data from all CSVs
all_data = []

# Iterate through all CSV files in the folder
for file_name in os.listdir(input_folder):
    if file_name.endswith(".csv"):
        file_path = os.path.join(input_folder, file_name)
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            all_data.append(df)
            print(f"Loaded {file_name} with {len(df)} rows.")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

# Combine all data into a single DataFrame
if not all_data:
    print("No CSV files were found or loaded.")
    exit()

combined_df = pd.concat(all_data, ignore_index=True)

# Ensure the "Match Date" column exists and sort by date
if "Match Date" in combined_df.columns:
    combined_df["Match Date"] = pd.to_datetime(combined_df["Match Date"], errors="coerce")
    combined_df = combined_df.sort_values("Match Date")
else:
    print("No 'Match Date' column found in the combined data.")
    exit()

# Extract the oldest and newest dates
oldest_date = combined_df["Match Date"].min().strftime("%Y-%m-%d")
newest_date = combined_df["Match Date"].max().strftime("%Y-%m-%d")

# Define the output file path
output_file = os.path.join(output_folder, f"all_match_results_{oldest_date}_to_{newest_date}.csv")

# Save the combined data to a new CSV file
combined_df.to_csv(output_file, index=False)
print(f"Combined CSV saved as '{output_file}'.")
