import re
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from urlparse import urlparse
import urllib2, os
import operator
def getBaseURL(urlInput):
	parsedURL = urlparse(urlInput)
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsedURL)
	return domain
def getURLSize(urlInput):
	try:
		f = urllib2.urlopen (urlInput)
		if "Content-Length" in f.headers:
			size = int (f.headers["Content-Length"])
		else:
			size = 0
		return size
	except Exception, e:
		raise e
		return 0

def findMaxURLs(inputDictionary,n):
	sortedDictionary = sorted(inputDictionary.items(),key = operator.itemgetter(1))
	return sortedDictionary[len(sortedDictionary)-n:]
def getAllURLsFromPage(pageContents):
	return re.findall(r'(https?://[^\s]+)', pageContents)
def getFetechableURLsFromPage(pageContents):
	return re.findall(r'(src=\"https?://[^\s]+\")', pageContents)
def insertURLsInDB(urlList):
	if len(urlList) == 0:
		return
	for oneURL in urlList:
		client = MongoClient()
		db = client.test

		result = db.URLCollection.insert_one(
		    {
		        "address": oneURL
		    }
		)
def insertURLIntoDB(url):
	client = MongoClient()
	db = client.test

	result = db.URLCollection.insert_one(
	    {
	        "address": url
	    }
	)
def findAllURLs():
	client = MongoClient()
	db = client.test

	cursor = db.URLCollection.find()
	urlList = []
	for document in cursor:
		urlList.append(document["address"])
	return urlList
def findURL(url):
	client = MongoClient()
	db = client.test
	cursor = db.URLCollection.find({"address":url})

	for document in cursor:
		return True
	return False

def greaterThenValue(n):
	client = MongoClient()
	db = client.test
	cursor = list(db.URLCollection.aggregate([
	{"$group" : {"_id" : "$address", "count":  { "$sum" : 1}}
	}]))
	urlList =[]
	for document in cursor:
		if document["count"]>=n:
			urlList.append(document["_id"])
	return urlList

def findTopN(n):
	client = MongoClient()
	db = client.test
	cursor = list(db.URLCollection.aggregate([
	{"$group" : {"_id" : "$address", "count":  { "$sum" : 1}}
	},
	{"$limit": n}]))
	urlList = []
	for document in cursor:
		urlList.append(document["_id"])
	return urlList

def getTopURLsFromPage(pageContents,n):
	urlList = getFetechableURLsFromPage(pageContents)
	dictionary = {}
	for x in urlList:
		key = getBaseURL(x)
		value = 1
		if dictionary.has_key(key):
			temp = dictionary.get(key)
			dictionary[key] = temp+value
			print "here"
		else:
			print dictionary.has_key(key)
			dictionary[key] = value
	return findMaxURLs(dictionary,n)


dic = {"aa":10,"b":2,"aaa":5,"c":100,"a":1}
findMaxURLs(dic,2)