
import os
import shutil
import sqlite3
import numpy as np

from valgsimulering import Valgsimulering
from datetime import date, timedelta, datetime
from resultHandler import ResultHandler

#https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
def daterange(start_date, end_date):
    days = int((end_date - start_date).days)
    for n in range(1, days, 7):
        yield start_date + timedelta(n)

#List of matrices with distribution of votes per party over counties and proportions used
geoShareFile = [{'file': "data/fylkesfordeling2013.csv", 'prop': 0.05},
                {'file': "data/fylkesfordeling2017.csv", 'prop': 0.3},
                {'file': "data/fylkesfordeling2021.csv", 'prop': 0.65}]

#Seats per county
seatsFile = "data/mandater21.csv"
#Database with polls
pollDatabase = "../dataGet/db/Valg_db.db"
#Empty file, for now
uncertaintyFile = "data/usikkerhet.csv"
#Database to store results
mainBase = "data/databaser/mainDB.db"
#File with data on each constituency to find data from survey database
constituency_file = "data/countylist.csv"

resultsDatabase = "data/databaser/mainDB_TEST.db"
dato = datetime.now()

#delete data
conn = sqlite3.connect(resultsDatabase)
cur = conn.cursor()
cur.execute("DELETE FROM Simulering;")
conn.commit()
cur.execute("DELETE FROM Resultater_parti;")
conn.commit()
cur.execute("DELETE FROM Resultater_kandidat;")
conn.commit()
cur.execute("DELETE FROM Resultater_parti_national;")
conn.commit()
cur.execute("DELETE FROM Info;")
conn.commit()
cur.execute("DELETE FROM Resultater_koalisjon_nasjonal;")
conn.commit()
cur.execute("DELETE FROM Sperregrense;")
conn.commit()
cur.execute("DELETE FROM Info;")
conn.commit()
cur.execute("DELETE FROM Maalinger;")
conn.commit()

#Date to start time series generation
start_date = date(2025, 7, 10)
#Date to end time series generation
end_date = date(2025, 7, 20)
#Adding info
current_date = datetime.today().strftime('%Y-%m-%d')
cur.execute("INSERT INTO Info (Date) VALUES (" "'" + str(current_date) +  "'" ");")
conn.commit()


for dato in daterange(start_date, end_date):

    dato = datetime.combine(dato, datetime.min.time())

    print("Kjorer modell for", dato)
    # Setter opp simuleringsmodell for angitt dato
    simuleringsmodell = Valgsimulering(geoShareFile, seatsFile, pollDatabase, uncertaintyFile, dato, constituency_file, 1000)
    simuleringsmodell._regional = False
    # Setter opp resulthandler som tar imot data fra simuleringsmodellen
    resultshandler = ResultHandler(resultsDatabase, simuleringsmodell.run(), dato)
    # Legger til data fra vektede polls
    resultshandler.addPolls(simuleringsmodell.returnPolls())
    # Kjorer ut resultater til DB
    resultshandler.run()

    print(np.mean(simuleringsmodell.returnPolls(), axis=0))


# -------------------------------------------------
# Kjorer modellen for ren polling uten simulering
# -------------------------------------------------

# < ---- NASJONALE OG REGIONALE MAALINGER ---- > 

# Setter opp simuleringsmodell for angitt dato
simuleringsmodell = Valgsimulering(geoShareFile, seatsFile, pollDatabase, uncertaintyFile, dato, constituency_file, 1)
# Setter opp resulthandler som tar imot data fra simuleringsmodellen
resultshandler = ResultHandler(resultsDatabase, simuleringsmodell.run(), end_date)
# Legger til data fra vektede polls
resultshandler.addPolls(simuleringsmodell.returnPolls())
# Kjorer ut resultater til DB
resultshandler.run(-1)

 
# < ---- NASJONALE  MAALINGER ---- >

# Setter opp simuleringsmodell for angitt dato
simuleringsmodell = Valgsimulering(geoShareFile, seatsFile, pollDatabase, uncertaintyFile, dato, constituency_file, 1)
simuleringsmodell._regional = False
# Setter opp resulthandler som tar imot data fra simuleringsmodellen
resultshandler = ResultHandler(resultsDatabase, simuleringsmodell.run(), end_date)
# Legger til data fra vektede polls
resultshandler.addPolls(simuleringsmodell.returnPolls())
# Kjorer ut resultater til DB
resultshandler.run(-2)
print(simuleringsmodell.returnPolls())

print(np.sum(simuleringsmodell.returnResults()[0][2], axis=0))

