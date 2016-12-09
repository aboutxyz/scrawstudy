# coding: utf-8
"""
craw python document

"""
import sys
import time
from lxml import etree
import requests
import urlparse
import logging
from optparse import OptionParser
import concurrent.futures

seen_urls = set(['/'])
seturl = set()

logger = logging.getLogger('parse_url')
LEVELS={
        1:'CRITICAL',
        2:'ERROR',
        3:'WARNING',
        4:'INFO',
        5:'DEBUG',
        }
logger.setLevel(logging.INFO)
handler1 = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler1.setFormatter(formatter)
logger.addHandler(handler1)
handler2 = logging.FileHandler('scraw.log')
# handler2.setLevel(logging.INFO)
handler2.setFormatter(formatter)
logger.addHandler(handler2)


def parse_url(fetched_url):
    try:
        s = requests.session()
        responseurl = s.get("http://localhost:3000/" + fetched_url, timeout=0.5)
        responseurl.encoding = "utf-8"
    except requests.RequestException as e:
        logger.info(u'连接时间错误')
        return -1
    try:
        selector = etree.HTML(responseurl.content)
        urls = set(selector.xpath('//a/@href'))
    except KeyError:
        pass
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
    diff = seturl-seen_urls
    seen_urls.update(diff)
    return (seen_urls, diff)


def parse():
    parser = OptionParser(description=__doc__)
    parser.add_option("-d", "--depth",
                      action="store", type="int", dest="depth", default=1,
                      help="Url path's deep, default 1")
    (options, args) = parser.parse_args()
    return options


def run(depth):
    if depth == 0:
        return -1
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_url = executor.submit(parse_url, '/')
            for i in range(depth-1):
                for url in list(future_to_url.result()[1]):
                    future_to_url = executor.submit(parse_url, url)
                    print str(i+1) + url
            for url in list(future_to_url.result()[1]):
                print str(depth) + url
        print len(seen_urls)
          
            

def main():
    options = parse()
    if options.depth is None:
        print 'Need to specify the parameters option "-d"!'
    else:
        run(options.depth)


if __name__ == '__main__':
    main()
