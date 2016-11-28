# coding:utf-8

import sys
import socket
import time
import lxml
import requests
import urlparse
from threading import Thread, Lock
from queue import Queue
from bs4 import BeautifulSoup

seen_urls = set(['/'])
lock = Lock()


class Fetch(object):
    def __init__(self):
        pass

    def run(self):
        while True:
            url = self.tasks.get()
            print(url)
            try:
                responseurl = requests.get("http://127.0.0.1:3000/" + url)
                responseurl.encoding = "utf-8"
            except:
                pass
            links = self.parse(self, url, responseurl)

            for link in links.difference(seen_urls):
                self.tasks.put(link)
            seen_urls.update(links)

    @staticmethod
    def parse(self, fetched_url, responseurl):
        urls = set()
        seturl = set()
        soup = BeautifulSoup(responseurl.text, "lxml")
        try:
            urls = set(x['href'] for x in soup.findAll('a'))
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



if __name__ == '__main__':
    start = time.time()

    print('{} URLs fetched in {:.1f} seconds'.format(len(seen_urls), time.time() - start))



