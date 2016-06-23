import time

f_0 = open('Relay_Information_0', 'w')

from stem.descriptor.remote import DescriptorDownloader
downloader_0 = DescriptorDownloader()

try:
  for desc in downloader_0.get_server_descriptors().run(): # Information that relays publish about themselves.
    f_0.write( str(desc) + "\n\n\n\n\n") # Bandwidth in Bytes/s (Average, Burst, Observed)
    # print desc.__name__
except Exception as exc:
  print("Unable to retrieve the server descriptors: %s" % exc)

# ------------------------------------------------------
# Run this before any experiment.

f_1 = open('Relay_Information_1', 'w')

from stem.descriptor.remote import DescriptorDownloader
downloader_1 = DescriptorDownloader()

try:
  for desc in downloader_1.get_consensus().run(): # Information by directory authorities. (Published every hour.)
    f_1.write(str(desc) + "\n\n") # Gives bandwidth in kb/s
    # print desc.unrecognized_bandwidth_entries
except Exception as exc:
  print("Unable to retrieve the consensus: %s" % exc)


# ---------------------------------------------------------------------------------------------------
# import os

# from stem.control import Controller
# from stem.descriptor import parse_file

# with Controller.from_port(port = 9051) as controller:
#   controller.authenticate()

#   exit_digests = set()
#   data_dir = controller.get_conf('DataDirectory')

#   for desc in controller.get_microdescriptors():
#     if desc.exit_policy.is_exiting_allowed():
#       exit_digests.add(desc.digest)

#   print 'Exit Relays:'

#   for desc in parse_file(os.path.join(data_dir, 'cached-microdesc-consensus')):
#   	print desc
#     # if desc.digest in exit_digests:
#       # print '  %s (%s)' % (desc.nickname, desc.fingerprint)