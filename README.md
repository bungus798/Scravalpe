# Scravalpe: Valorant Data Scraper

**Author:** Angus Yeung  
**Date:** 2025-02-15  

Scravalpe is a personal project that scrapes Valorant match results and player statistics from [vlr.gg](https://www.vlr.gg). It extracts match event information, scores, and detailed player stats, then consolidates the data into CSV files for further analysis.

---

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Project Structure](#project-structure)  
4. [Prerequisites & Installation](#prerequisites--installation)  
5. [Usage](#usage)  
   - [Running the Scraper](#running-the-scraper)  
   - [Combining the CSV Outputs](#combining-the-csv-outputs)  
6. [Notes & Limitations](#notes--limitations)  
7. [License](#license)

---

## Project Overview

This repository contains two primary components:

1. **Scraper Script (Main Scraper)**  
   - Uses `requests` and `BeautifulSoup` to retrieve the match listings from vlr.gg.  
   - Uses `Selenium` to navigate and parse individual match pages.  
   - Saves two types of CSV files in separate folders:  
     - **Match results** in `match_results`  
     - **Player statistics** in `player_results`

2. **CSV Combiner Script**  
   - Reads and concatenates the CSV files you’ve scraped.  
   - Sorts them (optionally) by a `"Match Date"` column.  
   - Outputs final combined CSV files into `combined_match_results` and `combined_player_results`.

---

## Features

- **Concurrent Scraping**: Utilizes `ProcessPoolExecutor` to parallelize requests and speed up data collection.  
- **Random User Agent**: Rotates `User-Agent` strings to help reduce likelihood of being blocked.  
- **Structured Data Storage**: Outputs neatly structured CSV files for both match-level and player-level data.  
- **Automated Merging**: A separate script combines all CSVs into final consolidated files for easy analysis.  

---

## Project Structure

```
scravalpe/
├── main.py                         # Main scraping script
├── combiner.py                     # Script to combine CSV files
├── match_results/                  # CSV files for match data (output from main.py)
├── player_results/                 # CSV files for player data (output from main.py)
├── combined_match_results/         # Combined match results CSV (output from combiner.py)
├── combined_player_results/        # Combined player results CSV (output from combiner.py)
├── README.md                       # This file
└── requirements.txt (optional)     # Python dependencies (if you decide to add one)
```

---

## Prerequisites & Installation

1. **Python 3.8+** (recommended)  
2. **Google Chrome** (or Chromium) installed.  
3. **ChromeDriver** matching your Chrome version.  
   - Download from [ChromeDriver official site](https://chromedriver.chromium.org/downloads).  
   - Update the `path_chromedriver` variable in `main.py` to point to your local ChromeDriver.
4. **Python Libraries** (install individually or via a `requirements.txt`):  
   - [requests](https://pypi.org/project/requests/)  
   - [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)  
   - [pandas](https://pypi.org/project/pandas/)  
   - [selenium](https://pypi.org/project/selenium/)

Install them via pip, for example:
```bash
pip install -r requirements.txt
```

---

## Usage

### Running the Scraper

1. In **`main.py`**, update the ChromeDriver path:
   ```python
   path_chromedriver = "/path/to/your/chromedriver"
   ```
2. Adjust the number of pages to scrape (if desired):
   ```python
   results_final_page_num = 10
   ```
   This will scrape pages 2 through 10 on [vlr.gg](https://vlr.gg/matches/results).

3. **Run**:
   ```bash
   python main.py
   ```
   - This creates `match_results/` and `player_results/` if they do not already exist.
   - For each scraped page, two files are produced:
     - `matches_page_<pagenum>.csv` in `match_results/`
     - `players_page_<pagenum>.csv` in `player_results/`

---

### Combining the CSV Outputs

After scraping multiple pages, you can combine all individual CSVs:

1. **Open** the CSV combiner script (e.g., `combiner.py`).  
2. Make sure folder references match:
   ```python
   input_folder_matches = "match_results"
   output_folder_matches = "combined_match_results"
   input_folder_players = "player_results"
   output_folder_players = "combined_player_results"
   ```
3. **Run**:
   ```bash
   python combiner.py
   ```
   - It creates a combined file in `combined_match_results/` and another in `combined_player_results/`.
   - If `"Match Date"` is present, it sorts and names the file based on the oldest and newest dates.  
     Otherwise, it just creates a `*_combined.csv`.

---

## Notes & Limitations

1. **Respect Website Terms**: Make sure to follow [vlr.gg’s Terms of Service](https://www.vlr.gg/) when scraping data.  
2. **Rate Limiting**: Consider adding additional random delays if you scrape many pages in a short time.  
3. **Website Structure**: If vlr.gg changes its layout, the scraper may need updates.  
4. **Selenium & ChromeDriver**: Ensure your local Chrome version matches your downloaded ChromeDriver version.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details (if present).
