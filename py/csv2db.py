# -*- coding: utf-8 -*-
__author__ = 'danielseo'

import csv
import codecs
import sys
import sqlite3

if len(sys.argv) != 4:
    sys.exit(1)

fileName = sys.argv[1]
tableName = sys.argv[2]
dbFileName = sys.argv[3]

print fileName + " " + tableName
TABLE_DDL = "CREATE TABLE IF NOT EXISTS " + tableName
INSERT_QUERY = "INSERT INTO " + tableName

def makeInsertQuery(headers, dataList):
    result = INSERT_QUERY + " ( "

    for i in range(len(headers)):
        if i != 0:
            result += ", "
        result += headers[i].replace(" ", "_")

    result += " ) VALUES ( "

    for i in range(len(dataList)):
        if i != 0:
            result += ", "
	
        result += "'" + dataList[i].replace("'", "''") +  "'"
    result += " ) ;"

    return result


con = sqlite3.connect(dbFileName)
try:

    headerNameList = []
    createTableQuery = TABLE_DDL + " ("

    with codecs.open(fileName, 'r') as f:
        csvReader = csv.reader(f)
	headers = csvReader.next()
        for i in range(len(headers)):
            header = headers[i].replace(" ", "_")
            headerNameList.append(header)
            if i != 0:
                createTableQuery += ", "
            createTableQuery += header + " VARCHAR(512) "

        createTableQuery += " );"

        cursor = con.cursor()
        cursor.execute(createTableQuery)
        con.commit()

        print createTableQuery

        for row in csvReader:
            currentInsertSql = makeInsertQuery(headers, row)
            print currentInsertSql
            cursor.execute(currentInsertSql)
        con.commit()

finally:
    con.close()
    pass
