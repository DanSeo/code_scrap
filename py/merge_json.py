#-*- coding: utf-8 -*-
import json
import os
import codecs
import sys

arguments = sys.argv

parentName = arguments[1]
childName = arguments[2]
saveFileName = arguments[3]


def parseJson (fileName):
	with codecs.open(fileName, 'r', encoding='utf-8') as f:
		return json.load(f)

files = [f for f in os.listdir(".") if os.path.isfile(f) and not f.endswith(".py")]

jsons = [parseJson(data) for data in files]
result = {parentName:[]}

for current in jsons:
	result[parentName].extend(current[childName])

with codecs.open(saveFileName, "w", encoding='utf-8') as f:
	data = json.dump(result, f, ensure_ascii=False)
