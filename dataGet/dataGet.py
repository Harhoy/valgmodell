# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import sqlite3
import random

def getMaaling(id):
    res = requests.get("https://www.pollofpolls.no/?cmd=Maling&gallupid=" + str(id))
    rescode = res.status_code
    html = res.text
    parsed_html = BeautifulSoup(html,'html.parser')
    data = {}

    try:
        for a in parsed_html.find_all('a', href =True):
            cand = a['href'].split("=")
            #print(cand)

            #oppslutning
            if len(cand) > 1:
                if cand[1] == 'Mandatfordeling&do':
                    data = {}
                    line = a['href'].split("&")
                    for i in range(2,len(line) - 1):
                        parti = line[i].split("=")[0]
                        andel = float(line[i].split("=")[1])
                        data[parti] = andel

        a = parsed_html.find_all("td", string="Valg")[0]
        valgtype = a.find_next_sibling("td").string

        a = parsed_html.find_all("td", string="Område")[0]
        omraade = a.find_next_sibling("td").string

        a = parsed_html.find_all("td", string="Institutt")[0]
        institutt = a.find_next_sibling("td").string

        a = parsed_html.find_all("td", string="Antall spurte")[0]
        utvalgsstorrelse = a.find_next_sibling("td").string

        a = parsed_html.find_all("td", string="Tatt opp")[0]
        dato = a.find_next_sibling("td").string

        return {'status': "ok", 'data': data, 'valgtype': valgtype, 'omraade': omraade, 'institutt':institutt, 'antall spurte': utvalgsstorrelse,'dato': dato, 'id': id}
    except:
        return {'status': "fail"}

def insertMaaling(maaling,  conn):

    cursor = conn.cursor()

    existCheck = "SELECT COUNT(1) from malinger where ID_POP = " + str(maaling['id'])
    res = cursor.execute(existCheck)
    count = res.fetchone()[0]

    if count == 0:

        sql = "insert into malinger (ID_POP, AP, H, Frp, SV, Sp, KrF, V, MDG, R, A, Valgtype, Omraade, Institutt, Utvalgsstorrelse, Dato) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        data = (maaling['id'],
                maaling['data']['Ap'],
                maaling['data']['H'],
                maaling['data']['Frp'],
                maaling['data']['SV'],
                maaling['data']['Sp'],
                maaling['data']['KrF'],
                maaling['data']['V'],
                maaling['data']['MDG'],
                maaling['data']['R'],
                maaling['data']['A'],
                maaling['valgtype'],
                maaling['omraade'],
                maaling['institutt'],
                maaling['antall spurte'],
                maaling['dato'])

        cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        return "committed"
    else:
        return "existing record"
        cursor.close()


if __name__ == "__main__":

    conn = sqlite3.connect("db/Valg_db.db")
    cursor = conn.cursor()
    findMax = "select max(ID_POP) from Malinger;"
    maxVal = cursor.execute(findMax).fetchone()[0]

    tries = 0
    maxTries = 20
    lastStatus = "ok"
    lastVal = maxVal + 1
    hentet = 0

    '''
    m = getMaaling(5363)
    print(insertMaaling(m, conn))
    print(m['status'])
    '''
    print("henter")
    while tries < maxTries and lastStatus != "fail":
        resp = getMaaling(lastVal)

        if resp['status'] == "ok":
            insertMaaling(resp, conn)
            tries += 1
            lastVal += 1
            hentet += 1
            time.sleep(30)
        else:
            lastStatus = "fail"
            tries = float("inf")

    print("hentet",hentet,"maalinger")
