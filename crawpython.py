# coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
ua = UserAgent()


class Crawpython(object):

    def __init__(self):
        self.visitedUrl = []

    def _hascraw(self,url):
        return (True if url in self.visitedUrl else False)

    def parsepage(self,url):
        headers = {
            'User-Agent': ua.random,
        }

        if self._hascraw(url):
            return
        else:
            self.visitedUrl.append(url)
        try:
            response = requests.get("127.0.0.1:3000",headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception,e:
            return -1