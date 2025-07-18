
from mandatfordeling import fordeling
import numpy as np
from copy import deepcopy


VOTES_CONSTANT = 1

class ValgSystemNorge:

    def __init__(self, stemmer, mandater, divisor = 1.4, sperregrense = 0.04):

        #Array sortert etter rekkefolgen i partier med antall stemmer per parti
        self._stemmer = deepcopy(stemmer)
        self._stemmerCopy = deepcopy(stemmer) * VOTES_CONSTANT

        #Liste med fylker og navn
        self._fylker = len(self._stemmer)

        #Liste med partinavn og nummer i rekkefolgen av inndatafiler (navn: id)
        self._partier = len(self._stemmer[0])

        #Antall mandater, sortert etter parti og fylke
        self._mandater = mandater[:, 0]

        #Antall utjevningsmandater
        self._utjevningsmandater = mandater[:, 1]

        #Divisorverdi
        self._divisor = divisor

        #Tildelte mandater fordelt etter fylke og parti
        self._mandaterTildelt = np.zeros((self._fylker,self._partier))

        #sperregrense
        self._sperregrense = sperregrense

        #Total number of seats in parliament
        self._totaltMandater = self._mandater.sum() + self._utjevningsmandater.sum()

        #utjevningsmandater to each party
        self._utjevningsmandater = np.zeros((self._partier,1))

        #Matrix of restkvotienter per fylke
        self._restKvotientMatrise = np.zeros((self._fylker, self._partier))

        self._overSperregrense = np.ones((self._partier))

        #Beregner antall distriktsmandater
    def calcDistriktsmandater(self):
        for i in range(self._fylker):
            self._mandaterTildelt[i] = fordeling(self._mandater[i], self._stemmer[i] * VOTES_CONSTANT, self._divisor)

        #Beregner antall utjevningsmandater
    def calcUtjevningsmandater(self):
        '''
        Calculation method: https://lovdata.no/dokument/NL/lov/2023-06-16-62/KAPITTEL_11#KAPITTEL_11
        11-7.Fordelingen av utjevningsmandatene mellom partiene ved stortingsvalg
        '''
        #remove votes below
        for party in range(self._partier):
            if self._stemmer[:, party].sum() < self._sperregrense:
            
                #Removing votes for party not participating in utjevningsmandater
                self._stemmer[:, party] = 0
                #reducing the totalt number of seats ()
                self._totaltMandater -= self._mandaterTildelt[:, party].sum()

                # Havner under sperregrensen
                self._overSperregrense[party] = 0


        #Redistribution of
        refordeling = True
        k = 0
        while refordeling:

                #Reset
                refordeling = False

                #Seats of contry is one constituency (Ledd 3)
                nasjonalMandat = fordeling(self._totaltMandater, self._stemmer.sum(axis=0), self._divisor)

                #direkte utjevningsmandater (Ledd 4)
                for party in range(self._partier):
                    if self._stemmer[:, party].sum() >= self._sperregrense:
                        self._utjevningsmandater[party] = nasjonalMandat[party] - self._mandaterTildelt.sum(axis=0)[party]

                    
                    #Need to redistribute votes from parties that have more seats in direct allocation (Ledd 5)
                    if self._utjevningsmandater[party] < 0:

                        #setting votes to zero -> getting no seats in next round
                        self._stemmer[:, party] = 0
                        #setting utjevningsmandater to zero -> check for redistribution is correct
                        self._utjevningsmandater[party] = 0
                        #reducing the number of seats once again
                        self._totaltMandater -= self._mandaterTildelt[:, party].sum()
                        #indicate redistribution needed in next round
                        refordeling = True

                #If too many iterations pass, there is likely an error...
                k += 1
                if k > 20:
                    raise Exception("Maximum number of redistributions made")


        #restkvotient matrix
        for fylke in range(self._fylker):
            for party in range(self._partier):
                self._restKvotientMatrise[fylke][party] = (self._stemmerCopy[fylke][party] / (2 * float(self._mandaterTildelt[fylke][party]) + 1)) / (self._stemmerCopy.sum(axis=1)[fylke] / self._mandater[fylke])

        #allocating to each county
        tildelteUtjevningsmandater = 0
        uMandater = [1] * self._fylker
        self._utjevningsmandaterTildeltFylkesmatrise = np.zeros((self._fylker, self._partier))

        while tildelteUtjevningsmandater < self._fylker:

            #finding the largest restkvotient
            minVal = -1
            minParti = 0
            minFylke = 0
            for fylke in range(self._fylker):
                for party in range(self._partier):
                    if self._restKvotientMatrise[fylke][party] > minVal and uMandater[fylke] > 0 and self._utjevningsmandater[party] > 0:
                        minVal = self._restKvotientMatrise[fylke][party]
                        minParti = party
                        minFylke = fylke

            #One seat per county
            self._utjevningsmandaterTildeltFylkesmatrise[minFylke][minParti] = 1
            #No more seats in this county
            uMandater[minFylke] = 0
            #One fewer seats for given party
            self._utjevningsmandater[minParti] = self._utjevningsmandater[minParti] - 1
            #Disregard this entry in future min value searches
            self._restKvotientMatrise[fylke][party] = -1
            #One less seat on total to allocate
            tildelteUtjevningsmandater = tildelteUtjevningsmandater + 1


    def getDistriktsmandater(self):
        return self._mandaterTildelt

    def getUtjevningsmandater(self):
        return self._utjevningsmandaterTildeltFylkesmatrise

    def getOverSperrengrense(self):
        return self._overSperregrense
