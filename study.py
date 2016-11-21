#coding:utf-8


'''
document
'''
import Queue
import sys
import time,datetime
import traceback
import threading
import sqlite3
from models import mySqlite
from threadfunc import *



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
    parser.add_option("-u", "-url", dest="urlpth", action="store",
                  help="Path you want to fetch", metavar="www.sina.com.cn")
    parser.add_option("-d", "-deep", dest="depth", action="store",type="int",
                  help="Url path's deep, default 1", default=1)
    parser.add_option("-k", "-key", dest="key", action="store",
                  help="You want to query keywords, For example 'test'")
    parser.add_option("-f", "-file", dest="logfile", action="store",
                  help="Record log file path and name, default spider.log",
                  default='spider.log')
    parser.add_option("-l", "-level", dest="loglevel", action = "store",
                  type="int",help="Log file level, default 1(CRITICAL)",
                  default=1)
    parser.add_option("-t", "-thread", dest="thread", action="store",
                  type="int",help="Specify the thread pool, default 10",
                  default=10)
    parser.add_option("-q", "-dbfile", dest="dbpth", action="store",
                  help="Specify the the sqlite file directory and name, \
                  default  test.db", metavar='test.db')
    parser.add_option("-s", "-testself", dest="testself", action="store_true",
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
    if '-h' in sys.argv  or '-help' in sys.argv:  #选择帮助信息,打印doc
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

    
if __name__=='__main__':
    main()
