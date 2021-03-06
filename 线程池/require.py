'''
使用python编写一个网站爬虫程序，支持参数如下：

spider.py -u url -d deep -f logfile -l loglevel(1-5)  --testself -thread number --dbfile  filepath  --key=”HTML5”

 

参数说明：

-u 指定爬虫开始地址

-d 指定爬虫深度

--thread 指定线程池大小，多线程爬取页面，可选参数，默认10

--dbfile 存放结果数据到指定的数据库（sqlite）文件中

--key 页面内的关键词，获取满足该关键词的网页，可选参数，默认为所有页面

-l 日志记录文件记录详细程度，数字越大记录越详细，可选参数，默认spider.log

--testself 程序自测，可选参数

 

功能描述：

1、指定网站爬取指定深度的页面，将包含指定关键词的页面内容存放到sqlite3数据库文件中

2、程序每隔10秒在屏幕上打印进度信息

3、支持线程池机制，并发爬取网页

4、代码需要详尽的注释，自己需要深刻理解该程序所涉及到的各类知识点

5、需要自己实现线程池

 

提示1：使用re  urllib/urllib2  beautifulsoup/lxml2  threading optparse Queue  sqlite3 logger  doctest等模块

提示2：注意是“线程池”而不仅仅是多线程

提示3：爬取sina.com.cn两级深度要能正常结束

 

建议程序可分阶段，逐步完成编写，例如：

版本1:Spider1.py -u url -d deep

版本2：Spider3.py -u url -d deep -f logfile -l loglevel(1-5)  --testself

版本3：Spider3.py -u url -d deep -f logfile -l loglevel(1-5)  --testself -thread number

版本4：剩下所有功能

 

加入知道创宇，如果你是WEB开发极客，需要完成一个简单论坛。
数据库使用MongoDB 、服务端应用使用Node.js 或 Python + Django 、前端使用 JQuery + Bootstrap Twitter。
论坛功能包括：
1. 用户自己注册、密码修改与找回
2. 无刷新发帖、回帖
3. 权限管理，只有自己发的贴自己才能删除
4. 文章列表支持分页显示
这应该不会有什么难度，如果你完成了，请尽快联系我们（yang@scanv.com）。因为你正是我们需要的人！

此笔试题长期有效:)
'''