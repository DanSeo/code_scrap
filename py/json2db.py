# -*- coding: utf-8 -*-
__author__ = 'danielseo'

import json
import os
import sys
import datetime
import subprocess
import time
import sqlite3
from urlparse import urlparse
import codecs


# DB 파일을 json 파일로 전환해서 저장한다
arguments = sys.argv

parentName = arguments[1]
dbFileName = arguments[2]
saveFileName = arguments[3]
sql = arguments[4]

con = sqlite3.connect(dbFileName)
cursor = con.cursor()
cursor.execute(sql)
alldata = cursor.fetchall()
try:
    resultData = { parentName : [] }
    for i in range(len(alldata)):
        current = alldata[i]

        fileName = current[1]
 	if not os.path.exists(fileName):
            print fileName
            continue
        with codecs.open(fileName,'r',encoding='utf-8') as rtFile:
	#with open(fileName, 'r') as rtFile:
            data = json.load(rtFile)
            data = data[parentName]
            for i in range(len(data)):
                resultData[parentName].append(data[i])

    with codecs.open(saveFileName, "w",encoding='utf-8') as output:
        json.dump(resultData, output, ensure_ascii=False, encoding='utf-8')


finally:
    con.close()
