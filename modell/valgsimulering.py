
import numpy as np
import pandas as pd
from random import random
from random import randrange
from vektingsmodell import VektingsmodellStandard
from valgsystem import ValgSystemNorge
from scipy.stats import norm
from tqdm import tqdm
import datetime
from random import random
from copy import deepcopy
from utils import *

class Valgsimulering:

    def __init__(self, geoShareFiles, seatsFile, pollDatabase, uncertaintyFile, dato, constituency_file, iterations = 1):

        # Files with distribution of votes across constituencies
        self._geoShareFiles = geoShareFiles
        # Seats per constituency
        self._seatsFile = seatsFile
        # Database with polling data
        self._pollDatabase = pollDatabase
        # File with estimated uncertainty
        self._uncertaintyFile = uncertaintyFile
        # Numbfer of iterations
        self._iterations = iterations
        # dato
        self._dato = dato

        self._regional = True

        self._constituency_file = constituency_file

        self._sperregrense = 0.04

        self._divisor = 1.4

        # Read data and populate data structures
        self.setup()

        self._otherPartyIndex = -1



    def setup(self):

        #  --- Polling data --- # 
        self._vektingsmodell = VektingsmodellStandard(self._pollDatabase, self._dato)
        self._pollData = self._vektingsmodell.run()

        #  --- Seats data --- # 
        self._seats = pd.read_csv(self._seatsFile, sep=';', header=None).values

        #  --- Uncertainty data --- # 
        self._uncertainty = pd.read_csv(self._uncertaintyFile, sep=';', header=None).values

        #  --- Geo shares --- # 
        self._geoShares = []
        integers = []
        for f in self._geoShareFiles:
            self._geoShares.append(pd.read_csv(f['file'], sep=';', header=None).values)
            integers.append({'prop': f['prop'], 'val': len(self._geoShares) - 1})
        self._geoShareList = randomIntegerList(integers)


        #  --- #  of parties --- # 
        self._parties = len(self._geoShares[0][0]) - 1 # Minus sum

        #  --- #  of constituencies --- # 
        self._constituencies = len(self._geoShares[0])

        #  --- reading counties --- # 
        cf = pd.read_csv(self._constituency_file, sep =",")
        self._counties = cf.set_index('ID').T.to_dict()
        assert len(self._counties) == self._constituencies
        for county in self._counties:
            vm = VektingsmodellStandard(self._pollDatabase, self._dato, method = "Standard", omraade = self._counties[county]['Name'])
            self._counties[county]['Poll'] = vm.run()
            del vm

    # -----------------------
    # Running the simulation
    # -----------------------
    
    def run(self):

        # Iterations, (direct, utjevning, total), counties, parties
        self._resultMatrix = np.zeros((self._iterations, 3, len(self._geoShares[0]), self._parties))

        # Vote shares
        self._resultsVoteShareNational = np.zeros((self._iterations,self._parties))

        # Sperregrense
        self._sperregrenseMatrix = np.zeros((self._iterations, self._parties))

        for iter in tqdm(range(self._iterations)):

            # Calclate vote shares
            self.calcVotes(self._geoShareList[randrange(len(self._geoShareList))])
            # New system with poll numbers
            vs = ValgSystemNorge(self._sharePartyConstituency, self._seats, self._divisor, self._sperregrense)
            # Calculate direktemandater
            vs.calcDistriktsmandater()
            # Calculate utjevningsmandater
            vs.calcUtjevningsmandater()

            # Distriktsmandater
            self._resultMatrix[iter][0] = vs.getDistriktsmandater()
            # utjevningsmandater
            self._resultMatrix[iter][1] = vs.getUtjevningsmandater()
            # Sum mandater
            self._resultMatrix[iter][2] = self._resultMatrix[iter][0] + self._resultMatrix[iter][1]

            self._sperregrenseMatrix[iter] = vs.getOverSperrengrense()

            if self._regional:
                self._resultsVoteShareNational[iter] = np.sum(self._sharePartyConstituency, axis=0)
            else:
                self._resultsVoteShareNational[iter] = deepcopy(self._voteSharesNational)

        return self._resultMatrix, self._sperregrenseMatrix

    def calcVotes(self, geoShare = 0):

        #  ------------------------------------------------  
        #  NATIONAL SURVEYS
        #  ------------------------------------------------

        # Votes nationally allocated to each party
        self._voteSharesNational = np.zeros((self._parties))

        # distribution of votes
        geoshareMatrix = self._geoShares[geoShare]

        #  Total poll variance
        var = [x ** 2 for x in  self._pollData[1][0]] 

        #  National weight
        w_national = sum(19 * var) ** .5

        # Just poll values
        if self._iterations == 1:
            for party in range(self._parties):
                self._voteSharesNational[party] = self._pollData[0][party]

                

        # Simulated values
        else:
            # Random draws
            for party in range(self._parties):

                # Polling error
                self._voteSharesNational[party] = norm.ppf(random(), self._pollData[0][party], self._pollData[1][0][party])

                # General uncertainty
                self._voteSharesNational[party] += self._uncertainty[party][1] + random() * (self._uncertainty[party][0] - self._uncertainty[party][1])

            # Normalize
            for party in range(self._parties):
                self._voteSharesNational[party] = self._voteSharesNational[party] / self._voteSharesNational.sum() * (1-self._pollData[0][self._otherPartyIndex])

        #  ------------------------------------------------  
        #  REGIONAL SURVEYS
        #  ------------------------------------------------
        
        self._voteSharesRegional = np.zeros((self._parties, self._constituencies))

        w_regional = {}

        if self._regional:
            for constituency, data in self._counties.items():
                
                #  Correct for different base (stupid)
                constituency -= 1

                pollingdata = data['Poll']
                
                #  There is a valid local poll
                if pollingdata != None:
                
                    var = [x ** 2 for x in pollingdata[1][0]]
 
                    w_regional[constituency] = sum(var) ** .5
                    
                    # Just poll values
                    if self._iterations == 1:
                        for party in range(self._parties):
                            self._voteSharesRegional[party][constituency] = pollingdata[0][party]
                            

                    # Simulated values
                    else:
                        
                        #  Sum of shares in the constituency (for normalization)
                        sumInConstituency = 0

                        # Random draws
                        for party in range(self._parties):

                            # Polling error (1-e9 to remove zero sum if SD is large due to no surveys)
                            self._voteSharesRegional[party][constituency] = max(1e-9,norm.ppf(random(), pollingdata[0][party], pollingdata[1][0][party]))
                            
                            #  Total votes
                            sumInConstituency += self._voteSharesRegional[party][constituency]

                        # Normalize
                        for party in range(self._parties):
                            self._voteSharesRegional[party][constituency] = self._voteSharesRegional[party][constituency] / min(10,sumInConstituency) * (1 - pollingdata[0][self._otherPartyIndex])
                        

                #  There is no valid local poll, does not enter
                else:
                    w_regional[constituency] = 10000
        
        #  ------------------------------------------------  
        #  TOTAL AVERAGE
        #  ------------------------------------------------

        #  Vote shares per constituency, per party - must be a more efficient way to do this ...

        '''
        This block calculates the average of national and regional surveys.
        First, the regional and national values are calculated, normalized and adjusted for "other parties" in the previous block.
        Then, depending on the mode (regional or national mode), the shares within each constituency is calculated, normalized 
        and adjusted for other parties
        '''

        #  Sum of national votes, broken down in each constituency
        self._constituency = np.zeros((self._constituencies))
        self._sharePartyConstituency = np.zeros((self._constituencies, self._parties))
        for party in range(self._parties):
            for constituency in range(self._constituencies):

                #If not regional mode, then only the national shares are used
                if self._regional:
                    self._constituency[constituency] += geoshareMatrix[constituency][party] * self._voteSharesNational[party]
                else: 
                    self._sharePartyConstituency[constituency][party] = geoshareMatrix[constituency][party] * self._voteSharesNational[party]

        if self._regional:
        
            #  Normalizing and calculating proper shares - within each constituency
            for constituency in range(self._constituencies):
                for party in range(self._parties):
                    self._sharePartyConstituency[constituency][party] = geoshareMatrix[constituency][party] * self._voteSharesNational[party] / self._constituency[constituency]

            #  Calculating the total average
            self._sharePartyConstituency_total = np.zeros((self._constituencies, self._parties))
            self._constituency = np.zeros((self._constituencies))
            for party in range(self._parties):
                for constituency in range(self._constituencies):
                    
                    #  Share based on regional surveys
                    regional = self._voteSharesRegional[party][constituency]

                    #  Share based on national surveys
                    national = self._sharePartyConstituency[constituency][party]

                    #  Total average
                    self._sharePartyConstituency_total[constituency][party] = 1.0 /  (1.0 / w_national + 1.0 / w_regional[constituency]) * (national / w_national + regional / w_regional[constituency])
                    
                    # Sum in constituency
                    self._constituency[constituency] += self._sharePartyConstituency_total[constituency][party]

                    

                    
            # Normalizing once more
            # Taking the constituency total and adjusting for share of national votes
            # Remvoing the share of other parties (using the national average for now)
            for party in range(self._parties):
                for constituency in range(self._constituencies):
                
                    self._sharePartyConstituency_total[constituency][party] /= self._constituency[constituency] 
                    self._sharePartyConstituency_total[constituency][party] *= geoshareMatrix[constituency][-1] * (1 - self._pollData[0][self._otherPartyIndex])
                    
                    
            self._sharePartyConstituency = self._sharePartyConstituency_total


    def returnResults(self):
        return self._resultMatrix

    def returnPolls(self):
        return self._resultsVoteShareNational

if __name__ == "__main__":


    geoShareFile = [{'file': "data/fylkesfordeling2013.csv", 'prop': 0.1},
                {'file': "data/fylkesfordeling2017.csv", 'prop': 0.3},
                {'file': "data/fylkesfordeling2021.csv", 'prop': 0.6}]

    #geoShareFile = ["data/fylkesfordeling2013.csv","data/fylkesfordeling2017.csv","data/fylkesfordeling2021.csv"]
    seatsFile = "data/mandater24.csv"
    pollDatabase = "../dataGet/db/Valg_db.db"
    uncertaintyFile = "data/usikkerhet.csv"
    constituency_file = "data/countylist.csv"
    dato = datetime.datetime.now()

    


    v = Valgsimulering(geoShareFile, seatsFile, pollDatabase, uncertaintyFile, dato, constituency_file, 10)
    v.run()



    # print(v.returnResults())
    #print(v.returnResults())
    #print(np.mean(v._sperregrenseMatrix, axis=0))
    #print(v._sperregrenseMatrix.shape)
    #print(v._sperregrenseMatrix)

