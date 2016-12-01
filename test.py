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
seturl = set()

def parse(fetched_url):
    try:
        s = requests.session()
        responseurl = s.get("http://localhost:3000/" + fetched_url, timeout=0.1)
        responseurl.encoding = "utf-8"
    except requests.RequestException as e:
        pass
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
    seen_urls.update(seturl)
    return seen_urls


with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    future_to_url = executor.submit(parse, '/')
    for i in range(3):
        for url in list(future_to_url.result()):
            future_to_url = executor.submit(parse, url)
    print len(future_to_url.result())

