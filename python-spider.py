# coding:utf-8
'''
test doc
'''

import sys
import time
import lxml
from lxml import etree
import requests
import urllib2
import urlparse
from threading import Thread, Lock
from queue import Queue
from bs4 import BeautifulSoup


seen_urls = set(['/'])
lock = Lock()


class Fetch(Thread):
    def __init__(self, tasks, *kwargs):
        Thread.__init__(self, kwargs=kwargs)
        self.tasks = tasks
        self.url = None
        self.depth = None
        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                (self.url, self.depth) = self.tasks.get()
                print self.url
            except:
                pass

            if self.depth > 0:
                try:
                    self.depth-=1
                    s = requests.session()
                    responseurl = s.get("http://localhost:3000/" + self.url, timeout=0.01)
                    responseurl.encoding = "utf-8"
                except:
                    pass
                lock.acquire()
                links = self.parse(self, self.url, responseurl)
                for link in links.difference(seen_urls):
                    self.tasks.put((link, self.depth))
                seen_urls.update(links)
                lock.release()
                self.tasks.task_done()



    @staticmethod
    def parse(self, fetched_url, responseurl):
        #urls = set()
        seturl = set()
        try:
            selector = etree.HTML(responseurl.content)
            urls = set(selector.xpath('//a/@href'))
        except KeyError:
            pass
        # soup = BeautifulSoup(responseurl.text, "lxml")
        # try:
        #     urls = set(x['href'] for x in soup.findAll('a'))
        # except KeyError:
        #     pass
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



class ThreadPool:
    def __init__(self, num_threads):
        self.tasks = Queue()
        for _ in range(num_threads):
            Fetch(self.tasks)

    def add_task(self, job):
        self.tasks.put(job)

    def wait_completion(self):
        self.tasks.join()


def main():
    start = time.time()
    pool = ThreadPool(4)
    pool.add_task(("/", 1))
    pool.wait_completion()
    print('{} URLs fetched in {:.1f} seconds'.format(len(seen_urls), time.time() - start))


if __name__ == '__main__':
    main()
