import StringIO
import time
import pycurl
import stem.control
import sys
import string
from geoip import geolite2
import datrie

def determine(flags):
	if ('Fast' and 'Stable' and 'Running' and 'Stable' and 'Valid') in flags:
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

def insert_in_trie(relay_list,trie):
	for relay in relay_list:
		trie[relay.address] = relay.fingerprint

def get_possible_middle(the_trie, ip_to_match):
	temp_middle = the_trie.keys(ip_to_match)
	print "IP Matching: "
	print ip_to_match
	while len(temp_middle) < 5:
		ip_to_match = ip_to_match[:-1]
		temp_middle = the_trie.keys(ip_to_match)
	return temp_middle

# Returns tuple (entry,middle,exit)
def get_relays(controller):
	controller.authenticate()
	entry_dict = {}
	middle_dict = {}
	exit_dict = {}

	relay_fingerprints = [desc for desc in controller.get_network_statuses() if determine(desc.flags)]
	entry_guards = [desc for desc in relay_fingerprints if if_guard(desc.flags)]
	exit_nodes = [desc for desc in relay_fingerprints if if_exit(desc.flags)]
	middle_nodes = [desc for desc in relay_fingerprints if desc not in set(exit_nodes) and desc not in set(entry_guards)]

	for relay in entry_guards:
		my_Address = geolite2.lookup(relay.address)
		if my_Address is not None and my_Address.location is not None:
			entry_dict[my_Address.location] = relay.fingerprint

	for relay in middle_nodes:
		my_Address = geolite2.lookup(relay.address)
		if my_Address is not None and my_Address.location is not None:
			middle_dict[my_Address.location] = relay.fingerprint

	for relay in exit_nodes:
		my_Address = geolite2.lookup(relay.address)
		if my_Address is not None and my_Address.location is not None:
			exit_dict[my_Address.location] = relay.fingerprint

	return (entry_dict,middle_dict,exit_dict)

# with stem.control.Controller.from_port() as controller:
# 	controller.authenticate()
# 	print get_relays(controller)

# 	relay_fingerprints = [desc for desc in controller.get_network_statuses() if determine(desc.flags)]

# 	# print len(relay_fingerprints)

# 	entry_guards = [desc for desc in relay_fingerprints if if_guard(desc.flags)]

# 	print len(entry_guards)

# 	exit_nodes = [desc for desc in relay_fingerprints if if_exit(desc.flags)]

# 	print len(exit_nodes)

# 	middle_nodes = [desc for desc in relay_fingerprints if desc not in set(exit_nodes) and desc not in set(entry_guards)]

# 	print len(middle_nodes)

# 	entry_dict = {}
# 	middle_dict = {}
# 	exit_dict = {}

# 	# counter = 0
# 	for relay in entry_guards:
# 		# print relay.address
# 		my_Address = geolite2.lookup(relay.address)
# 		# print my_Address.location
# 		if my_Address is not None:
# 			entry_dict[geolite2.lookup(relay.address).location] = relay.fingerprint
# 		# else:
# 		# 	counter = counter + 1

# 	for relay in middle_nodes:
# 		# print relay.address
# 		my_Address = geolite2.lookup(relay.address)
# 		# print my_Address.location
# 		if my_Address is not None:
# 			middle_dict[geolite2.lookup(relay.address).location] = relay.fingerprint

# 	for relay in exit_nodes:
# 		# print relay.address
# 		my_Address = geolite2.lookup(relay.address)
# 		# print my_Address.location
# 		if my_Address is not None:
# 			exit_dict[geolite2.lookup(relay.address).location] = relay.fingerprint

# 	# print counter
# 	# entry_trie = datrie.Trie(string.printable)
# 	# middle_trie = datrie.Trie(string.printable)
# 	# exit_trie = datrie.Trie(string.printable)

# 	# insert_in_trie(entry_guards,entry_trie)
# 	# insert_in_trie(middle_nodes,middle_trie)
# 	# insert_in_trie(exit_nodes,exit_trie)

# # Step 3 - Works but moving back 1 character at a time not bit by bit
# 	middle_trie = datrie.Trie(string.printable)
# 	insert_in_trie(middle_nodes,middle_trie)

# 	temp_exit_nodes = exit_nodes[:5]

# 	temp_exit_nodes = [desc.address for desc in temp_exit_nodes] # Change it later

# 	print temp_exit_nodes

# 	possible_middle = []

# 	for i in xrange(5):
# 		selected_exit = temp_exit_nodes[i]
# 		possible_middle.append(get_possible_middle(middle_trie,selected_exit))

# 	print possible_middle
