from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
from datetime import datetime

def get_player_id_from_name(player_name):
    all_players = players.get_active_players()
    for player in all_players:
        if player['full_name'].lower().strip() == player_name.lower().strip():
            return player['id']
    return None

def extract_team_and_city(matchup):
    parts = matchup.split(" ")
    home = parts[1] != "@"
    opponent = parts[-1]
    city = opponent  # Using team abbreviation as city
    return opponent, city, home

def calculate_days_rest(dates):
    rest_days = [0]
    for i in range(1, len(dates)):
        delta = (dates[i - 1] - dates[i]).days
        rest_days.append(delta)
    return rest_days

def get_player_game_logs(player_name='LeBron James', season='2023-24'):
    player_id = get_player_id_from_name(player_name)
    if player_id is None:
        raise ValueError(f"Player '{player_name}' not found.")
    
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    df = gamelog.get_data_frames()[0]

    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%Y-%m-%d', errors='coerce')
    df = df.sort_values('GAME_DATE', ascending=False)

    df['OPPONENT'], df['CITY'], df['HOME'] = zip(*df['MATCHUP'].apply(extract_team_and_city))
    df['DAYS_REST'] = calculate_days_rest(df['GAME_DATE'].tolist())

    for stat in ['PTS', 'REB', 'AST']:
        df[f'AVG_{stat}_VS_OPPONENT'] = df.groupby('OPPONENT')[stat].transform('mean')
        df[f'AVG_{stat}_IN_CITY'] = df.groupby('CITY')[stat].transform('mean')

    return df

if __name__ == "__main__":
    player_name = input("Enter player name (e.g., LeBron James): ")
    df = get_player_game_logs(player_name)
    print(df[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST', 'MIN', 'DAYS_REST', 'HOME', 'OPPONENT', 'CITY']].head())
