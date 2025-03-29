from flask import Flask, request, jsonify
from model import compute_adjusted_projection
from get_stats import get_player_game_logs

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        df = get_player_game_logs(data['player_name'])

        projection, season_avg, city_adj, opp_adj, rest_adj, home_adj, def_adj = compute_adjusted_projection(
            df,
            data['stat_type'],
            data['city'],
            data['opponent'],
            data['home'],
            data['days_rest'],
            data['defender'],
            data['drip_rating']
        )

        result = {
            "player": data["player_name"],
            "stat": data["stat_type"],
            "prop_line": data["prop_line"],
            "projection": round(projection, 2),
            "season_avg": round(season_avg, 2),
            "adjustments": {
                "city": round(city_adj, 2),
                "opponent": round(opp_adj, 2),
                "rest": round(rest_adj, 2),
                "home": round(home_adj, 2),
                "defender": round(def_adj, 2)
            },
            "recommendation": (
                "OVER ✅" if projection > data["prop_line"] + 1 else
                "UNDER ✅" if projection < data["prop_line"] - 1 else
                "AVOID ⚠️"
            )
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
