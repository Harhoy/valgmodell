import numpy as np

def fordeling(mandater, shares, divisorVal):
    #Array med antall mandater til hvert parti
    returnVal = [0] * len(shares)
    while mandater > 0:
        maxParty = -1
        maxVal = 0
        for i in range(len(shares)):
            if returnVal[i] == 0:
                divisor = divisorVal
            else:
                divisor = 2 * returnVal[i] + 1
            if shares[i] / divisor > maxVal:
                maxVal = shares[i] / divisor
                maxParty = i
        returnVal[maxParty] += 1
        mandater -= 1
    return np.array(returnVal)
