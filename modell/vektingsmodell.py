

import sqlite3
from sqlalchemy import text
from copy import deepcopy


'''
    conn = sqlite3.connect("db/Valg_db.db")
    cursor = conn.cursor()
    findMax = "select max(ID_POP) from Malinger;"
    maxVal = cursor.execute(findMax).fetchone()[0]
    =HVIS(C6<=vektB;HVIS(C6<=vektA;1;1-(C6-vektA)/(vektB-vektA));0)

'''


class Vektingsmodell:

    def __init__(self, database, dateA, dateB):

        #Database with downloaded data on polls
        self._database = database
        #Connection
        self._conn = sqlite3.connect(self._database)
        #Cursor
        self._cursor = self._conn.cursor()

        #Extract raw data from database
    def getData(self, omraade):

        query = "SELECT AP, H, Frp, SV, Sp, KrF, V, MDG, R, A, Utvalgsstorrelse, Dato FROM Malinger WHERE Omraade == " +  "'" + omraade +  "'"

        results = []
        for row in self._conn.execute(query):
            temp = {}
            temp['AP'] = row[0]
            temp['H'] = row[1]
            temp['Frp'] = row[2]
            temp['SV'] = row[3]
            temp['Sp'] = row[4]
            temp['KrF'] = row[5]
            temp['V'] = row[6]
            temp['MDG'] = row[7]
            temp['R'] = row[8]
            temp['A'] = row[9]
            temp['N'] = row[10]
            temp['Dato'] = row[11]
            results.append(deepcopy(temp))

        return results


if __name__ == "__main__":

    vm = Vektingsmodell("data/poll/db/Valg_db.db")
    vm.getData("Hele landet")
