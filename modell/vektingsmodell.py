import sqlite3
from sqlalchemy import text
from copy import deepcopy
import numpy as np
import datetime
'''
    conn = sqlite3.connect("db/Valg_db.db")
    cursor = conn.cursor()
    findMax = "select max(ID_POP) from Malinger;"
    maxVal = cursor.execute(findMax).fetchone()[0]
    =HVIS(C6<=vektB;HVIS(C6<=vektA;1;1-(C6-vektA)/(vektB-vektA));0)

'''


class Vektingsmodell:

    def __init__(self, database, dateA = 15, dateB = 30):

        #Database with downloaded data on polls
        self._database = database
        #Connection
        self._conn = sqlite3.connect(self._database)
        #Cursor
        self._cursor = self._conn.cursor()
        #Connecting party name and number
        self._partiNavnNummer = {'AP':0, 'H':1, 'Frp':2, 'SV':3, 'Sp':4, 'KrF':5, 'V':6, 'MDG':7, 'R':8, 'A':9}

        self._dateA = dateA
        self._dateB = dateB

        #Extract raw data from database
    def getData(self, omraade):

        query = "SELECT AP, H, Frp, SV, Sp, KrF, V, MDG, R, A, Utvalgsstorrelse, Dato FROM Malinger WHERE Omraade == " +  "'" + omraade +  "'"

        self._results = []
        for row in self._conn.execute(query):
            temp = {}
            temp['AP'] = row[0]
            temp['H'] = row[1]
            temp['Frp'] = row[2]
            temp['SV'] = row[3]
            temp['Sp'] = row[4]
            temp['KrF'] = row[5]
            temp['V'] = row[6]
            temp['MDG'] = row[7]
            temp['R'] = row[8]
            temp['A'] = row[9]
            temp['N'] = row[10]
            temp['Dato'] = row[11]
            self._results.append(deepcopy(temp))

        #return results

    def numpfy(self):

        #Matrix of the observed party shares
        self._shareMarix = np.zeros((len(self._results),len(self._partiNavnNummer)))
        #Array with the number of observations
        self._observations = np.zeros((len(self._results),1))
        #Array with dates
        self._dates = np.zeros((len(self._partiNavnNummer),1))

        #Coupling shares with parties, observations and dates
        for i in range(len(self._results)):
            for parti, index in self._partiNavnNummer.items():
                self._shareMarix[i][index] = self._results[i][parti]

            self._observations[i] = self._results[i]['N']




if __name__ == "__main__":

    vm = Vektingsmodell("data/poll/db/Valg_db.db")
    vm.getData("Hele landet")
    vm.numpfy()
