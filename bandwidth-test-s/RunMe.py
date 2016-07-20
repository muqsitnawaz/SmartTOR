import stem.control
from geoip import geolite2
import ipgetter
import socket
import random
import subprocess
import StringIO
import pycurl
import time

Ranges = [(10000, 15000), (5000, 10000), (0, 5000)]
urlList = ['http://ipv4.download.thinkbroadband.com:80/5MB.zip', 
           'http://ipv4.download.thinkbroadband.com:80/10MB.zip',
           'http://ipv4.download.thinkbroadband.com:80/20MB.zip',
           'http://ipv4.download.thinkbroadband.com:80/50MB.zip',
           'http://ipv4.download.thinkbroadband.com:80/100MB.zip',
           'http://ipv4.download.thinkbroadband.com:80/200MB.zip']

def main():
    with stem.control.Controller.from_port() as controller:
        controller.authenticate()

        numReadings = 7
        
        for LOW, HIGH in Ranges:
            relays = get_relays(controller, LOW, HIGH)    

            entry = relays[0];
            middle = relays[1];
            exit = relays[2];

            if (len(entry) == 0 or len(middle) == 0 or len(exit) == 0):
                print ("Set of Entry / Middle / Exit Nodes was empty!")
                continue

            for i in range(0,5):
                entry_relay = entry[random.choice(entry.keys())], random.choice(entry.keys())
                middle_relay = middle[random.choice(middle.keys())], random.choice(middle.keys())
                exit_relay = exit[random.choice(exit.keys())], random.choice(exit.keys())

                circuit = [entry_relay, middle_relay, exit_relay]

                for url in urlList:
                    try:
                        if urlList.index(url) == 3:
                            scan(controller, circuit, url, 5, LOW, HIGH)
                        elif urlList.index(url) == 4:
                            scan(controller, circuit, url, 5, LOW, HIGH)
                        elif urlList.index(url) == 5:
                            scan(controller, circuit, url, 3, LOW, HIGH)
                        else:
                            scan(controller, circuit, url, numReadings, LOW, HIGH)
                    except Exception as E:
                        continue

                    time.sleep(60)



def scan(controller, circuit, url, numReadings, LOW, HIGH):
    path = [x[0][0] for x in circuit]

    try:
        circuit_id = controller.new_circuit(path, await_build = True)
    except Exception as E:
        print "Scan: " + str(E)
        return 1000

    def attach_stream(stream):
        if stream.status == 'NEW':
            try:
                controller.attach_stream(stream.id, circuit_id)
            except Exception as E:
                print "Scan: " + str(E)
                return 1000


    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

    try:
        controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
        getPage(controller, circuit, url, numReadings, LOW, HIGH)
    finally:
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')
        controller.close_circuit(circuit_id)


def getPage(controller, circuit, url, numReadings, LOW, HIGH):
    # print "IN GET PAGE"

    path = [x[0][0] for x in circuit]

    dest_Address =  geolite2.lookup(socket.gethostbyname('ipv4.download.thinkbroadband.com'))

    # print "FOUND DEST ADDRESS"

    myIP = ipgetter.myip() # Finds External IP Address.
    my_Address = geolite2.lookup(socket.gethostbyname(myIP))
    ip_list = [controller.get_network_status(x).address for x in path] # Get ip addresses from fingerprints
    locations_relay = [geolite2.lookup(x).location for x in ip_list] # Do lookups
    locations =  [my_Address.location] + locations_relay + [dest_Address.location]
    distance = totalDistance(locations) # Check Haversine File.

    # print "FOUND DISTANCE"

    for i in xrange(0,numReadings):
        command = "sudo bash RunMe.sh " + str(url) + " Result " + str(LOW) + " " + str(HIGH) + " " + str(circuit[0][0][0]) + " " + str(circuit[1][0][0]) + " " + str(circuit[2][0][0]) + " " + str(circuit[0][0][1]) + " " + str(circuit[1][0][1]) + " " + str(circuit[2][0][1]) + " " + str(distance)
        # print command
        subprocess.call((command), shell=True);


def get_relays(controller, low = float("-inf"), high = float("inf")):
    controller.authenticate()
    entry_dict = {}
    middle_dict = {}
    exit_dict = {}

    relay_fingerprints_all = [desc for desc in controller.get_network_statuses() if determine(desc.flags)]
    relay_fingerprints = [desc for desc in relay_fingerprints_all if set_bandwidth(desc.bandwidth, low, high)]

    entry_nodes = [desc for desc in relay_fingerprints if if_guard(desc.flags)]
    exit_nodes = [desc for desc in relay_fingerprints if if_exit(desc.flags)]
    middle_nodes = [desc for desc in relay_fingerprints if desc not in set(exit_nodes) and desc not in set(entry_nodes)]

    for relay in entry_nodes:
        my_Address = geolite2.lookup(relay.address)
        if my_Address is not None and my_Address.location is not None:
            entry_dict[my_Address.location] = (relay.fingerprint, relay.bandwidth)

    for relay in middle_nodes:
        my_Address = geolite2.lookup(relay.address)
        if my_Address is not None and my_Address.location is not None:
            middle_dict[my_Address.location] = (relay.fingerprint, relay.bandwidth)

    for relay in exit_nodes:
        my_Address = geolite2.lookup(relay.address)
        if my_Address is not None and my_Address.location is not None:
            exit_dict[my_Address.location] = (relay.fingerprint, relay.bandwidth)

    return (entry_dict, middle_dict, exit_dict)

def determine(flags):
    if ('Stable' and 'Running' and 'Valid') in flags:
        return True
    else:
        return False

def if_guard(flags):
    if 'Guard' in flags:
        return True
    else:
        return False

def if_exit(flags):
    if 'Exit' in flags:
        return True
    else:
        return False

def if_middle(flags):
    if 'Guard' not in flags and 'Exit' not in flags:
        return True
    else:
        return False

def set_bandwidth(bandwidth, low, high):
    if (bandwidth >= low and bandwidth <= high):
        return True
    else:
        return False


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

if __name__ == "__main__":
    main()