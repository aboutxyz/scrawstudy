#coding:utf-8

class mySqlite(object):

    def init(self, path):
        try:
            self.conn = sqlite.connect(path) #连接sqlite
            self.cur = self.conn.cursor()  #cursor是一个记录游标，用于一行一行迭代的访问查询返回的结果
        except Exception, e:
            pass


    def create(self, table):
        '''创建table，我这里创建包含2个段 ID（数字型，自增长），Data（char 128字符）'''
        try:
            self.cur.execute("CREATE TABLE IF NOT EXISTS %s(Id INTEGER PRIMARY KEY AUTOINCREMENT, Data VARCHAR(40))"% table)
            self.done()
        except sqlite.Error ,e: #异常记录日志并且做事务回滚,以下相同
            self.conn.rollback()

    def insert(self, table, data):
        '''插入数据，指定表名，设置data的数据'''
        try:
            self.cur.execute("INSERT INTO %s(Data) VALUES('%s')" % (table,data))
            self.done()
        except sqlite.Error ,e:
            self.conn.rollback()

    def done(self):
        '''事务提交'''
        self.conn.commit()

    def close(self):
        '''关闭连接'''
        self.cur.close()
        self.conn.close()