# coding:utf-8
"""
craw python document

"""

import sys
import time
import lxml
from lxml import etree
import requests
import urlparse
from optparse import OptionParser
import concurrent.futures

seen_urls = set(['/'])
class Fetch():
    def __init__(self, *kwargs):
        self.url = None
        self.responseurl = None

    def run(self, url):
        s = requests.session()
        self.responseurl = s.get("http://localhost:3000/" + self.url, timeout=0.1)
        self.responseurl.encoding = "utf-8"
        if self.responseurl is not None:
            links = self.parse(self, self.url, self.responseurl)
            for link in links.difference(seen_urls):
                self.tasks.put((link, self.depth))
            seen_urls.update(links)
        return seen_urls
            
            
    @staticmethod
    def parse(self, fetched_url, responseurl):
        seturl = set()
        try:
            selector = etree.HTML(responseurl.content)
            urls = set(selector.xpath('//a/@href'))
        except KeyError:
            pass
        for url in urls:
            normalized = urlparse.urljoin(fetched_url, url)
            parts = urlparse.urlparse(normalized)
            if parts.scheme not in ('', 'http', 'https'):
                continue
            host, port = parts.hostname, parts.port
            if host and host.lower() not in ('localhost'):
                continue
            defragmented, frag = urlparse.urldefrag(parts.path)
            seturl.add(defragmented)
        return seturl
    
    

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    result = executor.map(Fetch().run, seen_urls)
    for i in result:
        print i