import requests
from bs4 import BeautifulSoup
import pandas as pd , numpy as np
import warnings
import time

warnings.filterwarnings('ignore')

# x_league = 1
# y_team = 1
# temporada = 2017
n_leagues = 5

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

all_players = pd.DataFrame()

# LEAGUE LINKS

url = 'https://www.transfermarkt.es/wettbewerbe/europa'

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')

a = soup.find_all("table", {"class": "inline-table"})

league_links = []

for i in range(min(len(a), n_leagues)):
    league_links.append(a[i].find_all('a', href=True)[0].get('href'))

# LEAGUE LOOOP

for x_league in league_links:

    # SEASON LOOOP

    for temporada in range(2017, 2025):

        # IN A LEAGUE LINK, GET ALL TEAM LINKS

        time.sleep(1)

        url = f'https://www.transfermarkt.es/{x_league}/plus/?saison_id={temporada}'

        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        b = soup.find_all('td', {'class':'hauptlink no-border-links'})

        team_links = []

        for j in range(len(b)):
            team_links.append(b[j].find_all('a', href=True)[0].get('href'))

        
        # TEAM LOOOP

        for y_team in team_links:

            # IN A TEAM LINK, GET TEAM TABLE

            time.sleep(5)

            url = f'https://www.transfermarkt.es/{y_team}'

            response = requests.get(url, headers=headers)

            soup = BeautifulSoup(response.text, 'html.parser')

            pageTree = requests.get(url, headers=headers)

            tables = pd.read_html(pageTree.content)

            first_table = tables[1]

            if 'Edad' in first_table.columns:
                first_table = first_table[::3][['Jugadores', 'Edad', 'Valor de mercado']]

            elif 'F. Nacim./Edad' in first_table.columns:
                first_table = first_table[::3][['Jugadores', 'F. Nacim./Edad', 'Valor de mercado']]

            first_table['Temporada'] = f'{temporada}/{temporada+1}'

            def convert_market_value(value):
                value = value.replace('€', '').strip()
                value = value.replace(',', '.')

                if value == '-':
                    return 0
                elif 'mill.' in value:
                    return float(value.replace('mill.', '').strip()) * 1_000_000
                elif 'mil' in value:
                    return float(value.replace('mil', '').strip()) * 1_000
                return float(value)

            first_table['Valor de mercado (num)'] = first_table['Valor de mercado'].apply(convert_market_value)
            first_table['League'] = x_league.split('/')[1]
            first_table['Team'] = y_team.split('/')[1]

            # APPEND PLAYER LIST FOR THAT LEAGUE, TEAM, AND SEASON TO THE TABLE OUTSIDE THE LOOP

            all_players = pd.concat([all_players, first_table])

            print(x_league.split('/')[1], temporada, y_team.split('/')[1])

            all_players.to_csv('all_players_transfers.csv')