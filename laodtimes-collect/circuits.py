import StringIO
import time
import sys
import os
import geoip2.database
import pycurl
import stem.control
import subprocess
import shutil

command = 'mkdir' + ' ' + str(sys.argv[2])
os.system(command)
os.chdir(str(sys.argv[2]))
shutil.copy2('../result-format.csv', '.')

f0 = open("Entry_Nodes",'a')
f1 = open("Middle_Nodes",'a')
f2 = open("Exit_Nodes",'a')

counter = 0

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 60  # timeout before we give up on a circuit

def scan(controller, path):
  circuit_id = controller.new_circuit(path, await_build = True)

  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, circuit_id)

  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()

    subprocess.call(("../RunMe.sh " + str(sys.argv[1]) + " " + str(counter)), shell=True)

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