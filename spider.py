#coding=utf-8

'''
This script is used to crawl analyzing web!

The Feature:
1 可以指定抓取的深度
2 将抓取到的关键字数据存放在sqlite
3 使用logging记录日志
4 并发线程池

Required dependencies:
1 chardet #分析抓取页面的字符集
sudo easy_install chardet

Usage:
spider.py -u url -d deep -f logfile -l loglevel(1-5)  -testself -thread number -dbfile  filepath  -key="HTML5"

Writer: Dongweiming
Date: 2012.10.22
'''

import urllib2
import Queue
import sys
import traceback
import threading
import re
import datetime
import lxml
import chardet
import logging
import logging.handlers
from time import sleep
from urlparse import urlparse
from lxml import etree
from optparse import OptionParser

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite



lock = threading.Lock() #设置线程锁
LOGGER = logging.getLogger('Crawler') #设置logging模块的前缀
LEVELS={   #日志级别
        1:'CRITICAL',
        2:'ERROR',
        3:'WARNING',
        4:'INFO',
        5:'DEBUG',#数字越大记录越详细
        }
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s') #自定义日志格式

class mySqlite(object):

    def init(self, path, logger, level):
        '''初始化数据库连接.

           >>> from sqlite3 import dbapi2 as sqlite
           >>> conn = sqlite.connect('testdb')
        '''
        try:
            self.conn = sqlite.connect(path) #连接sqlite
            self.cur = self.conn.cursor()  #cursor是一个记录游标，用于一行一行迭代的访问查询返回的结果
        except Exception, e:
            myLogger(logger, self.loglevel, e, True)
            return -1

        self.logger = logger
        self.loglevel = level

    def create(self, table):
        '''创建table，我这里创建包含2个段 ID（数字型，自增长），Data（char 128字符）'''
        try:
            self.cur.execute("CREATE TABLE IF NOT EXISTS %s(Id INTEGER PRIMARY KEY AUTOINCREMENT, Data VARCHAR(40))"% table)
            self.done()
        except sqlite.Error ,e: #异常记录日志并且做事务回滚,以下相同
            myLogger(self.logger, self.loglevel, e, True)
            self.conn.rollback()
        if self.loglevel >3: #设置在日志级别较高才记录,这样级别高的详细
                myLogger(self.logger, self.loglevel, '创建表%s' % table)

    def insert(self, table, data):
        '''插入数据，指定表名，设置data的数据'''
        try:
            self.cur.execute("INSERT INTO %s(Data) VALUES('%s')" % (table,data))
            self.done()
        except sqlite.Error ,e:
            myLogger(self.logger, self.loglevel, e, True)
            self.conn.rollback()
        else:
            if self.loglevel >4:
                myLogger(self.logger, self.loglevel, '插入数据成功')

    def done(self):
        '''事务提交'''
        self.conn.commit()

    def close(self):
        '''关闭连接'''
        self.cur.close()
        self.conn.close()
        if self.loglevel >3:
            myLogger(self.logger, self.loglevel, '关闭sqlite操作')


class Crawler(object):

    def init(self, args, app, table, logger):
        self.deep = args.depth  #指定网页的抓取深度
        self.url = args.urlpth #指定网站地址
        self.key = args.key #要搜索的关键字
        self.logfile = args.logfile #日志文件路径和名字
        self.loglevel = args.loglevel #日志级别
        self.dbpth = args.dbpth #指定sqlite数据文件路径和名字
        self.tp = app #连接池回调实例
        self.table = table #每次请求的table不同
        self.logger = logger #logging模块实例
        self.visitedUrl = [] #抓取的网页放入列表,防止重复抓取

    def _hasCrawler(self, url):
        '''判断是否已经抓取过这个页面'''
        return (True if url in self.visitedUrl else False)

    def getPageSource(self, url, key, deep):
        ''' 抓取页面,分析,入库.
        '''
        headers = {  #设计一个用户代理,更好防止被认为是爬虫
            'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; \
            rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6' }
        #if  urlparse(url).scheme == 'https':
           #pass
        if self._hasCrawler(url): #发现重复直接return
            return
        else:
            self.visitedUrl.append(url) #发现新地址假如到这个列表
        try:
            request = urllib2.Request(url = url, headers = headers) #创建一个访问请求,指定url,并且把访问请求保存在request
            result = urllib2.urlopen(request).read() #打开这个请求,并保存读取数据
        except urllib2.HTTPError, e:  #触发http异常记录日志并返回
            myLogger(self.logger, self.loglevel, e, True)
            return -1
        try:
            encoding = chardet.detect(result)['encoding'] #判断页面的编码
            if encoding.lower() == 'gb2312':
                encoding = 'gbk'  #今天我抓取新浪是gb2312,但是其中有个'蔡旻佑'不能被识别,所以用gbk去解码gb2312的页面
            if encoding.lower() != 'utf-8': #发现不是默认编码就用应该的类型解码
                result = result.decode(encoding)
        except Exception, e:
            myLogger(self.logger, self.loglevel, e, True)
            return -1
        else:
            if self.loglevel >3:
                myLogger(self.logger, self.loglevel, '抓取网页 %s 成功' % url)
        try:
            self._xpath(url, result, ['a'], unicode(key, 'utf8'), deep) #分析页面中的连接地址,以及它的内容
            self._xpath(url, result, ['title', 'p', 'li', 'div'], unicode(key, "utf8"), deep) #分析这几个标签的内容
        except TypeError: #对编码类型异常处理,有些深度页面和主页的编码不同
            self._xpath(url, result, ['a'], key, deep)
            self._xpath(url, result, ['title', 'p', 'li', 'div'], key, deep)
        except Exception, e:
            myLogger(self.logger, self.loglevel, e, True)
            return -1
        else:
            if self.loglevel >3:
                myLogger(self.logger, self.loglevel, '分析网页 %s 成功' % url)
        return True

    def _xpath(self, weburl, data, xpath, key, deep):

        sq = mySqlite(self.dbpth, self.logger, self.loglevel)
        page = etree.HTML(data)
        for i in xpath:
            hrefs = page.xpath(u"//%s" % i) #根据xpath标签
            if deep >1:
                for href in hrefs:
                    url = href.attrib.get('href','')
                    if not url.startswith('java') and not  \
                        url.startswith('mailto'):  #过滤javascript和发送邮件的链接
                            self.tp.add_job(self.getPageSource,url, key, deep-1) #递归调用,直到符合的深度
            for href in hrefs:
                value = href.text  #抓取相应标签的内容
                if value:
                    m = re.compile(r'.%s.' % key).match(value) #根据key匹配相应内容
                    if m:
                        sq.insert(self.table, m.group().strip()) #将匹配的数据插入到sqlite
        sq.close()

    def work(self):
        '''主方法调用.

        >>> import datetime
        >>> logger = configLogger('test.log')
        >>> time = datetime.datetime.now().strftime("%m%d%H%M%S")
        >>> sq = mySqlite('test.db', logger, 1)
        >>> table = 'd' + str(time)
        >>> sq.create(table)
        >>> tp = ThreadPool(5)
        >>> def t():pass
        >>> t.depth=1
        >>> t.urlpth='http://www.baidu.com'
        >>> t.logfile = 'test.log'
        >>> t.loglevel = 1
        >>> t.dbpth = 'test.db'
        >>> t.key = 'test'
        >>> d = Crawler(t, tp, table, logger)
        >>> d.getPageSource(t.urlpth, t.key, t.depth)
        True
        '''
        if not self.url.startswith('http://'): #支持用户直接写域名,当然也支持带前缀
            self.url = 'http://' + self.url
        self.tp.add_job(self.getPageSource, self.url, self.key, self.deep)
        self.tp.wait_for_complete() #等待线程池完成


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


def configLogger(logfile):
    '''配置日志文件和记录等级'''
    try:
        handler = logging.handlers.RotatingFileHandler(logfile,
                                                       maxBytes=10240000, #文件最大字节数
                                                       backupCount=5, #会轮转5个文件，共6个
                                                        )
    except IOError, e:
        print e
        return -1
    else:
        handler.setFormatter(formatter)  #设置日志格式
        LOGGER.addHandler(handler) #增加处理器
        logging.basicConfig(level=logging.NOTSET) #设置,不打印小于4级别的日志
    return LOGGER #返回logging实例

def myLogger(logger, lv, mes, err=False):
    '''记录日志函数'''
    getattr(logger, LEVELS.get(lv, 'WARNING').lower())(mes)
    if err: #当发现是错误日志,还会记录错误的堆栈信息
        getattr(logger, LEVELS.get(lv, 'WARNING').lower())(traceback.format_exc())

def parse():
    parser = OptionParser(
                  description="This script is used to crawl analyzing web!")
    parser.add_option("-u", "--url", dest="urlpth", action="store",
                  help="Path you want to fetch", metavar="www.sina.com.cn")
    parser.add_option("-d", "--deep", dest="depth", action="store",type="int",
                  help="Url path's deep, default 1", default=1)
    parser.add_option("-k", "--key", dest="key", action="store",
                  help="You want to query keywords, For example 'test'")
    parser.add_option("-f", "--file", dest="logfile", action="store",
                  help="Record log file path and name, default spider.log",
                  default='spider.log')
    parser.add_option("-l", "--level", dest="loglevel", action = "store",
                  type="int",help="Log file level, default 1(CRITICAL)",
                  default=1)
    parser.add_option("-t", "--thread", dest="thread", action="store",
                  type="int",help="Specify the thread pool, default 10",
                  default=10)
    parser.add_option("-q", "--dbfile", dest="dbpth", action="store",
                  help="Specify the the sqlite file directory and name, \
                  default  test.db", metavar='test.db')
    parser.add_option("-s", "--testself", dest="testself", action="store_true",
                  help="Test myself", default=False)
    (options, args) = parser.parse_args()
    return options

def main():
    '''主函数'''

    options = parse()
    if options.testself: #如果testself,执行doctest
        import doctest
        print doctest.testmod()
        return
    if not options.urlpth or not options.key or not options.dbpth: #判断必选项是否存在
        print 'Need to specify the parameters option "-u " or "-k" or "-q"!'
        return
    if '-h' in sys.argv  or '--help' in sys.argv:  #选择帮助信息,打印doc
        print __doc__

    logger = configLogger(options.logfile) #实例化日志调用
    time = datetime.datetime.now().strftime("%m%d%H%M%S") #每次请求都会根据时间创建table
    tp = ThreadPool(options.thread)
    sq = mySqlite(options.dbpth, logger, options.loglevel)
    table = 'd' + str(time)
    sq.create(table) #创建table
    sq.close()
    crawler = Crawler(options, tp, table, logger)
    crawler.work()  #主方法

if __name__ == "__main__":
    main()