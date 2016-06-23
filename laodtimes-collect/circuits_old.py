import StringIO
import time
import sys
import os
import geoip2.database
import pycurl
import stem.control

command = 'mkdir' + ' ' + str(sys.argv[2])
os.system(command)
os.chdir(str(sys.argv[2]))

f0 = open("Entry_Nodes",'a')
f1 = open("Middle_Nodes",'a')
f2 = open("Exit_Nodes",'a')

counter = 0

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 60  # timeout before we give up on a circuit

def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

  output = StringIO.StringIO()

  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.PROXY, 'localhost')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
  query.setopt(pycurl.WRITEFUNCTION, output.write)

  try:
    query.perform()
    global f_results
    global counter
    f_results.write("File_Generated_" + str(counter) + ".html" + " | ")
    f_results.write(str(query.getinfo(query.EFFECTIVE_URL)) + " | ")
    f_results.write(str(query.getinfo(query.HTTP_CODE)) + " | ")
    f_results.write(str(query.getinfo(query.TOTAL_TIME)) + " | ")
    f_results.write(str(query.getinfo(query.NAMELOOKUP_TIME)) + " | ")
    f_results.write(str(query.getinfo(query.CONNECT_TIME)) + " | ")
    f_results.write(str(query.getinfo(query.PRETRANSFER_TIME)) + " | ")
    f_results.write(str(query.getinfo(query.REDIRECT_TIME)) + " | ")
    f_results.write(str(query.getinfo(query.REDIRECT_COUNT)) + " | ")
    f_results.write(str(query.getinfo(query.SIZE_UPLOAD)) + " | ")
    f_results.write(str(query.getinfo(query.SIZE_DOWNLOAD)) + " | ")
    f_results.write(str(query.getinfo(query.SPEED_UPLOAD)) + " | ")
    f_results.write(str(query.getinfo(query.HEADER_SIZE)) + " | ")
    f_results.write(str(query.getinfo(query.REQUEST_SIZE)) + " | ")
    f_results.write(str(query.getinfo(query.CONTENT_LENGTH_DOWNLOAD)) + " | ")
    f_results.write(str(query.getinfo(query.CONTENT_LENGTH_UPLOAD)) + " | ")
    f_results.write(str(query.getinfo(query.CONTENT_TYPE)) + " | ")
    f_results.write(str(query.getinfo(query.RESPONSE_CODE)) + " | ")
    f_results.write(str(query.getinfo(query.SPEED_DOWNLOAD)) + " | ")
    f_results.write(str(query.getinfo(query.SSL_VERIFYRESULT)) + " | ")
    f_results.write(str(query.getinfo(query.INFO_FILETIME)) + " | ")
    f_results.write(str(query.getinfo(query.STARTTRANSFER_TIME)) + " | ")
    f_results.write(str(query.getinfo(query.REDIRECT_TIME)) + " | ")
    f_results.write(str(query.getinfo(query.REDIRECT_COUNT)) + " | ")
    f_results.write(str(query.getinfo(query.HTTP_CONNECTCODE)) + " | ")
    f_results.write(str(query.getinfo(query.HTTPAUTH_AVAIL)) + " | ")
    f_results.write(str(query.getinfo(query.PROXYAUTH_AVAIL)) + " | ")
    f_results.write(str(query.getinfo(query.OS_ERRNO)) + " | ")
    f_results.write(str(query.getinfo(query.NUM_CONNECTS)) + " | ")
    f_results.write(str(query.getinfo(query.SSL_ENGINES)) + " | ")
    f_results.write(str(query.getinfo(query.INFO_COOKIELIST)) + " | ")
    f_results.write(str(query.getinfo(query.LASTSOCKET)) + " | ")
    f_results.write(str(query.getinfo(query.FTP_ENTRY_PATH)) + " | ")
    return output.getvalue()
  except pycurl.error as exc:
    raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller, path):
  circuit_id = controller.new_circuit(path, await_build = True)

  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, circuit_id)

  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()

    returned_page = query(sys.argv[1])
    open(str(counter) + ".html", "w").write(returned_page)

    return time.time() - start_time
  finally:
    controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')


# -----------------------------------  MAIN  ----------------------------------------

f3 = open("Time_of_Experiment", 'a')
f3.write((time.strftime("%c") + "\n"))
f3.close()
with stem.control.Controller.from_port() as controller:
  controller.authenticate()
  
  entry_nodes = []
  exit_nodes = []
  middle_nodes = []
  total_nodes = []

  # print "Node Collection Start \n"
  reader = geoip2.database.Reader('../GeoLite2-City.mmdb')

  for i in controller.get_network_statuses():
    total_nodes.append(i)

  total_nodes.sort(key=lambda x: x.bandwidth, reverse=True)

  for desc in total_nodes:
    if (reader.city(str(desc.address)).country.name) == sys.argv[5]:
      middle_nodes.append(desc.fingerprint)
      f1.write(str(desc) + "l " + str(reader.city(str(desc.address)).country.name) + "\n\n")

    if 'Guard' in (desc.flags) and str(reader.city(str(desc.address)).country.name) == sys.argv[4]:
      f0.write(str(desc) + "l " + str(reader.city(str(desc.address)).country.name) + "\n\n")
      entry_nodes.append(desc.fingerprint)
    if 'Exit' in (desc.flags) and str(reader.city(str(desc.address)).country.name) == sys.argv[6]:
      f2.write(str(desc) + "l " + str(reader.city(str(desc.address)).country.name) + "\n\n")
      exit_nodes.append(desc.fingerprint)

  entry_nodes = [entry_nodes[x] for x in [0,1,2]]
  exit_nodes = [exit_nodes[x] for x in [0,1,2]]
  middle_nodes = [middle_nodes[x] for x in [0,1,2]]

  f0.close()
  f1.close()
  f2.close()

  print "Experiment Begins: \n\n"

  for fingerprint_0 in entry_nodes:
    for fingerprint_1 in middle_nodes:
      if (fingerprint_0 == fingerprint_1): continue
      for fingerprint_2 in exit_nodes:
        if (fingerprint_2 == fingerprint_0 or fingerprint_2 == fingerprint_1): continue
        for i in range (0,int(sys.argv[3])):
          # global counter
          counter = counter + 1
          try:
            f_results = open("Results", 'a')
            time_taken = scan(controller, [fingerprint_0, fingerprint_1, fingerprint_2])
            f_results.write(str(sys.argv[1]) + " | " + str(fingerprint_0) + " | " + str(fingerprint_1) \
            + " | " + str(fingerprint_2) + " | " + str(time_taken) + "\n")
            print('(%s,%s,%s,%s \n) => %0.2f seconds' % (str(sys.argv[1]),fingerprint_0,fingerprint_1,fingerprint_2, time_taken))
            f_results.close()
          except Exception as exc:
            f_results.write(str(fingerprint_0) + " | " + str(fingerprint_1) + " | " + str(fingerprint_2) + \
            " | " + str(exc) + "\n")
            print('(%s,%s,%s) => %s \n' % (fingerprint_0,fingerprint_1,fingerprint_2, exc))
            f_results.close()

f3 = open("Time_of_Experiment", 'a')
f3.write((time.strftime("%c") + "\n"))
f3.close()
os.chdir('..')