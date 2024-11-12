from selenium.webdriver.common.by import By
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import warnings

warnings.filterwarnings('ignore')

season_links = [
    'https://fbref.com/en/comps/12/2023-2024/schedule/2023-2024-La-Liga-Scores-and-Fixtures',
    'https://fbref.com/en/comps/12/2022-2023/schedule/2022-2023-La-Liga-Scores-and-Fixtures',
    'https://fbref.com/en/comps/12/2021-2022/schedule/2021-2022-La-Liga-Scores-and-Fixtures',
    'https://fbref.com/en/comps/12/2020-2021/schedule/2020-2021-La-Liga-Scores-and-Fixtures',
    'https://fbref.com/en/comps/12/2019-2020/schedule/2019-2020-La-Liga-Scores-and-Fixtures',
    'https://fbref.com/en/comps/12/2018-2019/schedule/2018-2019-La-Liga-Scores-and-Fixtures',
    'https://fbref.com/en/comps/12/2017-2018/schedule/2017-2018-La-Liga-Scores-and-Fixtures'
]

def drop_top_column_level(dataframe):
    dataframe.columns = dataframe.columns.droplevel(0)

def merge_players(players, team_id):
    team_df = players[0]
    for i, df in enumerate(players[1:]):
        team_df = pd.merge(
            team_df, df, on='Player', how='outer', 
            suffixes=('', f'_{i+1}')
        )
    team_df = team_df.reset_index(drop=True)
    team_df['team_id'] = team_id
    return team_df
    
season_counter = 1
season_df = pd.DataFrame()

# Start the web driver once for all seasons
driver = webdriver.Chrome()

for season in season_links:
    
    # Get links of all the matches in the season
    driver.get(season)
    match_report_links = driver.find_elements(By.XPATH, "//a[text()='Match Report']")
    links = [link.get_attribute("href") for link in match_report_links]

    # Collect all match data for the season
    match_data_list = []
    
        # Define headers with a custom User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
    }

    for counter, link in enumerate(links, start=1):
        
        try:
            response = requests.get(link, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to retrieve content from {link}, status code: {response.status_code}")
                continue
            
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all tables with the specified class
            tables_html = soup.find_all('table', {'class': 'stats_table'})

            # Convert each found table to a DataFrame using pd.read_html
            tables = [pd.read_html(str(table))[0] for table in tables_html]

            # Drop the top column level for all tables
            for table in tables:
                drop_top_column_level(table)

            # Process home and away player data
            home_players = tables[0:7]
            away_players = tables[7:14]

            home_df = merge_players(home_players, 'H')[1:]
            away_df = merge_players(away_players, 'A')[1:]

            # Combine home and away data, assign match_id, and store it
            match_players = pd.concat([home_df, away_df]).reset_index(drop=True)
            match_players['match_id'] = counter
            match_data_list.append(match_players)

            print(f"Completed match {counter} of season {season_counter}")
            
        except requests.exceptions.RequestException as e:
            print(f"Request error for match {counter}: {e}. Retrying in 1 hour...")
            time.sleep(3600)
            continue
        
        # Optional sleep to avoid hitting request limits
        time.sleep(random.uniform(5, 10))

    # Combine all matches in the season into a single DataFrame
    all_df = pd.concat(match_data_list).reset_index(drop=True)

    # Get season fixtures
    calendar = pd.read_html(season)[0].dropna(how='all')
    calendar['match_id'] = range(1, len(calendar) + 1)
    fixtures = calendar[['match_id', 'Home', 'Away']]
    
    # Melt fixtures to match home/away teams with match_id
    df_melted = fixtures.melt(id_vars=['match_id'], value_vars=['Home', 'Away'], 
                              var_name='team_id', value_name='team_name')
    df_melted['team_id'] = df_melted['team_id'].replace({'Home': 'H', 'Away': 'A'})

    # Merge player data with team names from fixtures
    complete_df = all_df.merge(df_melted[['match_id', 'team_id', 'team_name']], 
                               on=['match_id', 'team_id'], how='left')
    
    complete_df['season_id'] = season_counter

    complete_df.to_csv(f'tables/laliga_season_{2024 - season_counter}_{2025 - season_counter}')

    season_counter += 1
    
    # Append complete_df for the season to the season_df
    season_df = pd.concat([season_df, complete_df], ignore_index=True)

    print(f"Completed season {season_counter - 1}")

# Close the web driver once at the end
driver.quit()

season_df.to_csv('tables/laliga_all_seasons.csv')