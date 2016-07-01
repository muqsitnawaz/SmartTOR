import pickle



file = open("scan_head_exp.txt", "r")
newarray = pickle.load(file)

for i in newarray:
	print i
	print "\n"
