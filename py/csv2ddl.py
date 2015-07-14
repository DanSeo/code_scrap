# -*- coding: utf-8 -*-
__author__ = 'danielseo'

import csv
import codecs
import sys
import sqlite3
fileName = sys.argv[1]
tableName = sys.argv[2]

print fileName + " " + tableName
TABLE_DDL = "CREATE TABLE IF NOT EXISTS " + tableName

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
	# create table.
	print createTableQuery
finally:
    pass
