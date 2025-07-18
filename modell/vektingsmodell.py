import sqlite3
from sqlalchemy import text
from copy import deepcopy
import numpy as np
import datetime

'''
    #-----------------------
    Weighting model class
    #-----------------------



    Added weighting by dates

    #-----------------------
    #Database structure
    #-----------------------

    getdata should return an array with M polling shares, a float of N observations and a date

'''


smallNumber = 0.0000000000000000001

class VektingsmodellStandard:

    def __init__(self, database, dateNow, dateA = 20.0, dateB = 40.0, method = "Standard", omraade = "Hele landet"):

        #Database with downloaded data on polls
        self._database = database
        #Connection
        self._conn = sqlite3.connect(self._database)
        #Cursor
        self._cursor = self._conn.cursor()
        #Connecting party name and number
        self._partiNavnNummer =  {'AP':0, 'Frp':1, 'H':2, 'Krf':3, 'MDG':4, 'R':5, 'Sp':6, 'SV':7, 'V':8, 'A':9}
        #Date A in weighting model
        self._dateA = dateA
        #Date B in weighting model
        self._dateB = dateB
        #Method to weight
        self._method = method
        #Geographical area
        self._omraade = omraade
        #Date to calculate from
        self._dateNow = dateNow

        #Extract raw data from database
    def getData(self):

        query = "SELECT AP, Frp, H, Krf, MDG, R, Sp, SV, V, A, Utvalgsstorrelse, Dato, Aar, Institutt, ID_POP FROM Malinger WHERE Omraade == " +  "'" + self._omraade +  "'"



        self._results = []
        for row in self._conn.execute(query):
            temp = {}
            temp['AP'] = row[0]
            temp['Frp'] = row[1]
            temp['H'] = row[2]
            temp['Krf'] = row[3]
            temp['MDG'] = row[4]
            temp['R'] = row[5]
            temp['Sp'] = row[6]
            temp['SV'] = row[7]
            temp['V'] = row[8]
            temp['A'] = row[9]
            temp['N'] = row[10]
            temp['Dato'] = row[11]
            temp['Aar'] = row[12]
            temp['vekt'] = 0
            temp['vekt_total'] = 0
            temp['Institutt'] = row[13]
            temp['ID_POP'] = row[14]
            self._results.append(deepcopy(temp))

            #print(row[11])

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
            aar = self._results[i]['Aar']
            #Start of poll (Y M D)
            dato1 = datetime.datetime(aar, int(dato[1]), int(dato[0]))
            #End of poll
            dato2 = datetime.datetime(aar, int(dato[3]), int(dato[2]))

            #Date distance weight
            self._dates[i] = self.dateWeight(dato2)
            self._results[i]['vekt'] = self._dates[i][0]

        #convert matrix to fractions
        self._shareMarix = self._shareMarix / 100.0


        #Calculates the weight given to each observation based on the date
    def dateWeight(self, date):
        now = self._dateNow
        diff = float((now - date).days)

        if diff < 0:
            return smallNumber

        if diff < self._dateB:
            if diff < self._dateA:
                return 1
            else:
                return 1 - (diff - self._dateA) / (self._dateB - self._dateA)
        return smallNumber

        #Method to calculate averages according to Jackman (2005) - plus day count
    def calcWeightedAveragesStandard(self):

        #Matrix of weights
        self._weigthMatrix = np.zeros((len(self._results),len(self._partiNavnNummer)))
        #Matrix of weighted shares
        self._shareMarixWeighted = np.zeros((len(self._results),len(self._partiNavnNummer)))

        self._standardDeviationWeighted =  np.zeros((len(self._partiNavnNummer),1))

        self._totalObs = 0

        #Calculating intermediate matrix
        for i in range(len(self._weigthMatrix)):
            for j in range(len(self._weigthMatrix[0])):
                self._weigthMatrix[i][j] = self._dates[i] * self._observations[i] / (self._shareMarix[i][j] * (1 - self._shareMarix[i][j])) 

                self._totalObs += self._dates[i] * self._observations[i]
 
        #Summing av updating to give the weights
        columnSums = self._weigthMatrix.sum(axis=0)         
        for i in range(len(self._weigthMatrix[0])):
            if columnSums[i] > 1e-9:
                self._weigthMatrix[:, i] = self._weigthMatrix[:, i] / columnSums[i]
                self._standardDeviationWeighted[i] = (1.0 / columnSums[i]) ** .5
            else:
                self._weigthMatrix[:, i] = 0
                self._standardDeviationWeighted[i] = 10000

        w = np.mean(self._weigthMatrix, axis=1)
        for i in range(len(self._results)):
            self._results[i]['vekt_total'] = w[i]

        #Finally weighting the matrix shares
        self._shareMarixWeighted = np.multiply(self._shareMarix, self._weigthMatrix).sum(axis=0)

        #print(self._shareMarixWeighted)

        #Transpose
        self._standardDeviationWeighted = self._standardDeviationWeighted.T


    def run(self):
        self.getData()
        self.numpify()

        

        if len(self._results) > 0:

            if self._method == "Standard":
                self.calcWeightedAveragesStandard()

            return self._shareMarixWeighted, self._standardDeviationWeighted, self._totalObs
        
        return None

if __name__ == "__main__":

    date = datetime.datetime(2025, 5, 29, 18, 00)

    vm = VektingsmodellStandard("../dataGet/db/Valg_db.db", date, 20,40)
    #print(datetime.datetime.now())
    r = vm.run()
    print(r[0])
    print(r[1])
    for i in range(len(vm._results)):
        if vm._results[i]['vekt'] > 1e-10:
            print(vm._results[i]['vekt'])
