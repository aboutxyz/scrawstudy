# coding:utf-8

import threading
from queue import Queue

class MyThread(threading.Thread):
    def __init__(self, tasks,*kwargs):
        threading.Thread.__init__(self,kwargs=kwargs)        
        self.daemon = True
        self.tasks = tasks
        self.start()
        
    
    def run(self):
        while True:
            try:
                lock.acquire()   #线程安全上锁
                callable, args = self.tasks.get() #从工作队列中获取一个任务
                res = callable(args)  #执行的任务
                lock.release()  #执行完,释放锁
            except Exception, e:
                return -1



class ThreadPool(object):
    def __init__(self, num_threads):
        self.tasks = Queue()
        self.threads = []
        self.createThreadPool(num_threads)

    def createThreadPool(self, num_threads):
        for i in range(num_threads):
            thread = MyThread(self.tasks)
            self.threads.append(thread)

    def add_task(self,callable,*args):
        self.tasks.put((callable, args))

    def wait_completion(self):
        self.tasks.join()