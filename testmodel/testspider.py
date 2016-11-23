# coding:utf-8

from queue import Queue
from threading import Thread, Lock
import urlparse
import socket
import re
import time
from testthread import *

seen_urls = set(['/'])
lock = Lock()


class Fetcher(object):
    def __init__(self,app):
        self.pool = app
        self.url = "/"

    def run(url):
        sock = socket.socket()
        sock.connect(('localhost', 3000))
        request = 'GET {} HTTP/1.0\r\nHost: localhost\r\n\r\n'.format(url)
        sock.send(request.encode('ascii'))
        response = b''
        chunk = sock.recv(4096)
        while chunk:
            response += chunk
            chunk = sock.recv(4096)

        links = parse_links(response)
        seen_urls.update(links)
 

    def parse_links(self, fetched_url, response):
        if not response:
            print('error: {}'.format(fetched_url))
            return set()
        if not self._is_html(response):
            return set()
        urls = set(re.findall(r'''(?i)href=["']?([^\s"'<>]+)''',
                              self.body(response)))

        links = set()
        for url in urls:
            normalized = urlparse.urljoin(fetched_url, url)
            parts = urlparse.urlparse(normalized)
            if parts.scheme not in ('', 'http', 'https'):
                continue
            host, port = parts.hostname, parts.port
            if host and host.lower() not in ('localhost'):
                continue
            defragmented, frag = urlparse.urldefrag(parts.path)
            links.add(defragmented)

        return links

    def body(self, response):
        body = response.split(b'\r\n\r\n', 1)[1]
        return body.decode('utf-8')

    def _is_html(self, response):
        head, body = response.split(b'\r\n\r\n', 1)
        headers = dict(h.split(': ') for h in head.decode().split('\r\n')[1:])
        return headers.get('Content-Type', '').startswith('text/html')
        
    
    def work(self):
        self.pool.add_task(self.parse_links, self.url)
        self.pool.wait_completion() #等待线程池完成
        
        
def main():
    '''主函数'''    
    
    pool = ThreadPool(4)
    crawler = Fetcher(pool)
    crawler.work()
    
    
if __name__ == '__main__':
    start = time.time()
    main()
    print('{} URLs fetched in {:.1f} seconds'.format(len(seen_urls),time.time() - start))