
import numpy as np
import pandas as pd
from random import random
from vektingsmodell import VektingsmodellStandard
from valgsystem import ValgSystemNorge
from scipy.stats import norm
from tqdm import tqdm

class Valgsimulering:

    def __init__(self, geoShareFiles, seatsFile, pollDatabase, uncertaintyFile, iterations = 1):

        #Files with distribution of votes across constituencies
        self._geoShareFiles = geoShareFiles
        #Seats per constituency
        self._seatsFile = seatsFile
        #Database with polling data
        self._pollDatabase = pollDatabase
        #File with estimated uncertainty
        self._uncertaintyFile = uncertaintyFile
        #Numbfer of iterations
        self._iterations = iterations
        #Read data and populate data structures
        self.setup()



    def setup(self):

        # --- Polling data --- #
        self._vektingsmodell = VektingsmodellStandard(self._pollDatabase)
        self._pollData = self._vektingsmodell.run()

        # --- Seats data --- #
        self._seats = pd.read_csv(self._seatsFile, sep=';', header=None).values

        # --- Geo shares --- #
        self._geoShares = []
        for f in self._geoShareFiles:
            self._geoShares.append(pd.read_csv(f, sep=';', header=None).values)

        # --- # of parties --- #
        self._parties = len(self._geoShares[0][0])

        # --- # of constituencies --- #
        self._constituencies = len(self._geoShares[0])


    #Running the simulation
    def run(self):

        #Iterations, (direct, utjevning, total), counties, parties
        self._resultMatrix = np.zeros((self._iterations, 3, len(self._geoShares[0]), self._parties))

        for iter in tqdm(range(self._iterations)):
            #Calclate vote shares
            self.calcVotes()
            #New system with poll numbers
            vs = ValgSystemNorge(self._sharePartyConstituency, self._seats)
            #Calculate direktemandater
            vs.calcDistriktsmandater()
            #Calculate utjevningsmandater
            vs.calcUtjevningsmandater()

            #Distriktsmandater
            self._resultMatrix[iter][0] = vs.getDistriktsmandater()
            #utjevningsmandater
            self._resultMatrix[iter][1] = vs.getUtjevningsmandater()
            #Sum mandater
            self._resultMatrix[iter][2] = self._resultMatrix[iter][0] + self._resultMatrix[iter][1]


    def calcVotes(self, geoShare = 0):

        #Votes nationally allocated to each party
        self._voteSharesNational = np.zeros((self._parties))

        #distribution of votes
        geoshareMatrix = self._geoShares[geoShare]

        #Just poll values
        if self._iterations == 1:
            for party in range(self._parties):
                self._voteSharesNational[party] = self._pollData[0][party]

        #Simulated values
        else:
            #Random draws
            for party in range(self._parties):
                self._voteSharesNational[party] = norm.ppf(random(), self._pollData[0][party], self._pollData[1][0][party])

            #Normalize
            for party in range(self._parties):
                self._voteSharesNational[party] = self._voteSharesNational[party] / self._voteSharesNational.sum()

        #Vote shares per constituency, per party
        self._sharePartyConstituency = np.zeros((self._constituencies, self._parties))
        for party in range(self._parties):
            for constituency in range(self._constituencies):
                self._sharePartyConstituency[constituency][party] = geoshareMatrix[constituency][party] * self._voteSharesNational[party]


if __name__ == "__main__":

    geoShareFile = ["data/fylkesfordeling2013.csv"]
    seatsFile = "data/mandater24.csv"
    pollDatabase = "data/poll/db/Valg_db.db"
    uncertaintyFile = ""

    v = Valgsimulering(geoShareFile, seatsFile, pollDatabase, uncertaintyFile, 100)
    v.run()
