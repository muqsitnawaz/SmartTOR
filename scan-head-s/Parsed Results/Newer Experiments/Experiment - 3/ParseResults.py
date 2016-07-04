from __future__ import division
import re

Result = open("Website_Parsed_Results.txt", "w")

Results = []
Summary = []

with open("Results.txt", "r") as f:
    for line in f:
        try:
            Results.append([[x for x in (re.findall(r'[A-Z0-9]+', line[15:])) if len(x) == 40],
            re.match(r'[^ ]*', line[15:], flags=0).group(),
            int(re.findall(r'[0-9]+', line)[-6]),
            float(re.findall(r'[0-9.]+', line)[-4]),
            int(re.findall(r'[0-9]+', line)[-3])])
        except Exception as E:
            print E
            continue


prevWebsite = Results[0][1]
curTotal = Results[0][2]
prevDistance = Results[0][3]
curSize = Results[0][4]
overallTotal = (curTotal / curSize)
numEntries = 1
prevFps = Results[0][0]

for i in xrange(1, len(Results)):
    if (prevDistance == Results[i][3]):
        curTotal = Results[i][2]
        curSize = Results[i][4]

        overallTotal = overallTotal + (curTotal / curSize)

        numEntries = numEntries + 1

        # print overallTotal
    elif (prevDistance != Results[i][3]):
        Summary.append([prevFps, prevWebsite, overallTotal / numEntries, prevDistance])

        prevFps = Results[i][0]
        curTotal = Results[i][2]
        prevDistance = Results[i][3]
        curSize = Results[i][4]
        overallTotal = (curTotal / curSize)
        numEntries = 1

    if (i == len(Results) - 1):
        Summary.append([prevFps, prevWebsite, overallTotal / numEntries, prevDistance])

# for i in Summary:
# 	print i
	# print "\n"

for i in Summary:
    Result.write((str(i[0][0]) + " " + str(i[0][1]) + " " + str(i[0][2]) + " " + str(i[1]) + " " + str(i[2]) + " " + str(i[3]) + "\n"))
