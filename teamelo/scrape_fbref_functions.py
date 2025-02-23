import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime
import os
import numpy as np

# Crear carpetas para logs y datos si no existen
os.makedirs('scraping_logs', exist_ok=True)

# Inicializar archivo de log con timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f'scraping_logs/output_log_{timestamp}.txt'


def log_message(message: str):
    """Registra y muestra un mensaje con timestamp en el archivo de log."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"{current_time} - {message}"
    print(full_message)
    with open(log_file, 'a') as f:
        f.write(full_message + '\n')


def format_date_string(date_str: str) -> str:
    """Convierte una fecha a formato 'YYYY-MM-DD' si es posible, de lo contrario devuelve la fecha original."""
    try:
        date_obj = pd.to_datetime(date_str, errors='coerce')
        return date_obj.strftime('%Y-%m-%d') if not pd.isna(date_obj) else date_str
    except Exception:
        return date_str

def available_seasons(competition: str, comp_code: int):
 
    url = f"https://fbref.com/en/comps/{comp_code}/history/{competition}-Seasons"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        log_message(f"⚠️ Error al obtener datos: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "stats_table"})

    if not table:
        log_message(f"⚠️ No se encontró la tabla de temporadas para {competition}.")
        return pd.DataFrame()

    headers = [th.text.strip() for th in table.find("thead").find_all("th")]
    rows = [[td.text.strip() for td in row.find_all(["th", "td"])] for row in table.find("tbody").find_all("tr")]

    df = pd.DataFrame(rows, columns=headers)

    seasons = list(df["Season"].sort_values(ascending=True).reset_index(drop=True))

    return seasons


def scrape_season(season: str, competition: str, comp_code: int) -> pd.DataFrame:
    """Scrapea los datos de una temporada, formatea las fechas y guarda el resultado en CSV."""
    log_message(f"🔎 Iniciando scraping para {competition} temporada {season}...")

    all_seasons = available_seasons(competition, comp_code)

    if f"{season}" not in all_seasons:
        log_message(f"{competition} temporada {season} no disponible, omitiendo temporada {season}")
        return None

    url = f"https://fbref.com/en/comps/{comp_code}/{season}/schedule/{season}-{competition}-Scores-and-Fixtures"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        log_message(f"⚠️ Error al obtener datos: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "stats_table"})

    if not table:
        log_message(f"⚠️ No se encontró la tabla de 'Scores & Fixtures' para la temporada {season}.")
        return pd.DataFrame()

    headers = [th.text.strip() for th in table.find("thead").find_all("th")]
    rows = [[td.text.strip() for td in row.find_all(["th", "td"])] for row in table.find("tbody").find_all("tr")]

    df = pd.DataFrame(rows, columns=headers)

    # Manejar empates
    df['Score'] = df['Score'].str.replace(r'\(.*?\)\s*', '', regex=True)


    # Reordenar columnas para que 'Round' (si existe) esté antes de 'Wk'
    if 'Round' in df.columns and 'Wk' in df.columns:
        columns = list(df.columns)
        columns.insert(columns.index('Wk'), columns.pop(columns.index('Round')))  # Mover 'Round' antes de 'Wk'
        df = df[columns]


    if competition in ["Champions-League", "Europa-League", "Conference-League"]:
        df[['Home', 'Home_Country']] = df['Home'].str.rsplit(n=1, expand=True)
        df[['Away_Country', 'Away']] = df['Away'].str.split(n=1, expand=True)

    df = df.replace(r'^\s*$', pd.NA, regex=True)

    # Definir columnas a verificar
    columns_to_check = ['Date', 'Home', 'Away']
    if 'Wk' in df.columns:
        columns_to_check.insert(0, 'Wk')  # Incluir 'Wk' si existe
    if 'Round' in df.columns:
        columns_to_check.insert(0, 'Round')  # Incluir 'Wk' si existe

    # Eliminar filas donde todas las columnas clave estén vacías
    df = df.dropna(subset=columns_to_check, how='all')
    
    # Eliminar filas donde alguna columna clave tenga un valor igual al nombre de la columna
    df = df[~df[columns_to_check].apply(lambda row: any(pd.notna(row[col]) and row[col] == col for col in columns_to_check), axis=1)]

    # Definir las columnas requeridas mínimas
    required_columns = {'Date', 'Home', 'Away', 'Score'}

    # Verificar si faltan columnas requeridas
    if not required_columns.issubset(df.columns):
        missing_cols = required_columns - set(df.columns)
        log_message(f"⚠️ Columnas requeridas faltantes para {season}: {', '.join(missing_cols)}.")
        return pd.DataFrame()


    if competition in ["Champions-League", "Europa-League", "Conference-League"]:
        base_columns = ['Date', 'Home', 'Away', 'Home_Country', 'Away_Country', 'Score']
    else:
        base_columns = ['Date', 'Home', 'Score', 'Away']

    # Insertar 'Wk' si existe en el DataFrame y no está en base_columns
    if 'Wk' in df.columns and 'Wk' not in base_columns:
        base_columns.insert(0, 'Wk')

    # Insertar 'Round' si existe
    if 'Round' in df.columns and 'Round' not in base_columns:
        base_columns.insert(base_columns.index('Wk') if 'Wk' in base_columns else 0, 'Round')

    # Filtrar solo columnas existentes
    base_columns = [col for col in base_columns if col in df.columns]
    df = df[base_columns]


    # Formatear la columna 'Date' al formato 'YYYY-MM-DD'
    df['Date'] = df['Date'].apply(format_date_string)

    # Procesar columna 'Score'
    if 'Score' in df.columns:
        # Limpiar caracteres no deseados y normalizar guiones (–, —, −) a un guion estándar (-)
        df['Score'] = df['Score'].str.replace(r'\(.*?\)', '', regex=True).str.strip()  # Eliminar texto entre paréntesis
        df['Score'] = df['Score'].str.replace(r'[–—−]', '-', regex=True).str.strip()   # Reemplazar cualquier tipo de guion

        # Realizar la división en 'Home_Goals' y 'Away_Goals' de forma segura
        split_scores = df['Score'].str.split('-', expand=True)

        # Asegurarse de que la división siempre tenga dos columnas, rellenando con NaN si no
        if split_scores.shape[1] < 2:
            split_scores = split_scores.reindex(columns=range(2), fill_value=pd.NA)

        # Asignar los valores a las nuevas columnas
        df[['Home_Goals', 'Away_Goals']] = split_scores

        # Convertir las columnas a valores numéricos, manejando errores
        df['Home_Goals'] = pd.to_numeric(df['Home_Goals'], errors='coerce')
        df['Away_Goals'] = pd.to_numeric(df['Away_Goals'], errors='coerce')

        # Identificar y registrar cualquier fila con resultados no válidos
        invalid_rows = df[df['Home_Goals'].isna() | df['Away_Goals'].isna()]
        if not invalid_rows.empty:
            log_message(f"⚠️ Se encontraron {len(invalid_rows)} filas con valores de 'Score' inválidos: {invalid_rows['Score'].unique()}")

        # Calcular el resultado basado en los goles
        df['Result'] = df.apply(
        lambda row: 1 if pd.notna(row['Home_Goals']) and pd.notna(row['Away_Goals']) and row['Home_Goals'] > row['Away_Goals']
        else 0 if pd.notna(row['Home_Goals']) and pd.notna(row['Away_Goals']) and row['Home_Goals'] < row['Away_Goals']
        else 0.5 if pd.notna(row['Home_Goals']) and pd.notna(row['Away_Goals']) and row['Home_Goals'] == row['Away_Goals']
        else np.nan,
        axis=1
    )

        # Eliminar la columna original 'Score' después de procesar
        df.drop(columns=['Score'], inplace=True)

    else:
        log_message(f"⚠️ Columna 'Score' faltante para {season}.")
        return pd.DataFrame()


    df["Season"] = f"{season}"
    df = df[["Season"] + [col for col in df.columns if col != "Season"]]

    output_filename = f"scraped_data/{competition}/{competition}_{season}.csv"
    os.makedirs('scraped_data', exist_ok=True)
    os.makedirs(f'scraped_data/{competition}', exist_ok=True)
    df.to_csv(output_filename, index=False)
    log_message(f"✅ Datos de la temporada {season} guardados en '{output_filename}'.")

    return df


def scrape_multiple_seasons(season_start: str, season_end: str, competition: str, comp_code: int):
    """Scrapea múltiples temporadas consecutivas."""
    log_message(f"🚀 Iniciando scraping de {competition} desde temporada {season_start} hasta temporada {season_end}...")
    all_seasons = available_seasons(competition, comp_code)
    seasons_to_scrape = all_seasons[all_seasons.index(season_start):all_seasons.index(season_end)]
    for season in seasons_to_scrape:
        scrape_season(season, competition, comp_code)
        time.sleep(random.uniform(5, 10))
    log_message("🏁 Scraping de temporadas completado.")

def scrape_all_seasons(competition: str, comp_code: int):
    """Scrapea todas las temporadas disponibles."""
    all_seasons = available_seasons(competition, comp_code)
    log_message(f"🚀 Iniciando scraping de {competition} para todas las temporadas disponibles, desde {all_seasons[0]} hasta {all_seasons[-1]}...")
    for season in all_seasons:
        scrape_season(season, competition, comp_code)
        time.sleep(random.uniform(20, 30))
    log_message("🏁 Scraping de todas las temporadas disponibles completado.")

def update_latest_season(competition: str, comp_code: int):
    """Actualiza la última temporada disponible."""
    all_seasons = available_seasons(competition, comp_code)
    last_season = all_seasons[-1]
    log_message(f"🔄 Actualizando temporada más reciente para {competition}: {last_season}")
    scrape_season(last_season, competition, comp_code)
    log_message(f"✅ Temporada más reciente {last_season} actualizada")


if __name__ == "__main__":
    # Ejemplos de uso
    # competition = "Ligue-1"
    # competition = "Champions-League"
    competition = "Allsvenskan"
    # comp_code = 13
    # comp_code = 8
    comp_code = 29
    # Scraping de todas las temporadas
    # scrape_all_seasons(competition, comp_code)

    # Scraping de una temporada
    # scrape_season("1995-1996", competition, comp_code)

    # Scraping de varias temporadas
    scrape_multiple_seasons("2020", "2024", competition, comp_code)

    # Actualizar última temporada
    # update_latest_season(competition, comp_code)