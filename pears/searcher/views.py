#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from flask import render_template, request, Blueprint
import requests, json, urllib2, ipgetter
from ast import literal_eval

from . import searcher

from pears import best_pears
from pears import scorePages
from pears.utils import read_pears, query_distribution, load_entropies

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
root_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))

def get_result_from_dht(query_dist):
    #print "Checking dht..."	
    #return False
    try:
        urllib2.urlopen('http://localhost:8080', timeout=1)
    except urllib2.URLError as err:
        return False
    url = 'http://localhost:8080'
    headers = {'content-type': 'application/json', 'Accept-Charset':
            'UTF-8', 'Connection': 'close'}
    query_str  = ' '.join([each.strip('\n\[\]') for each in str(query_dist).split(' ')])
    r = requests.post(url, data=json.dumps(query_str), headers=headers)
    body = r.text.split('\n')[-1] if r else ''
    result = body.strip('\'\[\] \t\r').split(',')
    return result

def get_cached_urls(urls):
  urls_with_cache = urls
  for u in urls_with_cache:
    cache = re.sub(r"http\:\/\/|https\:\/\/", root_dir+"/html_cache/", u[0])
    if os.path.exists(cache):
      u.append("file://"+cache)
    else:
      u.append(u[0])
  return urls_with_cache

@searcher.route('/')
@searcher.route('/index')
def index():
    results = []
    entropies_dict = load_entropies()
    query = request.args.get('q')
    if not query:
        return render_template("index.html")
    else:
        query_dist = query_distribution(query, entropies_dict)
        pear_details = []
        results = []
        if query_dist.size:
            pears = get_result_from_dht(query_dist)
            pear_profiles = read_pears(pears)
            pear_details = best_pears.find_best_pears(query_dist, pear_profiles)
            pear_ips = pear_details.keys()
            results = scorePages.runScript(query, query_dist, pear_ips)
        if not pear_details or not results:
          pears = ['no pear found :(']
          scorePages.ddg_redirect(query)
        elif not pears:
            pears = [ipgetter.myip()]
        # '''remove the following lines after testing'''
        # pages = [['http://test.com', 'test']]

        results = get_cached_urls(results)
        return render_template('results.html', pears=pears,
                               query=query, results=results)
      
