import sys
import os
import requests
import codecs
from bs4 import BeautifulSoup
from urllib2 import urlopen
from urllib import urlretrieve
from urlparse import urlparse, urljoin

#TODO: issue when indexing top domain
#check http links in same domain

def write_to_cache(html, cached_page):
  print "Writing to",cached_page,"..."
  cache = codecs.open(cached_page,'w', encoding='utf8')
  cache.write(unicode(html))
  cache.close()

def cache_file(url,html):
  '''Write html in local cache directory'''
  url_parsed = urlparse(url)
  path_dirs = url_parsed.path.rstrip('/')[1:].split('/')
  page = path_dirs[-1]
  cached_netloc = "./html_cache/"+url_parsed.netloc
  if page == "":
    page = "index.html"
  cached_dir = cached_netloc+"/"+'/'.join(path_dirs[:-1])+"/"
  if not os.path.isdir(cached_dir):
    os.makedirs(cached_dir)
  cached_page = cached_dir+page
  if not os.path.exists(cached_page):
    #urlretrieve(url, cached_page)
    write_to_cache(html,cached_page)

def get_images(url):
  """Downloads all the images at 'url' to cache"""
  req = requests.get(url, allow_redirects=True, timeout=20)
  soup = BeautifulSoup(req.text,"lxml")
  url_parsed = list(urlparse(url))
  for image in soup.findAll("img"):
    print "Image: %(src)s" % image
    if not image["src"].lower().startswith("http"):
      img_path = urljoin(url,image["src"])
      print img_path
      cache_file(img_path)

def get_css(url):
  """Downloads all the css to local cache"""
  req = requests.get(url, allow_redirects=True, timeout=20)
  soup = BeautifulSoup(req.text,"lxml")
  url_parsed = list(urlparse(url))
  for link in soup.findAll("link"):
    if link["rel"][0] == "stylesheet":
      print "Link: %(href)s" % link
      if not link["href"].lower().startswith("http"):
        css_path = urljoin(url,link["href"])
        print css_path
        cache_file(css_path)

def runScript(url,html):
  print "Caching",url,"..."
  cache_file(url,html)
  #Optional: grab the images and css for that page
  #get_images(url)
  #get_css(url)
