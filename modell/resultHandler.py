import numpy as np
import sqlite3
from valgsimulering import Valgsimulering
import datetime
from math import log
from datetime import date as dato_find


'''
#------------------------------

Each function needs to satisfy the following criteria:

    Accepts the results-matrix
    Computes results according to a specific data model given by a table in the database
    The name of the function should equal the name of the database

Define different analysis kits (AK's) by a method an list of functions to be performed

#------------------------------
'''

def greaterThan(x, t):
    if x >= t:
        return 1
    return 0

def lessThan(x, t):
    if x <= t:
        return 1
    return 0

gt_vec = np.vectorize(greaterThan)
lt_vec = np.vectorize(lessThan)

class CoalitionHandler:

    def __init__(self, data, coalitions):

        # Dimensions [iterations, 1, fylker, partier] (results from handler, but only total seats)
        self._data = data[:, 2, :, :]

        # Dimensions [parties, coalitions], 0-1 matrix
        self._coalitions = coalitions

        #self.calcProbs()
        
    def calcProbs(self, threshold = 85, axis = 0, gt = True):
        
        """
        Calculate results for one coalition.
        Args: 
            axis (int): set to 0 for national values and 1 for county-specific lists
            threshold (int): number of simulations AT or (ABOVE - gt = True) (BELOW - gt = False) given number

        Returns:
            list of str: probabilities for coaltions over threshold        
        """

        stats = {}
        returns = []
        sum_seats = np.sum(self._data, axis=1).T        
        for i in range(len(self._coalitions[0])):

            # Get N copies of coalition i
            c_temp = np.tile(self._coalitions[:, i], (len(sum_seats[0]),1)).T

            # Find sum over iterations and sum to totals (iterations, coaltion sums)
            c_temp = np.sum(np.multiply(sum_seats, c_temp), axis=0)

            # Stats
            stats[str(i+1)] = {'mean': np.mean(c_temp), 'median': np.percentile(c_temp, 50), '10p': np.percentile(c_temp, 90), '90p': np.percentile(c_temp, 10)}

            # Mean of 0-1 matrix 
            if gt:
                returns.append(np.mean(gt_vec(c_temp, threshold)))
            else:
                returns.append(np.mean(lt_vec(c_temp, threshold)))                

        return returns, stats


class ResultHandler:

    def __init__(self, database, results, date, testMode = False):

        #Database where results are to be stored
        self._database = database

        #4D numpy array with  main results
        #STRUCTURE [iterations, 3, fylker, partier]
        self._results = results[0]

        # Vector with sperregrense-data
        self._sperregrenseMatrix = results[1]

        # Maalinger
        self._maalinger = results[2]

        #Date of simulation
        self._date = date

        # ID
        self._id = None

        # Test mode
        self._testMode = testMode

        #Dimension
        self._fylker = results[0].shape[2]
        self._partier = results[0].shape[3]
        self._iterasjoner = results[0].shape[0]

        #Array storing different methods to be called
        self._analyses = []

        self._maxBlocks = 60

    def addPolls(self, polls):
        self._pollData = polls
    
    def addSperregrense(self, sperregrenseMatrix):
        self._sperregrenseMatrix = sperregrenseMatrix

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
            self._cursor.execute("DELETE FROM " + table + ";")
        self._conn.commit()

    def insertSimulation(self, otherId = None):
        self.openDB()
        query = "insert into Simulering (Dato, id, iterasjoner) VALUES (?, ?, ?);"

        # Use standard numbering unless there is some signal value to be used for a special run
        if otherId == None:
            self._simuleringsID = self.getId("Simulering")
        else:
            self._simuleringsID = otherId

        # Date instead of week
        date = self._date#.strftime("%m/%d/%Y")
        week = str(datetime.date(date.year, date.month, date.day).isocalendar()[1])     
        data = (week, self._simuleringsID, self._iterasjoner)
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

                        margin = (1-float(p_total)/100.0)*float(p_total)/100.0

                        data = (self.getId("Resultater_kandidat"), self._simuleringsID, m, party + 1, fylke + 1,100 -p_distrikt, 100-p_utjevning, 100-p_total, margin)

                        self._cursor.execute(q, data)

                    p_distrikt += round(tempDict[m][0] / self._iterasjoner * 100, 1)
                    p_utjevning += round(tempDict[m][1] / self._iterasjoner * 100, 1)
                    p_total += round(tempDict[m][2] / self._iterasjoner * 100, 1)


        self.commitDB()
        self.closeDB()

    def resultater_kandidat(self):
        pass

    def sperregrense(self):
        pass

    def resultater_sperregrense(self):
        #Opening database
        self.openDB()        

        # Sum over overations
        self._sperregrense = self._sperregrenseMatrix.mean(axis= 0)

        for party in range(self._partier):
            prob = round(self._sperregrense[party] * 100,1)
            query = "insert into Sperregrense (SimuleringsID, Parti, Prob_Sperr) values (?, ?, ?)"
            data = (self._simuleringsID, party + 1, prob)
            self._cursor.execute(query, data) 

        self.commitDB()
        self.closeDB()


    def resultater_snitt_nasjonalt(self):

        #Opening database
        self.openDB()

        #averages across parties - shares
        resShares = self._pollData.sum(axis=0) / self._iterasjoner

        #Snitt per iterasjon
        resSeats = self._results.sum(axis=0) / self._iterasjoner

        #total per parti, summert over fylker
        totals = resSeats[2].sum(axis=0)

        
        q = "SELECT COUNT(*) FROM Koalisjon"
        coalitions_matrix = np.zeros((self._partier, self._cursor.execute(q).fetchone()[0]))
        
        #koalisjoner
        q = "select Partier, ID from Koalisjon"
        res = self._cursor.execute(q)
        coalitions = {}
        for r in res:
 
            coalitions[r[1]] = {'parties':[], 'shares': 0.0, 'seats': 0.0}
            coalitions[r[1]]['parties'] = r[0].split("-")
            coalitions[r[1]]['parties'] = [int(x) for x in coalitions[r[1]]['parties']]

            for i in range(len(coalitions[r[1]]['parties'])):
                p = coalitions[r[1]]['parties'][i] - 1
                c = r[1] - 1                
                coalitions_matrix[p][c] = 1


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

        ca = CoalitionHandler(self._results, coalitions_matrix)
        probs, stats = ca.calcProbs()
        #koliasjonsresultater
        for key, data in coalitions.items():
            query = "insert into Resultater_koalisjon_nasjonal (Koalisjon, SimuleringsID, Mandater, Share, flertall_prob, Mean_seats, Median_seats, p90_seats, p10_seats) values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            data = (key, self._simuleringsID, data['seats'], data['shares'], probs[key - 1], stats[str(key)]['mean'], stats[str(key)]['median'], stats[str(key)]['10p'],stats[str(key)]['90p'] )
            self._cursor.execute(query, data)



        self.commitDB()
        self.closeDB()

    def maalingerInformation(self):
        
        #Opening database
        self.openDB()

        for m in self._maalinger:
            
            query = '''
            insert into Maalinger
            (SimID, ID, Institutt, Vekt_dato, Vekt_total, Utvalg, Dato)
            values
            (?, ?, ?, ?, ?, ?, ?)
            '''
            
            data = (self._simuleringsID, m['ID_POP'], m['Institutt'], m['vekt'],  m['vekt_total'], int(m['N']) , m['Dato'] + " - " + str(m['Aar']))

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
        self._analyses.append(self.resultater_sperregrense)
        self._analyses.append(self.maalingerInformation)

    #-------------------------------
    #Run the program
    #-------------------------------


    def run(self, otherId = None):

        #KITS TO INCLUDE
        self.AKBasis()
        self.insertSimulation(otherId)

        for a in self._analyses:
            a()



if __name__ == "__main__":

    geoShareFile = [{'file': "data/fylkesfordeling2013.csv", 'prop': 0.05},
                    {'file': "data/fylkesfordeling2017.csv", 'prop': 0.35},
                    {'file': "data/fylkesfordeling2021.csv", 'prop': 0.60}]

    seatsFile = "data/mandater24.csv"
    pollDatabase = "../dataGet/db/Valg_db.db"
    uncertaintyFile = "data/usikkerhet.csv"
    resultsDatabase = "data/databaser/mainDB_TEST-kopi.db"
    constituency_file = "data/countylist.csv"
    dato = datetime.datetime.now()

    dato = dato_find(2025, 7, 4)
    dato = datetime.datetime.combine(dato, datetime.datetime.min.time())

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
    cur.execute("DELETE FROM Maalinger;")
    conn.commit()

    simuleringsmodell = Valgsimulering(geoShareFile, seatsFile, pollDatabase, uncertaintyFile, dato, constituency_file, 100)
    simuleringsmodell._regional = False
    resultshandler = ResultHandler(resultsDatabase, simuleringsmodell.run(), dato)
    resultshandler.addPolls(simuleringsmodell.returnPolls())
    resultshandler.run()
