import time
import pycurl
import StringIO
import pycurl
import stem.control
from geoip import geolite2

CONNECTION_TIMEOUT = 150
row = [];
total = [];
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

        # print dir(entry_nodes[0])
        # Canada, 
        websites = ["google.com.pk", "baidu.com", "ebay.com.au", "facebook.com", "youtube.com.pk", "amazon.com"
                    "baidu.com", "imdb.com"]
        numReadings = 1

        for i in xrange(0,100):
            print row;
            row = [];
            try:
                result_file = open("head_results.txt", "a")
                path = [entry_nodes[i].fingerprint, middle_nodes[i].fingerprint, exit_nodes[i].fingerprint]

                row.append(path);
                result_file.write('Country: ')
                result_file.write(geolite2.lookup((exit_nodes[i].address)).country)
                row.append(geolite2.lookup((exit_nodes[i].address)).country);
                result_file.write('\nPath: ')
                result_file.write(str(path))
                result_file.write('\nBandwidth (KB/s): ')
                result_file.write(str(entry_nodes[i].bandwidth) + " " + str(middle_nodes[i].bandwidth) + " " + str(exit_nodes[i].bandwidth))
                result_file.write('\nResults: \n')
                scan(controller, path, websites, numReadings, result_file)
                result_file.close()
            except:
                continue

            # Element: [(f,b), (f,b), (f,b), country, (google, time), (baidu, time)]
            # Element: [(f,b), (f,b), (f,b), country, (google, time), (baidu, time)]
            # Element: [(f,b), (f,b), (f,b), country, (google, time), (baidu, time)]


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

def scan(controller, path, websites, numReadings, result_file):
    circuit_id = controller.new_circuit(path, await_build = True)

    def attach_stream(stream):
        if stream.status == 'NEW':
            try:
                controller.attach_stream(stream.id, circuit_id)
            except:
                result_file.write('ERROR\n')
                return 100


    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

    try:
        controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
        scan_head(websites, numReadings, result_file)
        getPage(websites, numReadings)
    finally:
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')


def scan_head(websites, numReadings, result_file):
    for url in websites:
        try:
            time_calculated = 0
            avg_time = 0

            url = 'https://www.' + url

            for i in xrange(0, numReadings):
                start_time = time.time()
                check_page = query_head(url)
                if check_page == -1:
                    time_calculated =  -1
                else:
                    time_calculated = time.time() - start_time
                    avg_time = avg_time + time_calculated
                # result_file.write(url + " , " + str(round(time_calculated,2)) + "\n")
            result_file.write(url + " , AVG: " + str(round((avg_time / numReadings),2)) + "\n")
            row.append(( url,str(avg_time/numReadings) ) );
        except:
            continue
##for full page request
def getPage(websites, numReadings):
    for url in websites:
        try:
            url = 'https://www.' + url;
            for i in xrange(0,numReadings):
                start_time = time.time();
                subprocess.call(("sudo bash RunMe.sh " + url + " Result.txt " + str(distance) + " TOR"), shell=True);
                #time_calculated = time.time() - start_time;
        except:
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
        print "Starting Curl Perform"
        query.perform()
        print "Curl Finished"
    # fd.write(output.getvalue())
        return output.getvalue()
    except pycurl.error as exc:
        print("Unable to reach ", url)
        return -1

if __name__ == "__main__":
    main()
