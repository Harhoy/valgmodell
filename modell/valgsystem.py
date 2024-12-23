
from mandatfordeling import fordeling
import numpy as np

class ValgSystemNorge:

    def __init__(self, stemmer, mandater, divisor = 1.4, sperregrense = 0.04):

        #Array sortert etter rekkefolgen i partier med antall stemmer per parti
        self._stemmer = stemmer

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

        #Beregner antall distriktsmandater
    def calcDistriktsmandater(self):
        for i in range(self._fylker):
            self._mandaterTildelt[i] = fordeling(self._mandater[i], self._stemmer[i], self._divisor)

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
                self._restKvotientMatrise[fylke][party] =    (self._stemmer[fylke][parti] / (2 * float(mandaterTildeltNational(fylke, parti)) + 1)) / (votesFylke(fylke) / mandater(fylke))


        print("U",self._utjevningsmandater)

        '''



        'BEREGNER FORDELING TIL FYLKE

        'samlet antall stemmer i fylket totalt'

        'https://www.valg.no/om-valg/valgene-i-norge/stortingsvalg/fordeling-av-utjevningsmandater/
        'restkvotient
        For fylke = 1 To 19
            For parti = 1 To 9
                restkvotMatrise(fylke, parti) = (votesRegional(fylke, parti) / (2 * CDbl(mandaterTildeltNational(fylke, parti)) + 1)) / (votesFylke(fylke) / mandater(fylke))
            Next parti
        Next fylke


        'utjevningsmandater
        tildelteUtjevningsmandater = 0

        For fylke = 1 To 19
            uMandanter(fylke) = 1
        Next fylke

        Do While tildelteUtjevningsmandater < 19

            minVal = -1
            minParti = 0
            minFylke = 0

            'treigt....
            For fylke = 1 To 19
                For parti = 1 To 9
                    If restkvotMatrise(fylke, parti) > minVal And uMandanter(fylke) > 0 And utjevningsmandater(parti) > 0 Then
                        minVal = restkvotMatrise(fylke, parti)
                        minParti = parti
                        minFylke = fylke
                    End If
                Next parti
            Next fylke

            'Ett mandat, per fylke
            utjevningsMandaterTildeltNational(minFylke, minParti) = 1

            'Mandater er fordelt
            uMandanter(minFylke) = 0

            'Ett mindre mandat
            utjevningsmandater(minParti) = utjevningsmandater(minParti) - 1

            'Skal se bort fra denne kvotienten
            restkvotMatrise(minFylke, minParti) = -1

            'Samlet sett ett faerre utjevningsmandat totalt
            tildelteUtjevningsmandater = tildelteUtjevningsmandater + 1
        '''


    def getDistriktsmandater(self):
        return self._mandaterTildelt

    def getUtjevningsmandater(self):
        return self._utjevningsmandater
