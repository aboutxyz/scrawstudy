#coding:utf-8
import threading
import Queue

class MyThread(threading.Thread):

    def init(self, workQueue, timeout=30, *kwargs):
        threading.Thread.init(self, kwargs=kwargs)
        self.timeout = timeout #线程在结束前等待任务队列多长时间
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
                myLogger(self.logger, self.loglevel, e, True)
                return -1


class ThreadPool(object):

    def init(self, num_of_threads):
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