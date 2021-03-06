# coding:utf-8
"""
craw python document

"""

import sys
import time
import lxml
from lxml import etree
import requests
import urllib2
import urlparse
from threading import Thread, Lock
from queue import Queue
import getopt
from bs4 import BeautifulSoup
from optparse import OptionParser


seen_urls = set(['/'])
lock = Lock()


class Fetch(Thread):
    def __init__(self, tasks, *kwargs):
        Thread.__init__(self, kwargs=kwargs)
        self.tasks = tasks
        self.url = None
        self.depth = None
        self.responseurl = None
        self.daemon = True
        self.start()

    def run(self):
        while True:
            lock.acquire()
            try:
                (self.url, self.depth) = self.tasks.get()
                print self.url, self.depth
            except:
                pass
            if self.depth > 0:
                try:
                    self.depth -= 1
                    s = requests.session()
                    self.responseurl = s.get("http://localhost:3000/" + self.url, timeout=0.1)
                    self.responseurl.encoding = "utf-8"
                except requests.RequestException as e:
                    print "error of "+self.url, self.depth
                if self.responseurl is not None:
                    links = self.parse(self, self.url, self.responseurl)
                    for link in links.difference(seen_urls):
                        self.tasks.put((link, self.depth))
                    seen_urls.update(links)
            lock.release()
            self.tasks.task_done()



    @staticmethod
    def parse(self, fetched_url, responseurl):
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


def parse():
    parser = OptionParser(description=__doc__)
    parser.add_option("-d", "--depth",
                      action="store", type="int", dest="depth", default=1,
                      help="Url path's deep, default 1")
    (options, args) = parser.parse_args()
    return options


def main():
    options = parse()
    if options.depth is None:
        print 'Need to specify the parameters option "-d"!'
    start = time.time()
    pool = ThreadPool(4)
    pool.add_task(("/", int(options.depth)))
    pool.wait_completion()
    print('{} URLs fetched in {:.1f} seconds'.format(len(seen_urls), time.time() - start))

if __name__ == '__main__':
    # opts, args = getopt.getopt(sys.argv[1:], "d:h", ["depth=", "help"])
    # for k,v in opts:
    #     if k in ('-d', '-depth'):
    #         run(v)
    #     if k in ('-h', '-help'):
    #         print __doc__

    main()

