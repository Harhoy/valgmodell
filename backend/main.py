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

@app.route("/valgdistrikt")
def valgdistrikt():
    return render_template("valgdistrikt.html")

@app.route("/kandidater")
def kandidater():
    return render_template("kandidater.html")

@app.route("/")
def index():
    return render_template("index.html")

#----------------------------------------------
#Getting district names and numbers
#----------------------------------------------
@app.route("/getParties")
def get_parties():
    QUERY = text("SELECT ID, Name, Shortname, R, G, B FROM Parties ORDER BY ID")
    RETURN_VAL = {}
    result = db.engine.execute(QUERY)
    for row in result:
        RETURN_VAL[row[0]] = {'Name': row[2], 'R': row[3], 'G': row[4], 'B': row[5]}
    return json.dumps(RETURN_VAL)

#----------------------------------------------
#Getting party names and numbers
#----------------------------------------------
@app.route("/getDistricts")
def get_districts():
    QUERY = text("SELECT ID, Name FROM Districts ORDER BY ID")
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
            RETURN_VAL[parti] = {'distrikt': distrikt, 'utjevning': utjevning, 'total': total}

        return json.dumps(RETURN_VAL)

@app.route("/resultater_part_mandater_time_series", methods = ['POST'])
def resultater_part_mandater_time_series():

    if request.method == "POST":

        DISTRICT = request.json.get("district")
        #DISTRICT = request.args.get("district", default = 1, type = int)

        SIM_QUERY = text("SELECT ID, Dato from Simulering ORDER BY ID")
        result_simuleringer = db.engine.execute(SIM_QUERY)
        RETURN_VAL = []

        for rowA in result_simuleringer:

            CURRENT_SIM = rowA[0]
            QUERY = text("SELECT Mandater_distrikt, Mandater_utjevning, Mandater_total, Parti FROM Resultater_parti WHERE SimuleringsID == " +  "'" + str(CURRENT_SIM) +  "'" + " AND " + " Fylke == " +  "'" + str(DISTRICT) +  "'"  + " ORDER BY Parti")

            result = db.engine.execute(QUERY)
            RETURN_VAL_LOCAL = {'SimuleringsID': CURRENT_SIM, 'Data': {} , 'Dato': rowA[1]}
            for rowB in result:
                distrikt = rowB[0]
                utjevning = rowB[1]
                total = rowB[2]
                parti = rowB[3]
                RETURN_VAL_LOCAL['Data'][parti] = {'distrikt': distrikt, 'utjevning': utjevning, 'total': total}

            RETURN_VAL.append(RETURN_VAL_LOCAL)

    return json.dumps(RETURN_VAL)

#----------------------------------------------
#Getting counts for each county for newest but distribution data
#----------------------------------------------
@app.route("/resultater_part_mandater_hist", methods = ['POST'])
def resultater_part_mandater_hist():

    if request.method == "POST":

        CURRENT_SIM = db.engine.execute("select max(id) from Simulering").fetchone()[0]
        DISTRICT = request.args.get("district", default = 1, type = int)
        #DISTRICT = request.json.get("district")
        RETURN_VAL = {}

        QUERY = text("SELECT Resultat_distrikt, Resultat_utjevning, Resultat_total, Parti FROM Resultater_parti WHERE SimuleringsID == " +  "'" + str(CURRENT_SIM) +  "'" + " AND " + " Fylke == " +  "'" + str(DISTRICT) +  "'"  + " ORDER BY Parti")

        result = db.engine.execute(QUERY)
        for row in result:
            distrikt = row[0].split(";")
            utjevning = row[1].split(";")
            total = row[2].split(";")
            parti = row[3]
            RETURN_VAL[parti] = {'distrikt': distrikt, 'utjevning': utjevning, 'total': total}

        return json.dumps(RETURN_VAL)



#----------------------------------------------
#Getting probabilities for each candidate
#----------------------------------------------
@app.route("/resultater_part_mandater_prob", methods = ['POST'])
def resultater_part_mandater_prob():

    if request.method == "POST":

        CURRENT_SIM = db.engine.execute("select max(id) from Simulering").fetchone()[0]
        #DISTRICT = request.args.get("district", default = 1, type = int)
        DISTRICT = request.json.get("district")
        RETURN_VAL = {}

        #Getting the name to find the relevant candidates
        CURRENT_DISTRICT_NAME = db.engine.execute("select Name from Districts WHERE ID == " +  "'" + str(DISTRICT) +"'" ).fetchone()[0]

        #Getting the party name to find the relevant candidates
        CURRENT_PARTY_NAMES = db.engine.execute("select Name, Shortname, ID from Parties" )

        partyKey = {}
        candiates = {}
        for data in CURRENT_PARTY_NAMES:
            partyKey[data[2]] = data[1]


            QUERY_CAND = text("SELECT navn, alder, valgdistrikt, partinavn, kandidatnr from Kandidater_21 WHERE partikode  == " +  "'" + partyKey[data[2]] +  "'" + " AND " + " valgdistrikt == " +  "'" + CURRENT_DISTRICT_NAME +  "'"  + "")

            candidate_results = db.engine.execute(QUERY_CAND)
            candiates[partyKey[data[2]]] = {}

            for cand in candidate_results:
                candiates[partyKey[data[2]]][cand[4]] = {'Navn': cand[0], 'Alder': cand[1]}


        # ---- Getting probabilities ----
        QUERY_PROB = text("SELECT KandidatID, Prob_total, Parti FROM Resultater_kandidat WHERE SimuleringsID == " +  "'" + str(CURRENT_SIM) +  "'" + " AND " + " Fylke == " +  "'" + str(DISTRICT) +  "'"  + " ORDER BY Parti, Prob_total")

        result = db.engine.execute(QUERY_PROB)
        for row in result:

            kandidatnavn = candiates[partyKey[row[2]]][row[0]]['Navn']
            if not partyKey[row[2]] in RETURN_VAL.keys():
                RETURN_VAL[partyKey[row[2]]] = [{'Navn':kandidatnavn, 'P': round(row[1],0)}]
            else:
                RETURN_VAL[partyKey[row[2]]].append({'Navn':kandidatnavn, 'P': round(row[1],0)})

        return json.dumps(RETURN_VAL)



@app.route("/getCandidateId", methods = ['POST'])
def get_candidate_id():

    #name to find in candiate list
    name = request.json.get("Name")

    #getting candidate number
    QUERY_ID = text("SELECT valgdistrikt, kandidatnr, partikode FROM Kandidater_21 WHERE navn == " +  "'" + unicode(name) +  "'")
    result = db.engine.execute(QUERY_ID).fetchone()

    #informaton on the candidate
    response = {'name':name, 'fylke': result[0], 'candidateID': result[1], 'party': result[2]}

    # ---- Getting county number ----
    response['candidateFylkeID'] = db.engine.execute("select ID from Districts WHERE Name == " +  "'" + unicode(response['fylke']) +"'" ).fetchone()[0]

    # ---- Getting party number ----
    response['candidatePartyID'] = db.engine.execute("select ID from Parties WHERE Shortname == " +  "'" + unicode(response['party']) +"'" ).fetchone()[0]

    # ---- Getting probabilities ----
    QUERY_PROB = text("SELECT Prob_total FROM Resultater_kandidat WHERE KandidatID == " +  "'" + str(response['candidateID']) +  "'" + " AND " + " Fylke == " +  "'" + str(response['candidateFylkeID']) +  "'"  + " AND " + " Parti == " +  "'" + str(response['candidatePartyID']) +  "'"  + " ORDER BY SimuleringsID")

    probabilities = []
    result = db.engine.execute(QUERY_PROB)
    for row in result:
        probabilities.append(row[0])

    response['probabilities'] = probabilities

    return json.dumps(response)

#----------------------------------------------
#Getting count for total for newest
#----------------------------------------------
@app.route("/resultater_part_mandater_total")
def resultater_part_mandater_total():
    pass


if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='192.168.1.88', port=5000, debug=True, threaded=False)
