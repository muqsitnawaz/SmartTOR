from math import radians, cos, sin, asin, sqrt
# Donot forgot to import
def totalDistance(path):
    distance = 0
    for x in xrange(1, len(path)):
        distance += haversine(path[x][0], path[x][1], path[x-1][0], path[x-1][1])
    return distance

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

