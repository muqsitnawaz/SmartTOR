from scipy.spatial import cKDTree
from scipy import inf
from geoip import geolite2
import sys

#takes a dictionary named relays where (key, val) is (coordinates, fingerprint) of relays
class ProximitySearch(object):
    def __init__(self, relays):
        self.points = relays.keys()
        self.crime_kdtree = cKDTree(self.points)

    def get_points_nearby(self, point, max_points):
        """
        Find the nearest points to the tuple 'point', to a maximum of max_points
        """
        distances, indices = self.crime_kdtree.query(point, k=max_points,
                                                     distance_upper_bound=sys.maxint)
        point_neighbors = []
        for index, max_points in zip(indices, distances):
            if max_points == inf:
                break
            point_neighbors.append(self.points[index])
        return point_neighbors


# # Format (key, val) is (coordinates, fingerprint) of the relay


# Islamabad = (33.729388, 73.093146)

# proximity = ProximitySearch(dictionary)
# locations = proximity.get_points_nearby(Islamabad, 3)
# #Getting three closest relays to Islamabad results in Lahore, Mumbai, Dubai (Note the order)
# print [dictionary[x] for x in locations]
# print type(dictionary)
