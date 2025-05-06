from flask import Flask, jsonify
from src.user_cases import get_free_intervals, get_free_windows

app = Flask(__name__)


@app.route("/")
def home():
    return "Привет, Миша! Flask работает!"


@app.route("/win")
def windows():
    return jsonify(get_free_windows())


@app.route("/int")
def intervals():
    return jsonify(get_free_intervals(1*60*60, {"weeks": 2, "months": 0}))


if __name__ == "__main__":
    # debug=True включает автоматическую перезагрузку
    app.run(debug=True, port=8080, host='0.0.0.0')
