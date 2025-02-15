import os
import pandas as pd

# -----------------------------------------
# Combine match_results
# -----------------------------------------
input_folder_matches = "match_results"
output_folder_matches = "combined_match_results"
os.makedirs(output_folder_matches, exist_ok=True)

all_data_matches = []

# Read each CSV file from match_results
for file_name in os.listdir(input_folder_matches):
    if file_name.endswith(".csv"):
        file_path = os.path.join(input_folder_matches, file_name)
        try:
            df = pd.read_csv(file_path)
            all_data_matches.append(df)
            print(f"Loaded {file_name} with {len(df)} rows.")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

# Combine if we have data
if all_data_matches:
    combined_df_matches = pd.concat(all_data_matches, ignore_index=True)
    
    # Check if "Match Date" exists
    if "Match Date" in combined_df_matches.columns:
        combined_df_matches["Match Date"] = pd.to_datetime(
            combined_df_matches["Match Date"], errors="coerce"
        )
        combined_df_matches = combined_df_matches.sort_values("Match Date")
        
        oldest_date = combined_df_matches["Match Date"].min().strftime("%Y-%m-%d")
        newest_date = combined_df_matches["Match Date"].max().strftime("%Y-%m-%d")
        
        output_file_matches = os.path.join(
            output_folder_matches,
            f"all_match_results_{oldest_date}_to_{newest_date}.csv"
        )
    else:
        output_file_matches = os.path.join(
            output_folder_matches,
            "all_match_results_combined.csv"
        )
    
    # Save combined DataFrame
    combined_df_matches.to_csv(output_file_matches, index=False)
    print(f"Combined CSV saved as '{output_file_matches}'.")
else:
    print("No CSV files were found or loaded in match_results.")

# -----------------------------------------
# Combine player_results
# -----------------------------------------
input_folder_players = "player_results"
output_folder_players = "combined_player_results"
os.makedirs(output_folder_players, exist_ok=True)

all_data_players = []

# Read each CSV file from player_results
for file_name in os.listdir(input_folder_players):
    if file_name.endswith(".csv"):
        file_path = os.path.join(input_folder_players, file_name)
        try:
            df = pd.read_csv(file_path)
            all_data_players.append(df)
            print(f"Loaded {file_name} with {len(df)} rows.")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

# Combine if we have data
if all_data_players:
    combined_df_players = pd.concat(all_data_players, ignore_index=True)
    
    # Check if "Match Date" exists
    if "Match Date" in combined_df_matches.columns:
        output_file_players = os.path.join(
            output_folder_players,
            f"all_player_results_{oldest_date}_to_{newest_date}.csv"
        )
    else:
        output_file_players = os.path.join(
            output_folder_players,
            "all_player_results_combined.csv"
        )
    
    # Save combined DataFrame
    combined_df_players.to_csv(output_file_players, index=False)
    print(f"Combined CSV saved as '{output_file_players}'.")
else:
    print("No CSV files were found or loaded in player_results.")
