from flask import Flask, request, jsonify, render_template, send_from_directory
import asyncio, json, time, os
from threading import Thread
from faceit import get_full_stats
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

stats_file = "stats.json"
current_username = "_ExamPlay_"

@app.route("/")
def index():
    return render_template("faceit.html")  # Ищет в /templates

@app.route("/stats.json", methods=["GET", "POST"])
def stats():
    global current_username
    if request.method == "POST":
        username = request.json.get("username", "_ExamPlay_")
        current_username = username

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stats_data = loop.run_until_complete(get_full_stats(username))
        loop.close()

        if stats_data:
            with open(stats_file, "w") as f:
                json.dump({"username": username, **stats_data}, f, indent=2)
            return jsonify(stats_data)
        else:
            return jsonify({"ok": False, "error": "Статистика не найдена"}), 400
    else:
        try:
            with open(stats_file, "r") as f:
                return f.read()
        except:
            return jsonify({"username": "_ExamPlay_", "elo": "-", "kd": "-", "winrate": "-"})

def update_stats_loop():
    while True:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stats_data = loop.run_until_complete(get_full_stats(current_username))
        loop.close()
        if stats_data:
            with open(stats_file, "w") as f:
                json.dump({"username": current_username, **stats_data}, f, indent=2)
        time.sleep(10)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    Thread(target=update_stats_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=port)
