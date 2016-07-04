import re

Result = open("Website_Results.txt", "w")

Results = []
Summary = []

with open("Results.txt", "r") as f:
    for line in f:
        try:
            Results.append([re.match(r'[^ ]*', line[15:], flags=0).group(),
            int(re.search(r'[0-9]+', line, flags=0).group()),
            float(re.findall(r'[0-9.]+', line)[-2])])
        except Exception as E:
            print E
            continue


prevWebsite = Results[0][0]
prevTotal = Results[0][1]
prevDistance = Results[0][2]
numEntries = 1

# for i in Results:
#   print i

# print "\n\n"

for i in xrange(1, len(Results)):
    if (prevWebsite == Results[i][0] and prevDistance == Results[i][2]):
        prevTotal = prevTotal + Results[i][1]
        numEntries = numEntries + 1
    elif (prevWebsite != Results[i][0] and prevDistance != Results[i][2]):
        Summary.append([prevWebsite, prevTotal / numEntries, prevDistance])

        prevWebsite = Results[i][0]
        prevTotal = Results[i][1]
        prevDistance = Results[i][2]
        numEntries = 1

    if (i == len(Results) - 1):
        Summary.append([prevWebsite, prevTotal / numEntries, prevDistance])

for i in Summary:
    Result.write((str(i[0]) + " " + str(i[1]) + " " + str(i[2]) + "\n"))