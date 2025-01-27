import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from concurrent.futures import ProcessPoolExecutor

# Base URL
base_url = "https://www.vlr.gg"

# Folder to save the CSV files
output_folder = "match_results"

# Create if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# List of User-Agent strings for randomization so the website doesn't block me ;(
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/102.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0",
]

# Function to generate random headers
def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": base_url,
    }

# Function to process a single match
def process_match(url):
    try:
        response = requests.get(url, headers=get_headers())
        soup = BeautifulSoup(response.text, "html.parser")

        # Match event
        match_event_div = soup.find("div", class_="match-header-event-series")
        match_event = " ".join(match_event_div.text.split()).strip() if match_event_div else "N/A"

        # Match stage
        match_stage_div = soup.find("div", style="font-weight: 700;")
        match_stage = match_stage_div.text.strip() if match_stage_div else "N/A"

        # Match date
        match_date_div = soup.find("div", class_="moment-tz-convert")
        match_date = match_date_div["data-utc-ts"].split(" ")[0] if match_date_div else "N/A"

        # Teams and scores
        match_teams = soup.find_all("div", class_="wf-title-med")
        if len(match_teams) >= 2:
            team1 = match_teams[0].text.strip()
            team2 = match_teams[1].text.strip()
        else:
            team1 = team2 = "N/A"

        scoreboard = soup.find("div", class_="js-spoiler")
        if scoreboard:
            scores = scoreboard.find_all("span")
            team1_score = scores[0].text.strip() if scores else "N/A"
            team2_score = scores[-1].text.strip() if scores else "N/A"
        else:
            team1_score = team2_score = "N/A"

        # Determine winner
        teams_score = {team1: team1_score, team2: team2_score}
        winner = max(teams_score, key=teams_score.get, default="N/A")

        # Return match data
        return {
            "Match Event": match_event,
            "Match Stage": match_stage,
            "Match Date": match_date,
            "Team 1": team1,
            "Team 2": team2,
            "Team 1 Score": team1_score,
            "Team 2 Score": team2_score,
            "Winner": winner,
        }
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

# Fetch all match URLs from a specific results page
def get_match_urls(page_num):
    results_url = f"{base_url}/matches/results?page={page_num}"
    headers = get_headers()
    response = requests.get(results_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    matches = soup.find_all('a', class_='wf-module-item')
    return [base_url + link['href'] for link in matches if 'href' in link.attrs]

# Save matches from a specific page to a CSV file
def save_page_to_csv(page_num):
    try:
        match_urls = get_match_urls(page_num)

        # Process all matches in the page
        with ProcessPoolExecutor() as executor:
            match_data = list(filter(None, executor.map(process_match, match_urls)))

        # Save the match data to a CSV file
        csv_file = os.path.join(output_folder, f"matches_page_{page_num}.csv")
        df = pd.DataFrame(match_data)
        df.to_csv(csv_file, index=False)
        print(f"Page {page_num} data saved to {csv_file}")
    except Exception as e:
        print(f"Error saving page {page_num}: {e}")

if __name__ == "__main__":
    # Start timer
    start_time = time.time()

    # Number of pages to fetch
    results_final_page_num = 1

    # Process each page and save to CSV
    for page_num in range(1, results_final_page_num + 1):
        save_page_to_csv(page_num)

    # End timer
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"All pages saved. Elapsed time: {elapsed_time:.2f} seconds")
