from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route("/")
def home():

    with open("json_txt.json", "r", encoding="utf-8") as file:
        notes = json.load(file)

    return render_template("index.html", notes=notes)

if __name__ == "__main__":
    app.run(debug=True)