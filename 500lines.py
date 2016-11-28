# coding:utf-8

import Queue
import threading
from threading import Thread, Lock
import urlparse
import socket
import re
import time

seen_urls = set(['/'])
lock = Lock()

class Fetcher(object):
    def __init__(self, url, app):
        self.tp = app
        self.url = url

    def run(self, url):
        while True:
            print(url)
            sock = socket.socket()
            sock.connect(('localhost', 3000))
            get = 'GET {} HTTP/1.0\r\nHost: localhost\r\n\r\n'.format(url)
            sock.send(get.encode('ascii'))
            response = b''
            chunk = sock.recv(4096)
            while chunk:
                response += chunk
                chunk = sock.recv(4096)

            links = self.parse_links(url, response)

            for link in links.difference(seen_urls):
                seen_urls.update(links)

        if not response:
            print('error: {}'.format(seen_urls))
            return set()
        if not self._is_html(response):
            return set()
        urls = set(re.findall(r'''(?i)href=["']?([^\s"'<>]+)''',
                              self.body(response)))

        links = set()
        for url in urls:
            normalized = urlparse.urljoin(seen_urls, url)
            parts = urlparse.urlparse(normalized)
            if parts.scheme not in ('', 'http', 'https'):
                continue
            host, port = parts.hostname, parts.port
            if host and host.lower() not in ('localhost'):
                continue
            defragmented, frag = urlparse.urldefrag(parts.path)
            links.add(defragmented)
        for link in links:
            tp.add_job(self.run,link)
        return links

    def body(self, response):
        body = response.split(b'\r\n\r\n', 1)[1]
        return body.decode('utf-8')

    def _is_html(self, response):
        head, body = response.split(b'\r\n\r\n', 1)
        headers = dict(h.split(': ') for h in head.decode().split('\r\n')[1:])
        return headers.get('Content-Type', '').startswith('text/html')


    def work(self):
        self.tp.add_job(self.run)
        self.tp.wait_for_complete()  # 等待线程池完成

class MyThread(threading.Thread):

    def __init__(self, workQueue, *kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.setDaemon(True)  #设置deamon,表示主线程死掉,子线程不跟随死掉
        self.workQueue = workQueue
        self.start() #初始化直接启动线程

    def run(self):
        '''重载run方法'''
        while True:
            try:
                lock.acquire()   #线程安全上锁
                callable, args = self.workQueue.get(timeout=self.timeout) #从工作队列中获取一个任务
                res = callable(args)  #执行的任务
                lock.release()  #执行完,释放锁
            except Queue.Empty: #任务队列空的时候结束此线程
                break
            except Exception, e:
                # myLogger(self.logger, self.loglevel, e, True)
                return -1
class ThreadPool(object):

    def __init__(self, num_of_threads):
         self.workQueue = Queue.Queue()
         self.threads = []
         self.createThreadPool(num_of_threads)

    def createThreadPool(self, num_of_threads):
         for i in range(num_of_threads):
             thread = MyThread(self.workQueue)
             self.threads.append(thread)

    def wait_for_complete(self):
         '''等待所有线程完成'''
         while len(self.threads):
             thread = self.threads.pop()
         if thread.isAlive():  #判断线程是否还存活来决定是否调用join
             thread.join()

    def add_job( self, callable, *args):
        '''增加任务,放到队列里面'''
        self.workQueue.put((callable, args))


if __name__ == '__main__':
    start = time.time()
    tp = ThreadPool(4)
    crawler = Fetcher( tp)
    crawler.work()
    print('{} URLs fetched in {:.1f} seconds'.format(len(seen_urls),time.time() - start))