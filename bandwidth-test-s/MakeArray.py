ARRAY = []

for i in xrange(0,40000,5000):
	ARRAY.append((i, i + 5000))

ARRAY.reverse()
print ARRAY