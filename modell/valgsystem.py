
from mandatfordeling import fordeling

class ValgSystem:

    def __init__(self, fylker, partier, stemmer, mandater, divisor = 1.4):

        #Liste med fylker og navn
        self._fylker = fylker

        #Liste med partinavn og nummer i rekkefolgen av inndatafiler (navn: id)
        self._partier = partier

        #Array sortert etter rekkefolgen i partier med antall stemmer per parti
        self._stemmer = stemmer

        #Antall mandater, sortert etter parti og fylke
        self._mandater = mandater

        #Divisorverdi
        self._divisor = divisor

        #Tildelte mandater fordelt etter fylke og parti
        self._mandaterTildelt = np.zeros((len(self._fylker),len(self._partier)))


        #Beregner antall distriktsmandater
    def calcDistriktsmandater(self):
        for i in range(len(self._fylker)):
            self._mandaterTildelt[i] += fordeling(self._mandater[i], self._stemmer[i], self._divisor)


    def calcUtjevningsmandater(self):
        pass
