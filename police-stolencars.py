# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup,SoupStrainer
import re
import os
from urlparse import urlparse
import urllib2
import sys

class PageCrawler:

    url = None
    paging_param_first = None
    paging_param_step = None
    current_paging_value = None

    def __init__(self, url, paging_param_first = 1, paging_param_step = 1):
        self.url = url
        self.paging_param_first = paging_param_first
        self.paging_param_step = paging_param_step

    def __iter__(self):
        return self

    def next(self):
        if(self.current_paging_value is None):
            self.current_paging_value = self.paging_param_first
        else:
            self.current_paging_value = self.current_paging_value + self.paging_param_step

        current_url = self.url.replace("${paging}", str(self.current_paging_value))
        return Downloader(current_url).get()



class Downloader:
    _url = None
    def __init__(self, url):
        urllib2.socket.setdefaulttimeout(60)
        self._url = url

    def get(self):
        downloaded = False
        download_counter = 0
        page = None
        while not(downloaded) and download_counter < 30:
            try:
                conn = urllib2.urlopen(self._url)
                page = Page(conn.geturl(), conn.read())
                downloaded = True
            except:
                print sys.exc_info()[1]
                sys.stdout.flush()
                download_counter = download_counter + 1
        return page


class Page:
    _url = None
    _content = None

    def __init__(self, url, content):
        self._url = url
        self._content = content

    def geturl(self):
        return self._url

    def getcontent(self):
        return self._content


reload(sys)
sys.setdefaultencoding('utf-8')

script_path = sys.path[0]
os.chdir(script_path)

csv = open(script_path + "/results.csv", 'a')

counter = 0

crawler = PageCrawler("http://aplikace.policie.cz/patrani-vozidla/Detail.aspx?id=${paging}", counter, 1)

for page in crawler:
    bs = BeautifulSoup(page.getcontent())
    rows = bs.find('table', {'id':'searchTableResults'}).findAll('span')
    found = False

    info = dict({"id":"", "Druh":"", "Vyrobce":"", "Typ":"", "Barva":"", "SPZ":"", "MPZ":"", "VIN":"", "Motor":"", "RokVyroby":"", "Nahlaseno":""})
    for row in rows:
        if(row.string is not None):
            info[row['id'].replace("ctl00_Application_lbl", "")] = row.string
            found = True
    if(found):
        info["id"] = str(counter)
        line = "|".join(info.values())
        csv.write(line + "\n")
        print line
        print "--------"
    counter = counter + 1
   

