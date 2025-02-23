from scrape_fbref_functions import available_seasons, scrape_all_seasons, update_latest_season
import json

# Open and read the JSON file
with open('european_comps_fbref.json', 'r') as file:
    european_comps_fbref = json.load(file)

for comp in european_comps_fbref[15:]:
    name = comp["name"]
    code = comp["code"]
    scrape_all_seasons(name, code)