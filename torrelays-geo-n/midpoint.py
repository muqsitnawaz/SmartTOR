import math
def midpointCalculator(p1,p2):	
	lat1, lon1 = p1
	lat2, lon2 = p2
	assert -90 <= lat1 <= 90
	assert -90 <= lat2 <= 90
	assert -180 <= lon1 <= 180
	assert -180 <= lon2 <= 180
	lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
	dlon = lon2 - lon1
	dx = math.cos(lat2) * math.cos(dlon)
	dy = math.cos(lat2) * math.sin(dlon)
	lat3 = math.atan2(math.sin(lat1) + math.sin(lat2), math.sqrt((math.cos(lat1) + dx) * (math.cos(lat1) + dx) + dy * dy))
	lon3 = lon1 + math.atan2(dy, math.cos(lat1) + dx)
	lon3d = math.degrees(lon3)
	if lon3d < -180:
	    # print "oops1", lon3d
	    lon3d += 360
	elif lon3d > 180:
	    # print "oops2", lon3d
	    lon3d -= 360
	return(math.degrees(lat3), lon3d)

