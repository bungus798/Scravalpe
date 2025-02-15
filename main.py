"""
    Author: Angus Yeung
    Date: 2025-02-15
    Description: This script scrapes match results from vlr.gg and saves them to CSV files.
"""
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from concurrent.futures import ProcessPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Base URL
base_url = "https://www.vlr.gg"

# Folder to save the CSV files
match_results_folder = "match_results"
player_results_folder = "player_results"
# Create if it doesn't exist
os.makedirs(match_results_folder, exist_ok=True)
os.makedirs(player_results_folder, exist_ok=True)

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

# Initialize the Chrome driver
options = Options()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Possibly disable images, notifications, etc.
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

user_agent = random.choice(USER_AGENTS)
options.add_argument(f"user-agent={user_agent}")

service = Service("/Users/anguskongyeung/Documents/Angus' Folder/Personal/Coding/Scravalpe/chromedriver")

def create_driver():
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_round_data(map_element):
    # Get the player stats
    soup2 = BeautifulSoup(map_element, "html.parser")

    # Get the player stats
    score_header = soup2.find("div", class_="vm-stats-game-header")
    team1_round_info = score_header.find("div", class_="team")
    team1_round_score = team1_round_info.find("div").text

    team2_round_info = score_header.find("div", class_="team mod-right")
    team2_round_score = team2_round_info.find_all("div")[-1].text
    
    map_name = score_header.find("div", class_="map").find("span", style="position: relative;")
    map_name = map_name.text.strip().replace("PICK", "").strip()

    # Get the player stats
    team_1_table = soup2.find_all("table", class_="wf-table-inset")[0]
    team_2_table = soup2.find_all("table", class_="wf-table-inset")[1]

    table_data = []
    
    # Create the headers for the table
    table_header = team_1_table.find("tr").find_all("th")
    table_header = ["Map", "Win/Lose By", "Player"] + [th.get("title", "Team") for th in table_header]
    table_data.append(table_header)

    rows = team_1_table.find_all("tr")[1:]

    for row in rows:
        row_data = []
        
        # Get the round score difference and map name
        row_data.append(map_name)
        score_diff = int(team1_round_score) - int(team2_round_score)
        row_data.append(f"+{score_diff}" if score_diff > 0 else str(score_diff))

        # Get the name of players
        player_cell = row.find("td", class_="mod-player")
        name_div = player_cell.find("div", class_="text-of")
        player_name = name_div.get_text(strip=True)
        row_data.append(player_name)

        # Get the team name
        team_1_name = team1_round_info.find('div', class_='team-name').text.strip()
        row_data.append(team_1_name)

        # Get the agents they played
        spans = row.find_all('span', class_='mod-agent')
        agent = [img['title'] for img in [span.find('img') for span in spans]]
        row_data.append(agent[0] if len(agent) != 0 else " ")

        # Get the numerical data
        cols = row.find_all("span", class_=["mod-both"])
        for col in cols:
            row_data.append(col.text.strip())
        table_data.append(row_data)
    
    rows = team_2_table.find_all("tr")[1:]
    # Get the player stats from the second team
    for row in rows:
        row_data = []

        # Get the round score difference and map name
        row_data.append(map_name)
        score_diff = int(team2_round_score) - int(team1_round_score)
        row_data.append(f"+{score_diff}" if score_diff > 0 else str(score_diff))

        # Get the name of players
        player_cell = row.find("td", class_="mod-player")
        name_div = player_cell.find("div", class_="text-of")
        player_name = name_div.get_text(strip=True)
        row_data.append(player_name)

        # Get the team name
        team_2_name = team2_round_info.find('div', class_='team-name').text.strip()
        row_data.append(team_2_name)

        # Get the agents they played
        spans = row.find_all('span', class_='mod-agent')
        agent = [img['title'] for img in [span.find('img') for span in spans]]
        row_data.append(agent[0] if len(agent) != 0 else " ")

        # Get the numerical data
        cols = row.find_all("span", class_=["mod-both"])
        for col in cols:
            row_data.append(col.text.strip())
        table_data.append(row_data)

    return table_data

def get_player_from_map_data(url):
    try:
        driver = create_driver()
        driver.get(url)
        
        # Process the match
        html = driver.page_source
        match_info = process_match(html)

        maps = driver.find_elements(By.XPATH, value="//div[contains(@class, 'vm-stats-gamesnav-item') and @data-disabled='0']")
        
        player_data = []
        total_data = []

        if len(maps) <= 0:
            only_map = driver.find_element(By.XPATH, "//div[contains(@class, 'vm-stats-game mod-active')]").get_attribute("innerHTML")
            player_data = extract_round_data(only_map)

            # Update Columns with new headers
            player_data[0].insert(0, "Match Event")
            player_data[0].insert(1, "Match Stage")
            
            for i in range(1, len(player_data)):
                player_data[i].insert(0, match_info["Match Event"])
                player_data[i].insert(1, match_info["Match Stage"])

            print(f"Processed {url}")
            driver.close()
            return (match_info, player_data)

        else:
            # Click each map button and process the data
            for i in range(1, len(maps)):
                maps[i].click()
                match_stats = driver.find_element(By.XPATH, "//div[contains(@class, 'vm-stats-game') and @style='display: block;']").get_attribute("innerHTML")
                player_data = extract_round_data(match_stats)

                # Update Columns with new headers
                player_data[0].insert(0, "Match Event")
                player_data[0].insert(1, "Match Stage")
                
                for i in range(1, len(player_data)):
                    player_data[i].insert(0, match_info["Match Event"])
                    player_data[i].insert(1, match_info["Match Stage"])

                if not total_data:
                    total_data.append(player_data[0])
                total_data += player_data[1:]

            print(f"Processed {url}")
            driver.close()
            return [match_info, total_data]


    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None
    
# Function to process a single match
def process_match(html):
    try:
        soup = BeautifulSoup(html, "html.parser")

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
        print(f"Error processing: {e}")
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
def save_page_to_csvs(page_num):
    try:
        match_urls = get_match_urls(page_num)

        # Process all matches in the page (Change number of processes as needed)
        with ProcessPoolExecutor(max_workers=4) as executor:
            match_data = list(filter(None, executor.map(get_player_from_map_data, match_urls)))

        # Save the match data to a CSV file
        match_csv_file = os.path.join(match_results_folder, f"matches_page_{page_num}.csv")
        player_csv_file = os.path.join(player_results_folder, f"players_page_{page_num}.csv")
        
        
        for i in range(len(match_data)):
            match_df = pd.DataFrame([match_data[i][0]])
            player_df = pd.DataFrame(match_data[i][1][1:], columns=match_data[i][1][0])

            if not os.path.isfile(match_csv_file):
                match_df.to_csv(match_csv_file, index=False)
            else:
                match_df.to_csv(match_csv_file, mode='a', header=False, index=False)

            if not os.path.isfile(player_csv_file):
                player_df.to_csv(player_csv_file, index=False)
            else:
                player_df.to_csv(player_csv_file, mode='a', header=False, index=False)
    
        print(f"Page {page_num} data saved to {match_csv_file} and {player_csv_file}")

    except Exception as e:
        print(f"Error saving page {page_num}: {e}")

if __name__ == "__main__":
    # Start timer
    start_time = time.time()

    # Number of pages to fetch (Change As Needed)
    results_final_page_num = 10

    # Process each page and save to CSV
    for page_num in range(2, results_final_page_num + 1):
        save_page_to_csvs(page_num)

    # End timer
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"All pages saved. Elapsed time: {elapsed_time:.2f} seconds")
