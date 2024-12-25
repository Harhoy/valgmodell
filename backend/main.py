from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import date
import json
import sqlite3



#Selve appen
app = Flask(__name__)


conn = sqlite3.connect("/Users/bruker/Documents/Programmering/2024/valgside/valgmodell/modell/data/databaser/mainDB_TEST.db")
cur = conn.cursor()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/resultater_part_mandater")
def resultater_part_mandater():
    pass


if __name__ == "__main__":
    app.run(debug=True)
