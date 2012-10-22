import MySQLdb

class DB:
    """ This is mbasically a mysql_ping() hack, because MySQLdb unhelpfully lacks basic keepalive support """

    conn = None

    def connect(self):
        #global conn
        self.conn = MySQLdb.connect(host = 'db.somehost.com',
                                    user = 'dcorbe',
                                    passwd = 'xxXXxx',
                                    db = 'mlm')
        #conn = self.conn
        self.conn.autocommit(True)

    def cursor(self):
        if self.conn:
            self.conn.ping(True)
        try:
            return self.conn.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            return self.conn.cursor()
        

    def getInstance():
        global conn
        
        if conn == None:
            conn = DB()
            
        return conn
