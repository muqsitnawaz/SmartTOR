import re
import numpy as np
import operator

Results = []
Summary = []

File = open("Parsed_Results", "w")

def ParseTime(time):
    MIN = (re.findall(r'[0-9.]+m', time[1:], flags=0))
    SEC = (re.findall(r'[0-9.]+s', time[1:], flags=0))
    TOTAL_TIME = 0

    if len(MIN) is not 0:
        TOTAL_TIME = TOTAL_TIME + int(MIN[0][:-1]) * 60

    if len(SEC) is not 0:
        TOTAL_TIME = TOTAL_TIME + int(SEC[0][:-1])

    return TOTAL_TIME


def ParseResults(record):
    # [MB, TIME, BANDWIDTH, DISTANCE]
    return [record[0], record[1], min(record[3]), record[4]]


with open('TotalResults', 'r') as f:
    for i in f:
        try:
            record = []
            record.append(int(re.findall(r'[0-9]+MB', i, flags=0)[0][:-2]))
            record.append(ParseTime(re.findall(r'=[0-9.ms]+', i, flags=0)[0]))
            record.append([x for x in re.findall(r'[A-Z0-9]+', i) if len(x) == 40])
            record.append([float(x) for x in [x for x in i.split(' ') if x is not ''][-4:][0:3]])
            record.append(float([x for x in i.split(' ') if x is not ''][-4:][-1][:-1]))

            Results.append(record)
        except Exception as E:
            continue

# [MB, TIME, BANDWIDTH, DISTANCE]
Results = [ParseResults(x) for x in Results]

PREV_SIZE = Results[0][0]
TIME = [Results[0][1]]
PREV_BANDWIDTH = Results[0][2]
PREV_DISTANCE = Results[0][3]

for i in xrange(1, len(Results)):
    if (PREV_SIZE == Results[i][0] and PREV_BANDWIDTH == Results[i][2] and PREV_DISTANCE == Results[i][3]):
        TIME.append(Results[i][1])

        print "."
    elif (PREV_SIZE != Results[i][0] or PREV_BANDWIDTH != Results[i][2] or PREV_DISTANCE != Results[i][3]):
        Summary.append([PREV_SIZE, sum(TIME)/float(len(TIME)), np.std(TIME), PREV_BANDWIDTH, PREV_DISTANCE])

        PREV_SIZE = Results[i][0]
        TIME = [Results[i][1]]
        PREV_BANDWIDTH = Results[i][2]
        PREV_DISTANCE = Results[i][3]

        print "P"

    if (i == len(Results) - 1):
        Summary.append([PREV_SIZE, sum(TIME)/float(len(TIME)), np.std(TIME), PREV_BANDWIDTH, PREV_DISTANCE])


# Summary = sorted(Summary, key=operator.itemgetter(0, 3))

# for i in Summary:
#     File.write(str(i[0]) + " " + str(i[1]) + " " + str(i[2]) + " " + str(i[3]) + " " + str(i[4]) + " \n")
# print Summary