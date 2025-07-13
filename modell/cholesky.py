



import numpy as np


class Cholesky:

    def __init__(self, data):

        # Shares
        self._props = data[0]

        # Standard deviation
        self._standardDeviation = data[1][0]

        # Number of observations
        self._N = data[2]    
        
        self._covariance = np.zeros((len(self._props), len(self._props)))

        self.covariance()

    # With the help of chatgpt
    def covariance(self):
        p = np.asarray(self._props)
        cov = (np.diag(p) - np.outer(p, p)) / self._N
        std_dev = np.sqrt(np.diag(cov))
        corr = cov / np.outer(std_dev, std_dev)
        np.fill_diagonal(corr, 1.0)  # fix any numerical issues on diagonal
        self._correlation = corr

    # With the help of chatgpt, some slight tweaking        
    def generate(self):
        L = np.linalg.cholesky(self._correlation)
        Z = np.random.randn(1, len(self._props))
        X = np.dot(Z[0], L.T)
        v = self._standardDeviation * X + np.asarray(self._props)
        return v
        
                

