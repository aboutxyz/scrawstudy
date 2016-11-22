# coding:utf-8
import Queue
import threading
import sys


lock = threading.Lock()


class Mythread(threading.Thread):
    def __init__(self,tasks):
        Tread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                url = self.tasks.get()
                print url
                lock.acquire()
                lock.release()
                self.tasks.task_done()
            except Exception, e:
                pass


class Threadpool:
    def __init__(self,num_threads):
        self.tasks = Queue()
        for _ in range(num_threads):
            Mythread(self.tasks)

    def add_task(self,url):
        self.tasks.put(url)

    def wait_completion(self):
        self.task.join()


