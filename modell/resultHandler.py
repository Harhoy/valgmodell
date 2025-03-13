import numpy as np
import sqlite3
from valgsimulering import Valgsimulering
import datetime


'''
#------------------------------

Each function needs to satisfy the following criteria:

    Accepts the results-matrix
    Computes results according to a specific data model given by a table in the database
    The name of the function should equal the name of the database

Define different analysis kits (AK's) by a method an list of functions to be performed

#------------------------------
'''


class ResultHandler:

    def __init__(self, database, results, date, testMode = False):

        #Database where results are to be stored
        self._database = database
        #4D numpy array with results
        #STRUCTURE [iterations, 3, fylker, partier]
        self._results = results
        #Date of simulation
        self._date = date

        self._id = None

        self._testMode = testMode

        #Dimension
        self._fylker = results.shape[2]
        self._partier = results.shape[3]
        self._iterasjoner = results.shape[0]

        #Array storing different methods to be called
        self._analyses = []

        self._maxBlocks = 60

    def addPolls(self, polls):
        self._pollData = polls

    #-------------------------------
    #Database operations
    #-------------------------------

    def openDB(self):
        #print("Opening database", self._database)

        #Connection
        self._conn = sqlite3.connect(self._database)

        #Cursor
        self._cursor = self._conn.cursor()

        #if self._testMode:
        #    self.resetDB()

    def resetDB(self):
        tables = ['Resultater_parti','Resultater_kandidat','Simulering']
        for table in tables:
            print(table)
            self._cursor.execute("DELETE FROM " + table + ";")
        self._conn.commit()

    def insertSimulation(self):
        self.openDB()
        query = "insert into Simulering (Dato, id, iterasjoner) VALUES (?, ?, ?);"
        self._simuleringsID = self.getId("Simulering")
        data = (self._date.strftime("%m/%d/%Y"), self._simuleringsID, self._iterasjoner)
        self._cursor.execute(query, data)
        self.commitDB()
        self.closeDB()

    def closeDB(self):
        self._conn.close()

    def commitDB(self):
        self._conn.commit()

    def checkNotExistSimuleringsID(self, id):
        existCheck = "SELECT COUNT(1) from Simulering where id = " + str(id)
        res = self._cursor.execute(existCheck)
        count = res.fetchone()[0]
        if count == 0:
            return True
        return False

    def getId(self, table):
        findMax = "select max(id) from " + table + ";"
        maxVal = self._cursor.execute(findMax).fetchone()[0]
        if maxVal == None:
            self._id = 1
        else:
            self._id = maxVal + 1
        return self._id

    #-------------------------------
    #Analyses
    #-------------------------------

    def resultater_parti_counts(self):

        #In future, this should be rewritten in pandas...

        #Opening database
        self.openDB()

        #calculate the number of iterations for each number of seats
        tempDict2 = np.zeros((self._fylker, self._partier, 3))
        for party in range(self._partier):
            for fylke in range(self._fylker):
                tempDict = np.zeros((self._maxBlocks, 3))
                for iter in range(self._iterasjoner):

                    #distrikt
                    m1 = int(self._results[iter][0][fylke][party])
                    tempDict[m1][0] += 1
                    tempDict2[fylke][party][0] += (float(m1) - tempDict2[fylke][party][0]) / float(iter + 1)

                    #utjevning
                    m2 = int(self._results[iter][1][fylke][party])
                    tempDict[m2][1] += 1
                    tempDict2[fylke][party][1] += (float(m2) - tempDict2[fylke][party][1]) / float(iter + 1)

                    #total
                    m3 = int(self._results[iter][2][fylke][party])
                    tempDict[m3][2] += 1
                    tempDict2[fylke][party][2] += (float(m3) - tempDict2[fylke][party][2]) / float(iter + 1)

                #convert data to string
                distrikt = ""
                utjevning = ""
                total = ""

                distrikt_avg = ""
                utjevning_avg = ""
                total_avg = ""

                for i in range(self._maxBlocks):
                    distrikt += str(tempDict[i][0]) + ";"
                    utjevning += str(tempDict[i][1]) + ";"
                    total += str(tempDict[i][2]) + ";"

                # --- Write to db - counties ---
                q = "insert into Resultater_parti (id, SimuleringsID, Parti, Fylke, Resultat_distrikt, Resultat_utjevning, Resultat_total, Mandater_distrikt, Mandater_utjevning, Mandater_total) values (?,?,?,?,?,?,?,?,?,?);"
                data = (self.getId("Resultater_parti"), self._simuleringsID, party + 1, fylke + 1, distrikt, utjevning, total, round(tempDict2[fylke][party][0],1), round(tempDict2[fylke][party][1],1), round(tempDict2[fylke][party][2],1))
                self._cursor.execute(q, data)

                p_distrikt = 0
                p_utjevning = 0
                p_total = 0

                # --- Write to db - candidates ---
                for m in range(0,10):

                    #Tar bare med positive sannsynligheter
                    if m > 0:
                        q = "insert into Resultater_kandidat (id, SimuleringsID, KandidatID, Parti, Fylke, Prob_direkte, Prob_utjevning, Prob_total, Margin) values (?,?,?,?,?,?,?,?,?);"

                        margin = round(((1-float(p_total)/100.0)*float(p_total)/100.0)*100,0)

                        data = (self.getId("Resultater_kandidat"), self._simuleringsID, m, party + 1, fylke + 1,100 -p_distrikt, 100-p_utjevning, 100-p_total, margin)

                        self._cursor.execute(q, data)

                    p_distrikt += round(tempDict[m][0] / self._iterasjoner * 100, 1)
                    p_utjevning += round(tempDict[m][1] / self._iterasjoner * 100, 1)
                    p_total += round(tempDict[m][2] / self._iterasjoner * 100, 1)


        self.commitDB()
        self.closeDB()

    def resultater_kandidat(self):
        pass


    def resultater_snitt_nasjonalt(self):

        #Opening database
        self.openDB()

        #averages across parties - shares
        resShares = self._pollData.sum(axis=0) / self._iterasjoner

        #Snitt per iterasjon
        resSeats = self._results.sum(axis=0) / self._iterasjoner

        #total per parti, summert over fylker
        totals = resSeats[2].sum(axis=0)

        #koalisjoner
        q = "select Partier, ID from Koalisjon"
        res = self._cursor.execute(q)
        coalitions = {}
        for r in res:
            coalitions[r[1]] = {'parties':[], 'shares': 0.0, 'seats': 0.0}
            coalitions[r[1]]['parties'] = r[0].split("-")
            coalitions[r[1]]['parties'] = [int(x) for x in coalitions[r[1]]['parties']]

        #Checking results
        for party in range(self._partier):

            #Partiresultater
            share = round(resShares[party] * 100,1)
            seats = round(totals[party],1)
            query = "insert into Resultater_parti_national (id, SimuleringsID, Party, Share, Seats) values (?, ?, ?, ?, ?)"
            data = (self.getId("Resultater_parti_national"), self._simuleringsID, party + 1, share, seats)
            self._cursor.execute(query, data)

            for key, data in coalitions.items():
                if party + 1 in data['parties']:
                    data['seats'] += seats
                    data['shares'] += share

        #koliasjonsresultater
        for key, data in coalitions.items():

            query = "insert into Resultater_koalisjon_nasjonal (Koalisjon, SimuleringsID, Mandater, Share) values (?, ?, ? ,?)"
            data = (key, self._simuleringsID, data['seats'], data['shares'])
            self._cursor.execute(query, data)

        self.commitDB()
        self.closeDB()


    #-------------------------------
    #Analyses kits
    #-------------------------------

    def AKBasis(self):
        self._analyses.append(self.resultater_parti_counts)
        self._analyses.append(self.resultater_kandidat)
        self._analyses.append(self.resultater_snitt_nasjonalt)

    #-------------------------------
    #Run the program
    #-------------------------------


    def run(self):

        #KITS TO INCLUDE
        self.AKBasis()
        self.insertSimulation()

        for a in self._analyses:
            a()



if __name__ == "__main__":

    geoShareFile = ["data/fylkesfordeling2013.csv"]
    seatsFile = "data/mandater24.csv"
    pollDatabase = "data/poll/db/Valg_db.db"
    uncertaintyFile = "data/usikkerhet.csv"
    resultsDatabase = "data/databaser/mainDB_TEST-kopi.db"
    dato = datetime.datetime.now()

    #delete data
    conn = sqlite3.connect(resultsDatabase)
    cur = conn.cursor()
    cur.execute("DELETE FROM Simulering;")
    conn.commit()
    cur.execute("DELETE FROM Resultater_parti;")
    conn.commit()
    cur.execute("DELETE FROM Resultater_kandidat;")
    conn.commit()
    cur.execute("DELETE FROM Resultater_parti_national;")
    conn.commit()
    cur.execute("DELETE FROM Info;")
    conn.commit()
    cur.execute("DELETE FROM Resultater_koalisjon_nasjonal;")
    conn.commit()

    simuleringsmodell = Valgsimulering(geoShareFile, seatsFile, pollDatabase, uncertaintyFile, dato, 1000)
    resultshandler = ResultHandler(resultsDatabase, simuleringsmodell.run(), dato)
    resultshandler.addPolls(simuleringsmodell.returnPolls())

    resultshandler.run()
