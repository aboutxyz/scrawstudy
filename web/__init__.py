# -*- coding:utf-8 -*-
import sys
import requests,json
from requests import get
from flask import Flask, render_template,request,session

app = Flask(__name__)
app.secret_key = 'forget it you can never guess'
list=[]

@app.route('/',methods=["GET","POST"])
def index():
    return render_template('index.html')

# @app.route('/page/<int:page>',methods=["GET","POST"])
# def abc(page):
    # list=[]
    # perpage=20
    # startat=page*perpage-20
    # db = MySQLdb.connect(host='127.0.0.1',user='root',passwd='900502',db='t66y',port=3306,charset='utf8')
    # cursor=db.cursor()
    # cursor.execute('select ID,TITLE,LINK,AUTHOR,TIME From t66y limit %s, %s;', (startat,perpage))
    # data =cursor.fetchall()
    # list.extend(data)
    # db.close()
    # return render_template('index.html',list=list,page=page)

if __name__ == '__main__':
    app.run()
		



