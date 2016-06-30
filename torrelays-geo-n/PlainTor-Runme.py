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
from midpoint import midpointCalculator
import shutil
from UserURLHistory import getFetechableURLsFromPage
from haversine import totalDistance
import subprocess
with stem.control.Controller.from_port() as controller:
    pass
import operator
import math
import time

# Get the ccomplete page including all src urls embedded in the page
# ====================================================================================
# Get every content of a page and savee in a folder with name of 
# website (eg. yahoo, facebook). If folder already exists it'll be deleted
# ====================================================================================
# def get_page(url, controller, circuit, results, distance):
#     hostname = url.split(".")[1]
#     path = os.path.join(os.getcwd(), hostname)
#     if (os.path.exists(path)):
#         shutil.rmtree(path)
#     os.mkdir(path)
#     os.chdir(path)
#     fd = open(hostname + ".html", "w")
#     fd_read = open(hostname + ".html", "r")
#     time_taken = scan(controller, circuit, url, fd)
#     fetchable = getFetechableURLsFromPage(fd_read.read())
#     fetchable = list(set(fetchable))
#     urls = map(convert_src_to_url, fetchable)
#     time = query_parallel(urls) + time_taken
#     return time

# convert from for "src="xyz"" to xyz
def convert_src_to_url(str):
    return str[5:len(str)-1]
# ====================================================================================
# This function tests n random circuits from the results of proximity search
#  and returns the best circuit as measured by taking average of getting the head
# ====================================================================================
def get_best_circuit(url, controller, entry, middle, exit, ntimes):
    best_path = None
    best_time = float("inf")
    count = 0

    for i in xrange(0,ntimes):
        entry_relay = entry[random.randint(0, len(entry) -1)]
        middle_relay = middle[random.randint(0, len(middle) -1)]
        exit_relay = exit[random.randint(0, len(exit) -1)]

        path = [entry_relay[0][0], middle_relay[0][0], exit_relay[0][0]]
        path_With_Locations = [entry_relay, middle_relay, exit_relay]
        path_With_Locations = [(x[0],y) for (x,y) in path_With_Locations]

        try:
            circuitId = controller.new_circuit(path, await_build = True)
            circuit = controller.get_circuit(circuitId)
            time = scan_head(controller, circuit, url)

            if (time == -1):
                return -1
                continue
            elif (time < best_time):
                best_path = path_With_Locations
                best_time = time
            controller.close_circuit(circuitId)

        except stem.CircuitExtensionFailed as error:
            print "Circuit Failed! Trying Next."
            continue

    if (best_path == None):
        path_With_Locations = [entry[0], middle[0], exit[0]]
        path_With_Locations = [(x[0],y) for (x,y) in path_With_Locations]
        return path_With_Locations

    return best_path


# ====================================================================================
# This function tests n random circuits from the results of proximity search
# and returns the best circuit (BIAS: BANDWIDTH) as measured by taking the average
# of getting the head.
# ====================================================================================
def get_best_circuit_bandwidth(url, controller, entry, middle, exit, ntimes):
    best_path = None
    best_time = float("inf")
    count = 0

    entry.sort(key=lambda (x,y): x[1], reverse=False)
    middle.sort(key=lambda (x,y): x[1], reverse=False)
    exit.sort(key=lambda (x,y): x[1], reverse=False) # Sort

    for i in xrange(0,ntimes):
        entry_relay = entry[int(math.floor(abs(random.random() - random.random()) * (1 + len(entry))))]
        middle_relay = middle[int(math.floor(abs(random.random() - random.random()) * (1 + len(middle))))]
        exit_relay = exit[int(math.floor(abs(random.random() - random.random()) * (1 + len(exit))))]

        path = [entry_relay[0][0], middle_relay[0][0], exit_relay[0][0]]
        path_With_Locations = [entry_relay, middle_relay, exit_relay]
        path_With_Locations = [(x[0],y) for (x,y) in path_With_Locations]

        try:
            circuitId = controller.new_circuit(path, await_build = True)
            circuit = controller.get_circuit(circuitId)
            time = scan_head(controller, circuit, url)

            if (time == -1):
                return -1
                continue
            elif (time < best_time):
                best_path = path_With_Locations
                best_time = time

            controller.close_circuit(circuitId)

        except stem.CircuitExtensionFailed as error:
            print "Circuit Failed! Trying Next."
            continue

    if (best_path == None):
        path_With_Locations = [entry[0], middle[0], exit[0]]
        path_With_Locations = [(x[0],y) for (x,y) in path_With_Locations]
        return path_With_Locations

    print "PATH: " + str(best_path)
    return best_path



def readinFile():
    with open("ListOfDomains2.csv") as f:
        stocks = f.read().splitlines()
        return stocks


def main():
    # date = str(time.localtime().tm_year) + ":" + str(time.localtime().tm_mon) + ":" + str(time.localtime().tm_mday) + ":" + str(time.localtime().tm_hour) + ":" + str(time.localtime().tm_min) + ":" + str(time.localtime().tm_sec)
    # print date
    controller.authenticate()
    websites = ["facebook.com", "google.com", "amazon.com", "wikipedia.org", "qq.com" , "twitter.com", "live.com" ] # Don't Write (https://www.)
    numberRelays = 10

    experiment_tor(websites, 10)
    # experiment_smartor(websites, 1, 10)
    # experiment_smartor_bandwidth(websites, 1, numberRelays * 10)

# =====================================================================================
# Run the experiment using tor
# =====================================================================================

def experiment_tor(websites, ntimes):
    myIP = ipgetter.myip(); # Finds External IP Address.
    my_Address = geolite2.lookup(socket.gethostbyname(myIP)) # Finds Location Data using IP Address.

    for url in websites:
        
        dest_Address =  geolite2.lookup(socket.gethostbyname(url)) # Finds Location Data of Website.

        if (dest_Address == None):
            print("Couldn't get location of ", url)
            continue # Error Checking

        url = 'https://www.' + url
        test = controller.get_circuits()

        for circuit in test:
            if (len(circuit.path) > 2):
                path = circuit.path
                circ = circuit
                print circ.id
                break

        # ip_list = [controller.get_network_status(x[0]).address for x in path] # Get ip addresses from fingerprints
        # locations_relay = [geolite2.lookup(x).location for x in ip_list] # Do lookups
        # locations =  [my_Address.location] + locations_relay + [dest_Address.location]
        # distance = totalDistance(locations) # Check Haversine File.

        # def attach_stream(stream):
        #     if stream.status == 'NEW':
        #         controller.attach_stream(stream.id, circ.id)
        
        # controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

        # try:
        #     controller.set_conf('__LeaveStreamsUnattached', '1')
        #     scan_head(controller, circ, url)
        distance = 0
        for i in xrange(ntimes): # Check From Nofel
            subprocess.call(("sudo bash RunMe.sh " + url + " Result.txt " + str(distance) + " TOR"), shell=True)

        # finally:
            # print "In finally: scan.py"
            # controller.remove_event_listener(attach_stream)
            # controller.reset_conf('__LeaveStreamsUnattached')



# =====================================================================================
# Run the experiment using our algorithm.
# =====================================================================================
def experiment_smartor(websites, ntimes, num_relays):
    relays = get_relays(controller)

    entry = relays[0];
    middle = relays[1];
    exit = relays[2];

    myIP = ipgetter.myip();
    my_Address =  geolite2.lookup(socket.gethostbyname(myIP))

    for url in websites:
        dest_Address =  geolite2.lookup(socket.gethostbyname(url))

        if (dest_Address == None):
            print("Couldn't get location of ", url)
            continue

        #  Get list of fingerprints for exit nodes
        exit_nodes = get_relays_fingerprint(num_relays, exit, dest_Address.location)
        entry_nodes = get_relays_fingerprint(num_relays, entry, my_Address.location)
        middleLocation = midpointCalculator(dest_Address.location, my_Address.location)        
        middle_nodes = get_relays_fingerprint(num_relays, middle, my_Address.location)

        # print "HERE"

        url = 'https://www.' + url
        path_with_locations = get_best_circuit(url, controller, entry_nodes, middle_nodes, exit_nodes, 3)

        if path_with_locations == -1:
            continue

        locations = [my_Address.location] + [x[1] for x in path_with_locations] + [dest_Address.location]
        distance = totalDistance(locations)
        best_path = [x[0] for x in path_with_locations]

        circuit_id = controller.new_circuit(best_path, await_build = True)

        def attach_stream(stream):
            if stream.status == 'NEW':
                controller.attach_stream(stream.id, circuit_id)
                     
        controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)
        
        try:
            controller.set_conf('__LeaveStreamsUnattached', '1')

            for i in xrange(ntimes):
                subprocess.call(("sudo bash RunMe.sh " + url + " Result.txt " + str(distance) + " Nofel"), shell=True)

            controller.close_circuit(circuit_id)

        finally:
            # print "In finally: scan.py"
            controller.remove_event_listener(attach_stream)
            controller.reset_conf('__LeaveStreamsUnattached')

# =====================================================================================
# Run the experiment using another algorithm.
# =====================================================================================
def experiment_smartor_bandwidth(websites, ntimes, num_relays):
    relays = get_relays(controller)

    entry = relays[0];
    middle = relays[1];
    exit = relays[2];

    myIP = ipgetter.myip();
    my_Address =  geolite2.lookup(socket.gethostbyname(myIP))

    for url in websites:
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
        path_with_locations = get_best_circuit_bandwidth(url, controller, entry_nodes, middle_nodes, exit_nodes, 3)

        if path_with_locations == -1:
            continue

        locations = [my_Address.location] + [x[1] for x in path_with_locations] + [dest_Address.location]
        distance = totalDistance(locations)
        best_path = [x[0] for x in path_with_locations]


        circuit_id = controller.new_circuit(best_path, await_build = True)

        def attach_stream(stream):
            if stream.status == 'NEW':
                controller.attach_stream(stream.id, circuit_id)
        
        controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)
        
        try:
            controller.set_conf('__LeaveStreamsUnattached', '1')

            for i in xrange(ntimes): # Check From Nofel
                subprocess.call(("sudo bash RunMe.sh " + url + " Result.txt " + str(distance) + " Saim"), shell=True)

        finally:
            # print "In finally: scan.py"
            controller.remove_event_listener(attach_stream)
            controller.reset_conf('__LeaveStreamsUnattached')



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
