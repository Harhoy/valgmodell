from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import date
import json
import sqlite3
from copy import deepcopy
import datetime


'''
def clamp(x):
  return max(0, min(x, 255))

"#{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))
'''

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)




#Selve appen
app = Flask(__name__)

#Telling the app where the database is located
app.config['SQLALCHEMY_DATABASE_URI'] = r"sqlite:///" + "/Users/bruker/Documents/Programmering/2024/valgside/valgmodell/modell/data/databaser/mainDB_TEST.db"

#Databse
db = SQLAlchemy(app) #ny database og sender inn appen her

@app.route("/getSimInfo")
def get_sim_info():
    QUERY = text("SELECT Dato, id FROM Simulering WHERE id > 0")
    resp = []
    for r in db.engine.execute(QUERY):
        resp.append({'id': r[1], 'date':r[0]})
    return json.dumps(resp)

@app.route("/valgdistrikt")
def valgdistrikt():
    return render_template("valgdistrikt.html")

@app.route("/kandidater")
def kandidater():
    return render_template("kandidater.html")

@app.route("/partier")
def partier():
    return render_template("partier.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/valgkart")
def valgkart():
    return render_template("valgkart.html")

@app.route("/metode")
def metode():
    return render_template("metode.html")

@app.route("/datagrunnlag")
def datagrunnlag():
    return render_template("datagrunnlag.html")

@app.route("/utjevningsmandater")
def utjevningsmandater():
    return render_template("utjevningsmandater.html")

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
#Getting party coaltion names and numbers
#----------------------------------------------
@app.route("/getCoalitions")
def get_coalitions():
    parties_data = json.loads(get_parties())
    QUERY = text("SELECT Navn, Partier FROM Koalisjon ORDER BY ID")
    RETURN_VAL = {}
    result = db.engine.execute(QUERY)
    for row in result:
        RETURN_VAL[row[0]] = {'R':0.0, 'G':0.0, 'B':0.0}
        k = 0
        parties = row[1].split("-")
        parties = [int(x) for x in parties]
        for party in parties:
            for col in ['R','G','B']:
                RETURN_VAL[row[0]][col] += parties_data[str(party)][col]
            k += 1
        for col in ['R','G','B']:
            RETURN_VAL[row[0]][col] = int(RETURN_VAL[row[0]][col] / k)

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

        SIM_ID = request.json.get("simID")

        if SIM_ID < -99:
            SIM_ID = CURRENT_SIM

        QUERY = text("SELECT Mandater_distrikt, Mandater_utjevning, Mandater_total, Parti FROM Resultater_parti WHERE SimuleringsID == " +  "'" + str(SIM_ID) +  "'" + " AND " + " Fylke == " +  "'" + str(DISTRICT) +  "'"  + " ORDER BY Parti")

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

        SIM_QUERY = text("SELECT ID, Dato from Simulering WHERE ID > 0 ORDER BY ID")
        result_simuleringer = db.engine.execute(SIM_QUERY)
        RETURN_VAL = []

        for rowA in result_simuleringer:

            CURRENT_SIM = rowA[0]
            QUERY = text("SELECT Mandater_distrikt, Mandater_utjevning, Mandater_total, Parti FROM Resultater_parti WHERE SimuleringsID == " +  "'" + str(CURRENT_SIM) +  "'" + " AND " + " Fylke == " +  "'" + str(DISTRICT) +  "'"  + " ORDER BY Parti")

            result = db.engine.execute(QUERY)
            date = rowA[1]#.split("/")
            #date  = str(datetime.date(int(date[2]), int(date[0]), int(date[1])).isocalendar()[1]) 

        
            RETURN_VAL_LOCAL = {'SimuleringsID': CURRENT_SIM, 'Data': {} , 'Dato': date}
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


            QUERY_CAND = text("SELECT navn, alder, valgdistrikt, partinavn, kandidatnr from Kandidater_25 WHERE partikode  == " +  "'" + partyKey[data[2]] +  "'" + " AND " + " valgdistrikt == " +  "'" + CURRENT_DISTRICT_NAME +  "'"  + "")

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
    QUERY_ID = text("SELECT valgdistrikt, kandidatnr, partikode FROM Kandidater_25 WHERE navn == " +  "'" + unicode(name) +  "'")
    result = db.engine.execute(QUERY_ID).fetchone()

    #informaton on the candidate
    response = {'name':name, 'fylke': result[0], 'candidateID': result[1], 'party': result[2]}

    # ---- Getting county number ----
    response['candidateFylkeID'] = db.engine.execute("select ID from Districts WHERE Name == " +  "'" + unicode(response['fylke']) +"'" ).fetchone()[0]

    # ---- Getting party number ----
    response['candidatePartyID'] = db.engine.execute("select ID from Parties WHERE Shortname == " +  "'" + unicode(response['party']) +"'" ).fetchone()[0]

    response['candidatePartyName'] = db.engine.execute("select Name from Parties WHERE Shortname == " +  "'" + unicode(response['party']) +"'" ).fetchone()[0]

    # ---- Getting probabilities ----
    QUERY_PROB = text("SELECT Prob_total FROM Resultater_kandidat WHERE KandidatID == " +  "'" + str(response['candidateID']) +  "'" + " AND " + " Fylke == " +  "'" + str(response['candidateFylkeID']) +  "'"  + " AND " + " Parti == " +  "'" + str(response['candidatePartyID']) +  "'" +  " AND " + " SimuleringsID > 0 "  + " ORDER BY SimuleringsID")

    probabilities = []
    result = db.engine.execute(QUERY_PROB)
    for row in result:
        probabilities.append(round(row[0]))

    response['probabilities'] = probabilities

    return json.dumps(response)


@app.route("/resultater_parti_national")
def resultater_parti_national():

        CURRENT_SIM = db.engine.execute("select max(id) from Simulering WHERE id > 0").fetchone()[0]
        FIRST_SIM = db.engine.execute("select min(id) from Simulering WHERE id > 0").fetchone()[0]
        sharesData = []

        #Getting the party name to find the relevant candidates
        CURRENT_PARTY_NAMES = db.engine.execute("select Name, Shortname, ID from Parties" )

        partyKey = {}
        for data in CURRENT_PARTY_NAMES:
            partyKey[data[2]] = {'name': data[1], 'shares': 0.0}

        for iter in range(CURRENT_SIM):
            QUERY = text("SELECT Party, Share, Seats FROM Resultater_parti_national WHERE SimuleringsID == " +  "'" + str(iter + 1) +"' ORDER BY SimuleringsID")
            SIM_DATA = db.engine.execute(QUERY)
            temp = deepcopy(partyKey)
            for res in SIM_DATA:
                temp[res[0]]['shares'] = res[1]
                temp[res[0]]['seats'] = res[2]
            sharesData.append(temp)


        return json.dumps(sharesData)


@app.route("/resultater_national_specific", methods = ["POST"])
def resultater_national_specific():

    # Id of sim
    simID = request.json.get("simID")

    #Getting the party name to find the relevant candidates
    CURRENT_PARTY_NAMES = db.engine.execute("select Name, Shortname, ID, R, G, B, LeftRight from Parties" )

    partyKey = {}
    sharesData = []
        
    for data in CURRENT_PARTY_NAMES:
        partyKey[data[2]] = {'name': data[1], 'shares': 0.0, 'hex': rgb2hex(data[3], data[4], data[5]), "LR":  data[6]}
    
    QUERY = text("SELECT Party, Share, Seats FROM Resultater_parti_national WHERE SimuleringsID == " +  "'" + str(simID) +"' ORDER BY SimuleringsID")
    SIM_DATA = db.engine.execute(QUERY)
    for res in SIM_DATA:
        partyKey[res[0]]['shares'] = res[1]
        partyKey[res[0]]['seats'] = res[2]
    sharesData.append(partyKey)

    return json.dumps(sharesData)
    
    

@app.route("/resultater_kaolisjon_national")
def resultater_koalisjon_national():

        CURRENT_SIM = db.engine.execute("select max(id) from Simulering").fetchone()[0]
        FIRST_SIM = db.engine.execute("select min(id) from Simulering").fetchone()[0]
        sharesData = []

        #Getting the party name to find the relevant candidates
        CURRENT_COALTION_NAMES = db.engine.execute("select Navn, Partier, ID from Koalisjon" )

        coalitionKey = {}
        for data in CURRENT_COALTION_NAMES:
            coalitionKey[data[2]] = {'navn': data[0], 'partier': data[1],'share': 0.0,'mandater':0.0, 'prob': None}

        for iter in range(CURRENT_SIM):
            QUERY = text("SELECT Koalisjon, Mandater, Share, flertall_prob FROM Resultater_koalisjon_nasjonal WHERE SimuleringsID == " +  "'" + str(iter + 1) +"' ORDER BY SimuleringsID")
            SIM_DATA = db.engine.execute(QUERY)
            temp = deepcopy(coalitionKey)
            for res in SIM_DATA:
                temp[res[0]]['share'] = res[2]
                temp[res[0]]['mandater'] = res[1]
                temp[res[0]]['prob'] = res[3] * 100
            sharesData.append(temp)

        return json.dumps(sharesData)


@app.route('/partier_sperregrense')
def partier_sperregrense():


    CURRENT_PARTY_NAMES = db.engine.execute("select Name, Shortname, ID, R, G, B, LeftRight from Parties" )
    parties = [r[1] for r in CURRENT_PARTY_NAMES]
    returnData = dict.fromkeys(parties)

    # Need to make a fresh copy in memory
    for p in returnData.keys():
        returnData[p] = {'dates': [], 'dataseries':[], 'colors': None}

    QUERY = '''
    SELECT 
    Sperregrense.SimuleringsID, Sperregrense.Parti, Sperregrense.Prob_Sperr, Simulering.Dato, 
    Parties.Shortname, Parties.R, Parties.G, Parties.B
    FROM Sperregrense 
    Join Simulering ON Simulering.id = Sperregrense.SimuleringsID
    Join Parties ON Sperregrense.Parti = Parties.ID
    WHERE Sperregrense.SimuleringsID > 0
    ORDER BY Simulering.id
    '''

    DATA = db.engine.execute(text(QUERY))
    result = [{'simID':row[0], 'PartyID':row[1],'date':row[3],'party_name':row[4],'prob_sperr':row[2], 'R':row[5], 'G':row[6], 'B':row[7]} for row in DATA]

    print(returnData['H'])

    for i in range(len(result)):
    
        name = result[i]['party_name']
        returnData[name]['dataseries'].append(result[i]['prob_sperr'])

        print(len(returnData[name]['dataseries']))
        print(name, returnData[name])

        if result[i]['date'] not in returnData[name]['dates']:
            returnData[name]['dates'].append(result[i]['date'])

        if returnData[name]['colors'] == None:
            returnData[name]['colors']= { 'R': result[i]['R'],'G': result[i]['G'],'B': result[i]['B']}
    
    return json.dumps(returnData)
    

@app.route("/simulation_ids")
def simulation_ids():
    QUERY = text("SELECT max(id) from Simulering")
    return str(db.engine.execute(QUERY).fetchone()[0])

#----------------------------------------------
#Getting count for total for newest
#----------------------------------------------
@app.route("/resultater_part_mandater_total")
def resultater_part_mandater_total():
    pass

@app.route("/simulation_dates")
def simulation_dates():
    QUERY = text("SELECT id, Dato from Simulering WHERE id > 0")
    RES = db.engine.execute(QUERY)
    returnVal = []
    for r in RES:
        returnVal.append(r[1])
    return json.dumps(returnVal)


@app.route("/simInfo")
def simInfo():
    QUERY = text("SELECT Date from Info")
    res = db.engine.execute(QUERY).fetchone()[0]
    return res

@app.route("/maaalingerInfo")
def maalingerInfo():

    QUERY = text("SELECT max(id) from Simulering")
    id = str(db.engine.execute(QUERY).fetchone()[0])
     

    QUERY = '''
    SELECT ID, Institutt, Vekt_total, Utvalg, Dato from Maalinger 
    WHERE SimID = ? AND Vekt_total > ?
    ORDER BY Vekt_dato DESC, ID DESC;
    '''

    data = db.engine.execute(QUERY, (id,1e-10))#.fetchone()
    returnVal = []
    for d in data:
        returnVal.append(list(d))
    return json.dumps(returnVal)

@app.route("/getUtjevningsmandater")
def getUtjevningsmandater():

    QUERY = text("SELECT max(id) from Simulering")
    id = str(db.engine.execute(QUERY).fetchone()[0])

    QUERY = '''
    SELECT 
        Resultater_kandidat.KandidatID, 
        Resultater_kandidat.Parti, 
        Resultater_kandidat.Fylke, 
        Resultater_kandidat.Prob_utjevning,
        Parties.Shortname,
        Districts.Name
    FROM 
        Resultater_kandidat
    JOIN 
        Parties ON Resultater_kandidat.Parti = Parties.ID
    JOIN 
        Districts ON Resultater_kandidat.Fylke = Districts.ID
    WHERE 
        Resultater_kandidat.SimuleringsID = ? 
    ORDER BY 
        Resultater_kandidat.Prob_utjevning DESC
    LIMIT 
        100;
    '''

    data = db.engine.execute(QUERY, (id))
    returnVal = []
    for d in data:
        temp = {}
        temp['Fylke'] = d[5]
        temp['Parti'] = d[4]
        temp['Prob'] = d[3]
        returnVal.append(temp)

    return json.dumps(returnVal)
    



if __name__ == "__main__":
    app.run(debug=True)
    #app.run(host='192.168.1.88', port=5000, debug=True, threaded=False)
