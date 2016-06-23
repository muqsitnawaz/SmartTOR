import StringIO
import time
import sys
import os
import geoip2.database
import pycurl
import stem.control

f_0 = open('Published_Relay_Information', 'w')
f_1 = open('Hourly_Relay_Information', 'w')


# -----------------------------------  MAIN  ----------------------------------------

reader = geoip2.database.Reader('GeoLite2-City.mmdb') # So we can find where the relay is located.

from stem.descriptor.remote import DescriptorDownloader
downloader_0 = DescriptorDownloader()

for desc in downloader_0.get_server_descriptors().run(): # Information that relays publish about themselves.
    try:
      f_0.write(str(desc) + "l " + str(reader.city(str(desc.address)).country.name) + "\n\n")
    except:
      f_0.write(str(desc) + "l " + str("NOT FOUND IN DATABASE") + "\n\n")

with stem.control.Controller.from_port() as controller:
  controller.authenticate()

  for desc in controller.get_network_statuses():
    try:
      f_1.write(str(desc) + "l " + str(reader.city(str(desc.address)).country.name) + "\n\n")
    except:
      f_1.write(str(desc) + "l " + str("NOT FOUND IN DATABASE") + "\n\n")