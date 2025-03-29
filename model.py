import pandas as pd
from get_stats import get_player_game_logs

# 🔍 Estimate likely defender
def estimate_defender(player_position, depth_chart, injury_list):
    if player_position not in depth_chart:
        return None
    candidates = depth_chart[player_position]
    for defender in candidates:
        if defender not in injury_list:
            return defender
    return candidates[0] if candidates else None

# 🔢 Final projection calculator
def compute_adjusted_projection(df, stat_type, city, opponent, home, days_rest, defender, drip_rating):
    season_avg = df[stat_type].mean()

    city_avg = df[df['CITY'] == city][stat_type].mean()
    opp_avg = df[df['OPPONENT'] == opponent][stat_type].mean()

    if pd.isna(city_avg):
        city_avg = season_avg
    if pd.isna(opp_avg):
        opp_avg = season_avg

    # Modifiers
    city_adj = (city_avg - season_avg) * 0.2
    opp_adj = (opp_avg - season_avg) * 0.4
    rest_adj = (
        0.05 * season_avg if days_rest >= 3 else
        -0.1 * season_avg if days_rest == 0 else
        0
    )
    home_adj = 0.05 * season_avg if home else -0.05 * season_avg
    def_adj = drip_rating * season_avg

    projection = season_avg + city_adj + opp_adj + rest_adj + home_adj + def_adj

    return projection, season_avg, city_adj, opp_adj, rest_adj, home_adj, def_adj

# 🧠 GPT-compatible depth chart input helper
def parse_list_input(prompt):
    items = input(prompt).strip()
    if not items:
        return []
    return [item.strip() for item in items.split(",")]

# 🔮 Run the model
if __name__ == "__main__":
    player_name = input("Enter NBA player name (e.g., LeBron James): ")
    player_position = input("What position does the player play? (e.g., SF): ").upper()
    stat_type = input("What stat to predict? (PTS, REB, AST): ").upper()
    prop_line = float(input(f"Enter prop line for {stat_type}: "))
    opponent = input("Who are they playing tonight? (3-letter team code, e.g., MEM): ").upper()
    city = input("What city is the game in? (use team code, e.g., MEM): ").upper()
    home = input("Is it a home game? (yes/no): ").strip().lower() == "yes"
    days_rest = int(input("How many days of rest do they have?: "))

    # 🧠 Depth chart & DRIP data
    print("\nEnter opponent depth chart for player's position:")
    depth_chart = {
        player_position: parse_list_input(f"List defenders for {player_position} (comma-separated): ")
    }

    injury_list = parse_list_input("List players OUT tonight (comma-separated): ")

    print("\nEnter DRIP values for each potential defender:")
    drip_rating_map = {}
    for defender in depth_chart[player_position]:
        try:
            drip = float(input(f"{defender}'s DRIP: "))
            drip_rating_map[defender] = drip
        except:
            drip_rating_map[defender] = 0.0

    try:
        df = get_player_game_logs(player_name)
        if stat_type not in df.columns:
            raise ValueError(f"{stat_type} not found in dataset.")

        # Choose defender and get DRIP
        defender = estimate_defender(player_position, depth_chart, injury_list)
        drip_rating = drip_rating_map.get(defender, 0)

        # Projection
        (proj, season_avg, city_adj, opp_adj, rest_adj, home_adj, def_adj) = compute_adjusted_projection(
            df, stat_type, city, opponent, home, days_rest, defender, drip_rating
        )

        # Output
        print(f"\n📊 Base {stat_type} Avg: {season_avg:.2f}")
        print(f"📍 City adj ({city}): {city_adj:+.2f}")
        print(f"🛡️ Opponent adj ({opponent}): {opp_adj:+.2f}")
        print(f"🛌 Rest adj ({days_rest} days): {rest_adj:+.2f}")
        print(f"🏠 Home/Away adj: {home_adj:+.2f}")
        print(f"🧍 Defender adj ({defender} | DRIP {drip_rating:+.2f}): {def_adj:+.2f}")
        print(f"🎯 Final Projected {stat_type}: {proj:.2f}")
        print(f"📈 Prop Line: {prop_line:.2f}")

        if proj > prop_line + 1:
            print("🔮 Recommendation: OVER ✅")
        elif proj < prop_line - 1:
            print("🔮 Recommendation: UNDER ✅")
        else:
            print("🔮 Recommendation: AVOID ⚠️ (Too close to call)")

    except ValueError as e:
        print(f"❌ {e}")
