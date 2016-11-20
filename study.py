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



class Crawler(object):

    def init(self, args, app, table, logger):
        self.url = args.urlpth #指定网站地址
        self.key = args.key #要搜索的关键字
        self.dbpth = args.dbpth #指定sqlite数据文件路径和名字
        self.tp = app #连接池回调实例
        self.table = table #每次请求的table不同
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
            return -1
        try:
            encoding = chardet.detect(result)['encoding'] #判断页面的编码
            if encoding.lower() == 'gb2312':
                encoding = 'gbk'  #今天我抓取新浪是gb2312,但是其中有个'蔡旻佑'不能被识别,所以用gbk去解码gb2312的页面
            if encoding.lower() != 'utf-8': #发现不是默认编码就用应该的类型解码
                result = result.decode(encoding)
        except Exception, e:
            return -1
        try:
            self._xpath(url, result, ['a'], unicode(key, 'utf8')) #分析页面中的连接地址,以及它的内容
            self._xpath(url, result, ['title', 'p', 'li', 'div'], unicode(key, "utf8")) #分析这几个标签的内容
        except TypeError: #对编码类型异常处理,有些深度页面和主页的编码不同
            self._xpath(url, result, ['a'], key)
            self._xpath(url, result, ['title', 'p', 'li', 'div'], key)
        except Exception, e:
            return -1
        return True

    def _xpath(self, weburl, data, xpath, key):

        sq = mySqlite(self.dbpth, self.logger, self.loglevel)
        page = etree.HTML(data)
        for i in xpath:
            hrefs = page.xpath(u"//%s" % i) #根据xpath标签
            if deep >1:
                for href in hrefs:
                    url = href.attrib.get('href','')
                    if not url.startswith('java') and not  \
                        url.startswith('mailto'):  #过滤javascript和发送邮件的链接
                            self.tp.add_job(self.getPageSource,url, key) #递归调用,直到符合的深度
            for href in hrefs:
                value = href.text  #抓取相应标签的内容
                if value:
                    m = re.compile(r'.%s.' % key).match(value) #根据key匹配相应内容
                    if m:
                        sq.insert(self.table, m.group().strip()) #将匹配的数据插入到sqlite
        sq.close()

    def work(self):
        if not self.url.startswith('http://'): #支持用户直接写域名,当然也支持带前缀
            self.url = 'http://' + self.url
        self.tp.add_job(self.getPageSource, self.url, self.key)
        self.tp.wait_for_complete() #等待线程池完成


        
def main():
    time = datetime.datetime.now().strftime("%m%d%H%M%S") #每次请求都会根据时间创建table
    tp = ThreadPool(thread)
    sq = mySqlite(dbpath)
    table = 'd' + str(time)
    sq.create(table) #创建table
    sq.close()
    crawler = Crawler(options, tp, table)
    crawler.work()  #主方法
    if '-h' in sys.argv  or '-help' in sys.argv:  #选择帮助信息,打印doc
        print __doc__

    
if __name__=='__main__':
    main()
