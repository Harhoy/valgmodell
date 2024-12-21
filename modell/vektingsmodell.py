import sqlite3
from sqlalchemy import text
from copy import deepcopy
import numpy as np
import datetime

'''
    #-----------------------
    Weighting model class
    #-----------------------

    Implements a standard weighting model based on Jackman (2005): Pooling the Polls Over an Election Campaign. Australian Journal of Political Science, Vol. 40, No. 4, December, pp. 499–517

    Added weighting by dates

    #-----------------------
    #Database structure
    #-----------------------

    getdata should return an array with M polling shares, a float of N observations and a date

'''

class VektingsmodellStandard:

    def __init__(self, database, dateA = 15.0, dateB = 30.0, method = "Standard", omraade = "Hele landet"):

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

        self._method = method

        self._omraade = omraade

        #Extract raw data from database
    def getData(self):

        query = "SELECT AP, H, Frp, SV, Sp, KrF, V, MDG, R, A, Utvalgsstorrelse, Dato FROM Malinger WHERE Omraade == " +  "'" + self._omraade +  "'"

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

        #Move data over to numpy arrays
    def numpify(self):

        #Matrix of the observed party shares
        self._shareMarix = np.zeros((len(self._results),len(self._partiNavnNummer)))
        #Array with the number of observations
        self._observations = np.zeros((len(self._results),1))
        #Array with dates
        self._dates = np.zeros((len(self._results),1))

        #Coupling shares with parties, observations and dates
        for i in range(len(self._results)):
            for parti, index in self._partiNavnNummer.items():
                self._shareMarix[i][index] = self._results[i][parti]

            #Number of observations
            self._observations[i] = self._results[i]['N']

            dato = self._results[i]['Dato'].replace(" - ", "/").split("/")
            #Start of poll
            dato1 = datetime.datetime(2024,int(dato[1]), int(dato[0]))
            #End of poll
            dato2 = datetime.datetime(2024,int(dato[3]), int(dato[2]))

            #Date distance weight
            self._dates[i] = self.dateWeight(dato1)

        #convert matrix to fractions

        self._shareMarix = self._shareMarix / 100.0


        #Calculates the weight given to each observation based on the date
    def dateWeight(self, date):
        now = datetime.datetime.now()
        diff = float((now - date).days)
        if diff < self._dateB:
            if diff < self._dateA:
                return 1
            else:
                return 1 - (diff - self._dateA) / (self._dateB - self._dateA)
        return 0

        #Method to calculate averages according to Jackman (2005) - plus day count
    def calcWeightedAveragesStandard(self):

        #Matrix of weights
        self._weigthMatrix = np.zeros((len(self._results),len(self._partiNavnNummer)))
        #Matrix of weighted shares
        self._shareMarixWeighted = np.zeros((len(self._results),len(self._partiNavnNummer)))

        self._standardDeviationWeighted =  np.zeros((len(self._partiNavnNummer),1))

        #Calculating intermediate matrix
        for i in range(len(self._weigthMatrix)):
            for j in range(len(self._weigthMatrix[0])):
                self._weigthMatrix[i][j] = self._observations[i] / (self._shareMarix[i][j] * (1 - self._shareMarix[i][j])) * self._dates[i]

        #Summing av updating to give the weights
        columnSums = self._weigthMatrix.sum(axis=0)
        for i in range(len(self._weigthMatrix[0])):
            self._weigthMatrix[:, i] = self._weigthMatrix[:, i] / columnSums[i]
            self._standardDeviationWeighted[i] = (1.0 / columnSums[i]) ** .5

        #Finally weighting the matrix shares
        self._shareMarixWeighted = np.multiply(self._shareMarix, self._weigthMatrix).sum(axis=0)

        #Transpose
        self._standardDeviationWeighted = self._standardDeviationWeighted.T

    def run(self):
        self.getData()
        self.numpify()

        if self._method == "Standard":
            self.calcWeightedAveragesStandard()

        return self._shareMarixWeighted, self._standardDeviationWeighted

if __name__ == "__main__":

    vm = VektingsmodellStandard("data/poll/db/Valg_db.db")
    r = vm.run()
    print(r[0])
    print(r[1])
