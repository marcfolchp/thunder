from scrapev2 import scrape_multiple_seasons

start_year = 1988
end_year = 2024

competition = "La-Liga"
comp_code = 12
scrape_multiple_seasons(start_year, end_year, competition, comp_code)

competition = "Premier-League"
comp_code = 9
scrape_multiple_seasons(start_year, end_year, competition, comp_code)

competition = "Ligue-1"
comp_code = 13
scrape_multiple_seasons(start_year, end_year, competition, comp_code)

competition = "Bundesliga"
comp_code = 20
scrape_multiple_seasons(start_year, end_year, competition, comp_code)

competition = "Serie-A"
comp_code = 11
scrape_multiple_seasons(start_year, end_year, competition, comp_code)

competition = "Champions-League"
comp_code = 8
scrape_multiple_seasons(start_year, end_year, competition, comp_code)

competition = "Europa-League"
comp_code = 19
scrape_multiple_seasons(start_year, end_year, competition, comp_code)

competition = "Conference-League"
comp_code = 882
scrape_multiple_seasons(start_year, end_year, competition, comp_code)