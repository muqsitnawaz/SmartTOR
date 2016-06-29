import time
import pycurl
import StringIO
from geoip import geolite2
import socket


CONNECTION_TIMEOUT = 30

def main():
	# print socket.gethostbyname("cachefly.cachefly.net")
	websites = ["cachefly.cachefly.net/100mb.test"]
	# print cutUrl(websites[0])
	numReadings = 1
	head_result_file = open("head_results.txt", "a")
	scan_head(websites, numReadings, head_result_file)

def cutUrl(url):
	return url.split('/',1)[0]

def scan_head(websites, numReadings, head_result_file):
	time_calculated = 0
	for url in websites:
		
		# address = geolite2.lookup(socket.gethostbyname(cutUrl(url)))
		# print address
		url = 'https://' + url

		for i in xrange(0, numReadings):
			start_time = time.time()
			check_page = query_head(url)
			if check_page == -1:
				time_calculated =  -1
			else:
				time_calculated = time.time() - start_time
			head_result_file.write(url + " , " + str(round(time_calculated,2)) + "\n")


def query_head(url):
	"""
	Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
	"""

	output = StringIO.StringIO()

	query = pycurl.Curl()
	query.setopt(pycurl.URL, url)
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
