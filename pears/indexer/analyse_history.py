import os
import re
import sys
import csv
import sqlite3
import numpy as np
from urlparse import urlparse, urljoin
#from pears.models import Urls,OpenVectors
#from pears import db

domains = {}
home_directory = os.path.expanduser('~')
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if not os.path.isdir(root_dir+"/userdata/"):
    os.makedirs(root_dir+"/userdata/")

common_sites =["google", "facebook", "twitter", "duckduckgo", "yahoo", "bing"]

def get_firefox_history_db(in_dir):
  """Given a home directory it will search it for the places.sqlite file
  in Mozilla Firefox and return the path. This should work on Windows/
  Linux"""
  print "Finding Firefox DB history..."
  firefox_directory = in_dir + "/.mozilla/firefox"
  for files in os.walk(firefox_directory):
    # Build the filename
    if re.search('places.sqlite', str(os.path.join(files))):
      history_db = str(os.path.realpath(files[0]) + '/places.sqlite')
      # print history_db
      return history_db
  return None

def record_urls_to_process(db_urls):
    urls_to_process = []
    for url_str in db_urls:

        url = unicode(url_str[1])
        if not url.startswith('http'):
            continue
        url = url.replace('http://', 'https://').rstrip('/')
        if "www" not in url:
            url_with_www = url.replace("https://", "https://www.")
            if url_with_www in urls_to_process:
                continue
        else:
            url_with_www = url
        urls_to_process.append(url)
        url_parsed = urlparse(url)
        netloc = url_parsed.netloc
        if netloc in domains:
            domains[netloc]+=1
        else:
            domains[netloc] = 1
    return urls_to_process

def index_history():
  # [TODO] Set the firefox path here via config file
  HISTORY_DB = get_firefox_history_db(home_directory)
  if HISTORY_DB is None:
    print 'Error - Cannot find the Firefox history database.\n\nExiting...'
    sys.exit(1)

  # connect to the sqlite history database
  firefox_db = sqlite3.connect(HISTORY_DB)
  cursor = firefox_db.cursor()

  # get the list of all visited places via firefox browser
  cursor.execute("SELECT * FROM 'moz_places' ORDER BY last_visit_date DESC")
  rows = cursor.fetchall()

  urls_to_process = record_urls_to_process(rows)
  firefox_db.close()
  return urls_to_process

def write_analysis():
  f = open(root_dir+"/userdata/history_analysis.txt",'w')
  for d in sorted(domains, key=domains.get, reverse=True):
    f.write(d+" "+str(domains[d])+"\n")
  f.close()

def update_pearsignore(ignore_list):
  recorded_domains = []
  with open(root_dir+"/userdata/.pearsignore",'a+') as f:
      for d in f:
        d = d.rstrip('\n')
        recorded_domains.append(d)

      for d in ignore_list:
        if d not in recorded_domains:
          f.write(d+"\n")

def runScript(*args):
  '''Run script, either by indexing part of history or by indexing the urls
  provided by the user'''
  urls_to_process = index_history()
  write_analysis()
  perhaps_ignore = []

  for d in sorted(domains, key=domains.get, reverse=True):
    #print d,domains[d]
    for s in common_sites:
      m = re.search("^"+s+"\.|\."+s+"\.",d)
      if m:
        perhaps_ignore.append(d)
  print "\n\nWe suggest you put the following sites in your .pearsignore file:"
  print perhaps_ignore

  answer = raw_input("\nYou can always manually modify the .pearsignore file afterwards.\n\
OK to populate .pearignore? (y/n)\n")
  if answer == "y":
      update_pearsignore(perhaps_ignore)

  print "\nIn userdata/history_analysis.txt, you will find a list of domain names\n\
from your history, sorted from the most frequently visited to the least.\n\
We advise to transfer any entry in that file to your .pearsignore if you\n\
don't want that domain to be indexed.\n\n\
Your .pearsignore is found in the userdata folder."

if __name__ == '__main__':
  runScript(sys.argv)
