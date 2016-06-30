import sqlite3
import os
from datetime import datetime
import sys
from urlparse import urlparse
import socket
import calendar
import time
import operator

# -*- coding: utf-8 -*-

def execute_query(cursor, query):
    ''' Takes the cursor object and the query, executes it '''
    try:
        cursor.execute(query)
    except Exception as error:
        print(str(error) + "\n " + query)

def get_path(browser):
    '''Gets the path where the sqlite3 database file is present'''
    home_dir = os.environ['HOME']
    if browser == 'firefox':
        if sys.platform.startswith('win') == True:
            path = home_dir + '\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\'
        elif sys.platform.startswith('linux') == True:
            path = home_dir + "/.mozilla/firefox/"
        elif sys.platform.startswith('darwin') == True:
            path = home_dir + '/Library/Application Support/Firefox/Profiles/'

    elif browser == 'chrome':
        if sys.platform.startswith('win') == True:
            path = home_dir + ''
        elif sys.platform.startswith('linux') == True:
            path = home_dir + "/.config/chromium/Default/History"
        elif sys.platform.startswith('darwin') == True:
            path = home_dir+'/Library/Application Support/Google/Chrome/Default/History'
    return path


def history(cursor, src=""):
    ''' Function which extracts history from the sqlite file '''
    if src == 'firefox':
        sql = """select moz_historyvisits.id, moz_places.url, moz_places.visit_count, moz_historyvisits.visit_date/1000000 from moz_places, moz_historyvisits where moz_historyvisits.place_id = moz_places.id """
        sql1 = """select moz_historyvisits.id,
        moz_places.url,
        moz_places.visit_count,
        moz_historyvisits.visit_date/1000000,
        (select count(*) from moz_places as ct where ct.rev_host = moz_places.rev_host) as host_visit_count
        from moz_places, moz_historyvisits
        where moz_historyvisits.place_id = moz_places.id"""
        execute_query(cursor, sql)
        return cursor.fetchall()
    elif src == 'chrome':
        sql = "SELECT  urls.title, urls.url, urls.visit_count, \
        urls.last_visit_time/1000000-11644473600 FROM urls, visits\
        WHERE  urls.id = visits.url"
        execute_query(cursor, sql)
        return cursor.fetchall()


def parse_history (history):
    list = []
    for item in history:
        try:
            o = urlparse(item[1])
            url = o.hostname
            if url.startswith("www."):
                url = url[4:]
            list.append((url, item[2], item[3]))
        except Exception as e:
            continue
    return list

def combine_history(history):
    my_dict = {}
    for item in history:
        if item[0] in my_dict.keys():
            freq, date = my_dict[item[0]]
            if freq == 0:
                continue
            my_dict[item[0]] = (freq+item[1], ((freq*date) + (item[1] * item[2]))/(freq+item[1]))
        else:
            my_dict[item[0]] = (item[1], item[2])
    return my_dict

def dns_lookup(history):
    not_found = []
    for (key, val) in history.iteritems():
        try:
            ip = socket.gethostbyname(key)
            history[key] = val+ (ip,)
        except:
            not_found.append(key)
            continue
    print not_found
    for key in not_found:
        try:
            del history[key]
        except:
            continue
    return history

def convert_epoch_to_time_passed (history):
    t = calendar.timegm(time.gmtime())
    for (key, val) in history.iteritems():
        time_passed = t - (val[1])
        history[key] = (val[0], time_passed, val[2])
    return history

def get_history():
    try:
        firefox_path = get_path('firefox')
        chrome_sqlite_path = get_path('chrome')
        profiles = [i for i in os.listdir(firefox_path) if ('.default') in i]
        sqlite_path = firefox_path+ profiles[0]+'/places.sqlite'
        if os.path.exists(sqlite_path):
            firefox_connection = sqlite3.connect(sqlite_path)
        if os.path.exists(chrome_sqlite_path):
            chrome_connection = sqlite3.connect(chrome_sqlite_path)
    except Exception as error:
        print(str(error))
        exit(1)
    cursor = firefox_connection.cursor()
    hist = history(cursor, src="firefox")
    hist = parse_history(hist)
    hist = combine_history(hist)
    return hist

# history is of the form, key: hostname, val: (visit_count, visit_date)
def get_top_visited(history, n):
    sorted_list = sorted(history.keys(), key=lambda x: history[x], reverse = True)
    if n > len(sorted_list):
        return sorted_list
    return sorted_list[:n]

def get_first(tuple):
    # print tuple
    return tuple

