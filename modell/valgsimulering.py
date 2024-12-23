
import numpy as np
import pandas as pd
from random import random
from vektingsmodell import VektingsmodellStandard
from valgsystem import ValgSystemNorge
from scipy.stats import norm

class Valgsimulering:

    def __init__(self, geoShareFiles, seatsFile, pollDatabase, uncertaintyFile, iterations = 1, mode = "deterministic"):

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
        #Simulation mode
        self._mode = mode


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



    def run(self):

        for iter in range(self._iterations):

            #Calclate vote shares
            self.calcVotes()
            #Calculate resutls
            vs = ValgSystemNorge(self._sharePartyConstituency, self._seats)
            vs.calcDistriktsmandater()
            vs.calcUtjevningsmandater()


    def calcVotes(self, geoShare = 0):

        #Votes nationally allocated to each party
        self._voteSharesNational = np.zeros((self._parties))

        #distribution of votes
        geoshareMatrix = self._geoShares[geoShare]

        #Just poll values
        if self._mode == "deterministic":
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

        #print(self._sharePartyConstituency)

        #print(geoshareMatrix)

if __name__ == "__main__":

    geoShareFile = ["data/fylkesfordeling2013.csv"]
    seatsFile = "data/mandater24.csv"
    pollDatabase = "data/poll/db/Valg_db.db"
    uncertaintyFile = ""

    v = Valgsimulering(geoShareFile, seatsFile, pollDatabase, uncertaintyFile)
    #v.calcVotes()
    v.run()
