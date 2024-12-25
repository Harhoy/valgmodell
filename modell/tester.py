
import os
import shutil
import sqlite3

from valgsimulering import Valgsimulering
from datetime import date, timedelta, datetime
from resultHandler import ResultHandler

#https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
def daterange(start_date, end_date):
    days = int((end_date - start_date).days)
    for n in range(days):
        yield start_date + timedelta(n)

#List of matrices with distribution of votes per party over counties
geoShareFile = ["data/fylkesfordeling2013.csv"]
#Seats per county
seatsFile = "data/mandater24.csv"
#Database with polls
pollDatabase = "data/poll/db/Valg_db.db"
#Empty file, for now
uncertaintyFile = ""
#Database to store results
mainBase = "data/databaser/mainDB.db"
resultsDatabase = "data/databaser/mainDB_TEST.db"
dato = datetime.now()

#delete data
conn = sqlite3.connect(resultsDatabase)
cur = conn.cursor()
cur.execute("DELETE FROM Simulering;")
conn.commit()
cur.execute("DELETE FROM Resultater_parti;")
conn.commit()

#Date to start time series generation
start_date = date(2024, 10, 1)
#Date to end time series generation
end_date = date(2024, 12, 18)

for dato in daterange(start_date, end_date):

    dato = datetime.combine(dato, datetime.min.time())

    print("Kjorer modell for", dato)
    simuleringsmodell = Valgsimulering(geoShareFile, seatsFile, pollDatabase, uncertaintyFile, dato, 100)
    resultshandler = ResultHandler(resultsDatabase, simuleringsmodell.run(), dato)
    resultshandler.run()
