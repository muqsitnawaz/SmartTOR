import StringIO
import time
import sys
import pycurl
# from cStringIO import StringIO
import stem.control

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit


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


def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

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
    # fd.write(output.getvalue())
    return output.getvalue()
  except pycurl.error as exc:
    print("Unable to reach ", url)
    return -1

def query_head(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

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
    # fd.write(output.getvalue())
    return output.getvalue()
  except pycurl.error as exc:
    print("Unable to reach ", url)
    return -1

def scan_head(controller,curCircuit, url):
  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, curCircuit.id)
  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)
  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()
    check_page = query_head(url)
    if check_page == -1:
      return -1
    # print check_page
    return time.time() - start_time
  finally:
    controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')

def scan(controller,curCircuit, url, fd):
  # print all_circuits

# circuit_id = controller.new_circuit(path, await_build = True)
  # print curCircuit.path[0][0]
  # sys.exit("Stopping Program")

  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, curCircuit.id)
    # else:
    #   print stream.status

  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()
    # print "Check 1"
    check_page = query(url)
    if (check_page == -1):
      return -1
    fd.write(check_page)
    # print "Check 2"
    # if 'Congratulations. This browser is configured to use Tor.' not in check_page:
    #   raise ValueError("Request didn't have the right content")

    print "Check 3"
    return time.time() - start_time
  finally:
    # print "In finally: scan.py"
    controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')


# with stem.control.Controller.from_port() as controller:
#   controller.authenticate()

#   all_circuits = controller.get_circuits()

#   for curCircuit in all_circuits:
#     if curCircuit.path > 2:
#       print curCircuit.path
#       try:
#         time_taken = scan(controller,curCircuit, 'https://www.google.com.pk')
#         print('%0.2f seconds' % (time_taken))
#         sys.exit('Done once')
#       except Exception as exc:
#         print "im in scan.py"
#         print "Error occured"
