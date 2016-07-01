import time
import pycurl
import StringIO
import pycurl
import stem.control
import ipgetter
import socket
from geoip import geolite2
import pickle
import subprocess
# from tempfile import TemporaryFile

CONNECTION_TIMEOUT = 30

def main():
    with stem.control.Controller.from_port() as controller:
        controller.authenticate()

        entry_nodes = []
        exit_nodes = []
        middle_nodes = []

        for desc in controller.get_network_statuses():
            if determine(desc.flags):
                if if_middle(desc.flags):
                    middle_nodes.append(desc)
                if if_guard(desc.flags):
                    entry_nodes.append(desc)
                if if_exit(desc.flags):
                    exit_nodes.append(desc)

        websites = ["google.com.pk", "facebook.com", "amazon.com", "youtube.com.pk", "wikipedia.org"]
        numReadings = 10
        array = [];

        for i in xrange(0,150,10):
            try:
                path = [entry_nodes[i].fingerprint, middle_nodes[i].fingerprint, exit_nodes[i].fingerprint]
                array.append([(entry_nodes[i].fingerprint,entry_nodes[i].bandwidth, geolite2.lookup((entry_nodes[i].address)).country), 
                    (middle_nodes[i].fingerprint,middle_nodes[i].bandwidth, geolite2.lookup((middle_nodes[i].address)).country)
                    , (exit_nodes[i].fingerprint,exit_nodes[i].bandwidth, geolite2.lookup((exit_nodes[i].address)).country)]);
                scan(controller, path, websites, numReadings, array)
                print i
            except Exception as E:
                print E
                continue


        file = open("scan_website_exp.txt", "w")
        pickle.dump(array, file)

def sort_array(array, index):
    for i in range(0,len(array)):
        for j in range(i,len(array)):
            if (array[i][index][1] > array[j][index][1]):
                temp = array[i]
                array[i] = array[j]
                array[j] = temp

    return array

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

def scan(controller, path, websites, numReadings, array):
    circuit_id = controller.new_circuit(path, await_build = True)

    def attach_stream(stream):
        if stream.status == 'NEW':
            try:
                controller.attach_stream(stream.id, circuit_id)
            except Exception as E:
                print E
                return 1000


    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

    try:
        controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
        getPage(controller, websites, numReadings, array, path)
    finally:
        print "ERROR"
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')


def scan_head(controller, websites, numReadings, array, path):
    totalReadings = numReadings

    for url in websites:
        try:
            time_calculated = 0
            avg_time = 0

            dest_Address =  geolite2.lookup(socket.gethostbyname(url)) # Finds Location Data of Website.
            url = 'https://www.' + url

            for i in xrange(0, numReadings):
                start_time = time.time()
                check_page = query_head(url)
                if check_page == -1:
                    time_calculated =  0
                    totalReadings = totalReadings - 1
                else:
                    time_calculated = time.time() - start_time
                    avg_time = avg_time + time_calculated
                # result_file.write(url + " , " + str(round(time_calculated,2)) + "\n")

            myIP = ipgetter.myip() # Finds External IP Address.
            my_Address = geolite2.lookup(socket.gethostbyname(myIP))
            ip_list = [controller.get_network_status(x).address for x in path] # Get ip addresses from fingerprints
            locations_relay = [geolite2.lookup(x).location for x in ip_list] # Do lookups
            locations =  [my_Address.location] + locations_relay + [dest_Address.location]
            distance = totalDistance(locations) # Check Haversine File.

            array[-1].append((url,avg_time/totalReadings,distance));
        except Exception as E:
            print E
            continue

##for full page request
def getPage(controller, websites, numReadings, array, path):
    for url in websites:
        try:
            dest_Address =  geolite2.lookup(socket.gethostbyname(url))
            url = 'https://www.' + url;

            myIP = ipgetter.myip() # Finds External IP Address.
            my_Address = geolite2.lookup(socket.gethostbyname(myIP))
            ip_list = [controller.get_network_status(x).address for x in path] # Get ip addresses from fingerprints
            locations_relay = [geolite2.lookup(x).location for x in ip_list] # Do lookups
            locations =  [my_Address.location] + locations_relay + [dest_Address.location]
            distance = totalDistance(locations) # Check Haversine File.

            array[-1].append((url,distance));


            for i in xrange(0,numReadings):
                command = "phantomjs --proxy=127.0.0.1:9050 --proxy-type=socks5 loadspeed.js " + url + " " + str(distance) + " " + str(i) + " TOR"
                subprocess.call((command), shell=True);
        except Exception as E:
            print E
            continue;  


def query_head(url):
    """
    Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
    """

    output = StringIO.StringIO()

    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.PROXY, 'localhost')
    query.setopt(pycurl.PROXYPORT, 9050)
    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
    query.setopt(pycurl.WRITEFUNCTION, output.write)
    query.setopt(pycurl.HEADER, True)
    query.setopt(pycurl.NOBODY, True)
    query.setopt(pycurl.FOLLOWLOCATION, 1)

    try:
        # print "Starting Curl Perform"
        query.perform()
        # print "Curl Finished"
    # fd.write(output.getvalue())
        return output.getvalue()
    except pycurl.error as exc:
        print("Unable to reach ", url)
        return -1


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

