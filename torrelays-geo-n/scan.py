import StringIO
import time
import sys
import pycurl
import stem.control

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit

# ====================================================================================
# Take a list of URLs and using pycurl, generates requests for all urls together
# ====================================================================================

def query_parallel(urls):
    m = pycurl.CurlMulti()
    reqs = []
    for url in urls: 
        response = StringIO.StringIO()
        handle = pycurl.Curl()
        handle.setopt(pycurl.URL, url)
        handle.setopt(pycurl.WRITEFUNCTION, response.write)
        handle.setopt(pycurl.PROXY, '127.0.0.1')
        handle.setopt(pycurl.PROXYPORT, SOCKS_PORT)
        handle.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
        handle.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
        handle.setopt(pycurl.FOLLOWLOCATION, 1)
        req = (url, response, handle)
        m.add_handle(req[2])
        reqs.append(req)

    SELECT_TIMEOUT = 30.0
    num_handles = len(reqs)
    start_time = time.time()
    while num_handles:
        ret = m.select(SELECT_TIMEOUT)
        if ret == -1:
            continue
        while 1:
            ret, num_handles = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM: 
                break
    totalTime = time.time() - start_time
    for req in reqs:
        filename = get_filename(req[0])
        time.sleep(1)
        if len(filename) > 32:
            filename = filename[:32]
        fd = open(filename, "w")
        time.sleep(1)
        fd.write(req[1].getvalue())
        time.sleep(1)
        fd.close()
        time.sleep(1)
    return totalTime



def get_filename(url):
    toks = url.split("/")
    return toks[len(toks)-1]


# ====================================================================================
# Generates a single request to the specified url using pycurl
# ====================================================================================
def query(url):
    output = StringIO.StringIO()

    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.PROXY, '127.0.0.1')
    query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
    query.setopt(pycurl.WRITEFUNCTION, output.write)
    query.setopt(pycurl.FOLLOWLOCATION, 1)

    try:
        print "Starting Curl Perform"
        query.perform()
        print "Curl Finished"
        return output.getvalue()
    except pycurl.error as exc:
        print("Unable to reach ", url)
        return -1

def query_head(url):
    output = StringIO.StringIO()
    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.PROXY, '127.0.0.1')
    query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
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
        return output.getvalue()
    except pycurl.error as exc:
        print("Unable to reach ", url)
        return -1
    except:
        print "Some other error"
        return -1


# ====================================================================================
# Uses Controller to attach stream to specified circuit
# Uses query_head function to request head for the provided url
# Return time taken
# ====================================================================================
def scan_head(controller, curCircuit, url):
    def attach_stream(stream):
        if stream.status == 'NEW':
            controller.attach_stream(stream.id, curCircuit.id)

    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)
    try:
        controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us

        start_time = time.time()
        print "Starting Curl"        
        check_page = query_head(url)
        print "Curl Finished"
        if check_page == -1:
            return -1
        return time.time() - start_time
    finally:
        print "Resetting stuff"
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')
