from proximity import ProximitySearch
import random
import os
from history import*
from scan import*
import sys
from relays import get_relays
from geoip import geolite2
import stem.control
import ipgetter
from midpoint import haversine
import shutil
from UserURLHistory import getFetechableURLsFromPage
from test2 import totalDistance
with stem.control.Controller.from_port() as controller:
    pass

# Get the ccomplete page including all src urls embedded in the page

num_relays = 10
# ====================================================================================
# Get every content of a page and savee in a folder with name of 
# website (eg. yahoo, facebook). If folder already exists it'll be deleted
# ====================================================================================
def get_page(url, controller, circuit, results, distance):
    hostname = url.split(".")[1]
    path = os.path.join(os.getcwd(), hostname)
    if (os.path.exists(path)):
        shutil.rmtree(path)
    os.mkdir(path)
    os.chdir(path)
    fd = open(hostname + ".html", "w")
    fd_read = open(hostname + ".html", "r")
    time_taken = scan(controller, circuit, url, fd)
    fetchable = getFetechableURLsFromPage(fd_read.read())
    fetchable = list(set(fetchable))
    urls = map(convert_src_to_url, fetchable)
    time = query_parallel(urls) + time_taken
    return time

# convert from for "src="xyz"" to xyz
def convert_src_to_url(str):
    return str[5:len(str)-1]
# ====================================================================================
# This function tests n random circuits from the results of proximity search
#  and returns the best circuit as measured by taking average of getting the head
# ====================================================================================
def get_best_circuit(url, controller, entry, middle, exit, n):
    best_path = None
    best_time = 1000000
    count = 0
    for x in range(0, n):
        if (count == 2):
            break
        entry_relay = entry[random.randint(0, len(entry) -1)]
        exit_relay = exit[random.randint(0, len(exit) -1)]
        middle_relay = middle[random.randint(0, len(middle) -1)]
        path = [entry_relay[0], middle_relay[0], exit_relay[0]]
        path_with_locations = [entry_relay, middle_relay, exit_relay]
        # print path
        try:
            circuit_id = controller.new_circuit(path, await_build = True)
            circuit = controller.get_circuit(circuit_id)
            print "Accessing Head"
            time = scan_head(controller, circuit, url)
            if (time == -1):
                return -1
                continue
            if (time < best_time):
                best_path = path_with_locations
                count = count + 1
            controller.close_circuit(circuit_id)
        except stem.CircuitExtensionFailed as error:
            # print "Circuit failed, trying next"
            continue
    return best_path


def readinFile():
    with open("ListOfDomains2.csv") as f:
        stocks = f.read().splitlines()
        return stocks


def main():
    # history = get_top_visited(get_history(), 10)
    # history = ["ask.com", "tumblr.com"]
    controller.authenticate()
    # experiment_smartor(history)
    history = ["yahoo.com"]
    time_1 = experiment_smartor(history)
    time_2 = experiment_tor(history)

    print "Smartor: " + str(time_1)
    print "Tor: " + str(time_2)

# =====================================================================================
# Run the experiment using our algorithm.
# =====================================================================================
def experiment_smartor(history):
    results_smartor = open("results_smartor.txt", "a")
    relays = get_relays(controller)
    entry = relays[0];
    middle = relays[1];
    exit = relays[2];
    myIP = ipgetter.myip();
    my_Address =  geolite2.lookup(socket.gethostbyname(myIP))
    for url in history:
        dest_Address =  geolite2.lookup(socket.gethostbyname(url))
        if (dest_Address == None):
            print("Couldn't get location of ", url)
            continue
        #  Get list of fingerprints for exit nodes
        exit_nodes = get_relays_fingerprint(num_relays, exit, dest_Address.location)
        entry_nodes = get_relays_fingerprint(num_relays, entry, my_Address.location)
        middleLocation = midpointCalculator(dest_Address.location, my_Address.location)
        middle_nodes = get_relays_fingerprint(num_relays, middle, my_Address.location)
        url = 'https://www.' + url
        path_with_locations = get_best_circuit(url, controller, entry_nodes, middle_nodes, exit_nodes, 10)
        if path_with_locations == -1:
            continue
        locations = [my_Address.location] + [x[1] for x in path_with_locations] + [dest_Address.location]
        distance = totalDistance(locations)
        best_path = [x[0] for x in path_with_locations]
        print("best path ", best_path)
        circuit_id = controller.new_circuit(best_path, await_build = True)
        test = controller.get_circuit(circuit_id)
        print 'Accessing url: ' + url
        get_page(url, controller, test, results_smartor, distance)


# =====================================================================================
# Run the experiment using tor
# =====================================================================================

def experiment_tor(history):
    results_tor = open("results_tor.txt", "a")
    myIP = ipgetter.myip();
    my_Address =  geolite2.lookup(socket.gethostbyname(myIP))

    for url in history:
        dest_Address =  geolite2.lookup(socket.gethostbyname(url))
        if (dest_Address == None):
            print("Couldn't get location of ", url)
            continue
        url = 'https://www.' + url
        test = controller.get_circuits()
        for circuit in test:
            if (len(circuit.path) > 2):
                path = circuit.path
                circ = circuit
                break
                print path
                # test = path
        res_list = [controller.get_network_status(x[0]).address for x in path] # Get ip addresses from fingerprints
        # print res_list
        locations_relay = [geolite2.lookup(x).location for x in res_list] # Do lookups
        # print locations_relay
        locations =  [my_Address.location] + locations_relay + [dest_Address.location]
        distance = totalDistance(locations)
        time = get_page(url, controller, circ, results_tor, distance)
        if (time != -1):
            results_tor.write(str(distance) + "," + str(time) + "\n")


# =====================================================================================
# Given a dictionary of relays and a location, get n closest
# relays(fingerprints) in a list
# =====================================================================================

def get_relays_fingerprint(n, relays, location):
    retval = []
    proximityClass = ProximitySearch(relays)
    nRelaysLocation = proximityClass.get_points_nearby(location, n)
    for i in nRelaysLocation:
        retval.append((relays[i], i))
    return retval

if __name__ == "__main__":
    main()
