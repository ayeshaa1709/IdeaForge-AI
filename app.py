from flask import Flask, render_template, request, jsonify
from validator import validate_startup_idea

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/validate", methods=["POST"])
def validate():

    data = request.get_json()

    idea = data["idea"]

    result = validate_startup_idea(idea)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)