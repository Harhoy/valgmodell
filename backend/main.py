from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import date
import json
import sqlite3


#Selve appen
app = Flask(__name__)

#Telling the app where the database is located
app.config['SQLALCHEMY_DATABASE_URI'] = r"sqlite:///" + "/Users/bruker/Documents/Programmering/2024/valgside/valgmodell/modell/data/databaser/mainDB_TEST.db"

#Databse
db = SQLAlchemy(app) #ny database og sender inn appen her

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/getDistricts")
def get_districts():
    QUERY = text("SELECT ID Name FROM Districts")
    RETURN_VAL = {}
    result = db.engine.execute(QUERY)
    for row in result:
        RETURN_VAL[row[0]] = row[1]
    return json.dumps(RETURN_VAL)

#----------------------------------------------
#Getting counts for each county for newest
#----------------------------------------------
@app.route("/resultater_part_mandater", methods = ['POST'])
def resultater_part_mandater():

    if request.method == "POST":

        CURRENT_SIM = db.engine.execute("select max(id) from Simulering").fetchone()[0]
        #DISTRICT = request.args.get("district", default = 1, type = int)
        DISTRICT = request.json.get("district")
        RETURN_VAL = {}

        QUERY = text("SELECT Mandater_distrikt, Mandater_utjevning, Mandater_total, Parti FROM Resultater_parti WHERE SimuleringsID == " +  "'" + str(CURRENT_SIM) +  "'" + " AND " + " Fylke == " +  "'" + str(DISTRICT) +  "'"  + " ORDER BY Parti")

        result = db.engine.execute(QUERY)

        for row in result:

            distrikt = row[0]
            utjevning = row[1]
            total = row[2]
            parti = row[3]

            RETURN_VAL[parti] = {'distrikt': distrikt, 'utjevning':utjevning, 'total': total}

        return json.dumps(RETURN_VAL)

#----------------------------------------------
#Getting count for total for newest
#----------------------------------------------
@app.route("/resultater_part_mandater_total")
def resultater_part_mandater_total():
    pass


if __name__ == "__main__":
    app.run(debug=True)
