import numpy as np


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

    def __init__(self, database, results):

        #Database where results are to be stored
        self._database = database
        #4D numpy array with results
        #STRUCTURE [iterations, 3, fylker, partier]
        self._results = results

        #Dimensions
        '''
        self._fylker = results.shape[2]
        self._partier = results.shape[3]
        self._iterasjoner = results.shape[0]
        '''

        #Array storing different methods to be called
        self._analyses = []

    #-------------------------------
    #Database operations
    #-------------------------------

    def openDB(self):
        pass

    def closeDB(self):
        pass

    def commitDB(self):
        pass

    #-------------------------------
    #Analyses
    #-------------------------------

    def resultater_parti(self):
        print("hallo")
        pass

    def resultater_kandidat(self):
        print("hei")
        pass

    #-------------------------------
    #Analyses kits
    #-------------------------------

    def AKBasis(self):
        self._analyses.append(self.resultater_parti)
        self._analyses.append(self.resultater_kandidat)

    #-------------------------------
    #Run the program
    #-------------------------------


    def run(self):

        #KITS TO INCLUDE
        self.AKBasis()

        self.openDB()

        for a in self._analyses:
            a()

        self.commitDB()
        self.closeDB()


if __name__ == "__main__":

    rh = ResultHandler(",","s")
    rh.run()
