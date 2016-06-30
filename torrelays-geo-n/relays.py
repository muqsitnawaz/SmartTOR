import StringIO
import time
import pycurl
import stem.control
import sys
import string
from geoip import geolite2
import datrie

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
def get_relays(controller, low = float("-inf"), high = float("inf")):
	controller.authenticate()
	entry_dict = {}
	middle_dict = {}
	exit_dict = {}

	relay_fingerprints_all = [desc for desc in controller.get_network_statuses() if determine(desc.flags)]
	relay_fingerprints = [desc for desc in relay_fingerprints_all if set_bandwidth(desc.bandwidth, low, high)]

	if (high < 1000):
		entry_guards = [desc for desc in relay_fingerprints_all if if_guard(desc.flags)]
	else:
		entry_guards = [desc for desc in relay_fingerprints if if_guard(desc.flags)]

	exit_nodes = [desc for desc in relay_fingerprints if if_exit(desc.flags)]
	middle_nodes = [desc for desc in relay_fingerprints if desc not in set(exit_nodes) and desc not in set(entry_guards)]

	# print entry_guards
	for relay in entry_guards:
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

# def get_relays(controller):
# 	controller.authenticate()
# 	entry_dict = {}
# 	middle_dict = {}
# 	exit_dict = {}

# 	relay_fingerprints = [desc for desc in controller.get_network_statuses() if determine(desc.flags)]
# 	entry_guards = [desc for desc in relay_fingerprints if if_guard(desc.flags)]
# 	exit_nodes = [desc for desc in relay_fingerprints if if_exit(desc.flags)]
# 	middle_nodes = [desc for desc in relay_fingerprints if desc not in set(exit_nodes) and desc not in set(entry_guards)]

# 	for relay in entry_guards:
# 		my_Address = geolite2.lookup(relay.address)
# 		if my_Address is not None and my_Address.location is not None:
# 			entry_dict[my_Address.location] = (relay.fingerprint, relay.bandwidth)

# 	for relay in middle_nodes:
# 		my_Address = geolite2.lookup(relay.address)
# 		if my_Address is not None and my_Address.location is not None:
# 			middle_dict[my_Address.location] = (relay.fingerprint, relay.bandwidth)

# 	for relay in exit_nodes:
# 		my_Address = geolite2.lookup(relay.address)
# 		if my_Address is not None and my_Address.location is not None:
# 			exit_dict[my_Address.location] = (relay.fingerprint, relay.bandwidth)

# 	return (entry_dict,middle_dict,exit_dict)
