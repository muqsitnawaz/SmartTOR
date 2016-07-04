import pickle

file = open("PacketHeaders_C.txt", "r")
file_Result = open("ParsedHeaders_Results.txt", "w")
newarray = pickle.load(file)

for i in newarray:
	for j in xrange(0,4):
		try:
			file_Result.write(i[0][0] + " " + i[1][0] + " " + i[2][0] + " " + i[3 + j][0] + " " + str(i[3 + j][1]) + "\n")
		except:
			continue
