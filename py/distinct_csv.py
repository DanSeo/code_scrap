#-*- encoding:utf-8 -*-
import csv
import codecs
import sys

# csv파일을 distinct 연산하는 파일

arguments = sys.argv

fileName = arguments[1]
saveFile = arguments[2]



result = []
with codecs.open(fileName, "r", encoding='utf-8') as csvFile:
	reader = csv.reader (csvFile, delimiter=',', quotechar='"')
	unique = dict()
	for row in reader:
		unique[row[0]+"," + row[1] + "," + row[2]] = row
	for key in unique:
		result.append(unique[key])

with codecs.open(saveFile, 'wb', encoding='utf-8') as output :
	csvwriter = csv.writer(output, delimiter=',', quotechar='"')

	for data in result:
		csvwriter.writerow(data)
