# -*- coding: utf-8 -*-

import sqlite3
import os
import threading
import PriceParser
import sys
import time


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class DbController(object):
    """Database search and update.
    Usage:
        db = DbController()
        db.initDb()
        db. ...
    """

    dbFilename = "soda.db"
    conn = None
    dbInitSql = '''
        CREATE TABLE IF NOT EXISTS Updates(q TEXT, time TEXT);
        CREATE TABLE IF NOT EXISTS Items(id TEXT, site TEXT, url TEXT, price FLOAT, img TEXT, title TEXT, q TEXT);
        CREATE TABLE IF NOT EXISTS Sessions(sid TEXT, data TEXT);
        '''
    maxFetchPages = 5
    minDelayBetweenFetches = 10
    waitTimeForFetch = 3

    def __init__(self, dbFilename):
        """Initialize the database with given filename.
        If no such file exists, a new one will be created.
        """
        reload(sys)
        sys.setdefaultencoding('utf8')
        super(DbController, self).__init__()
        self.dbFilename = dbFilename
        self.connDb()

    # connection manage

    def connDb(self):
        self.conn = sqlite3.connect(self.dbFilename)
        self.conn.row_factory = sqlite3.Row
        self.conn.text_factory = str
        print '[connDb]Connection established'

    def closeDb(self):
        self.conn.close()
        self.conn = None
        print '[closeDb]Connection flushed'

    def initDb(self):
        """Initialize sqlite database, flush anything already exists.
        return:
            a connection
        """
        self.deleteDb()
        self.connDb()
        self.conn.executescript(self.dbInitSql)
        print '[initDb]Initialize done'

    def deleteDb(self):
        """Delete the whole database file(with extension of .db)
        """
        self.closeDb()
        if not os.path.isfile(self.dbFilename):
            print '[deleteDb]No such file named %s' % self.dbFilename
            return
        if not os.path.splitext(self.dbFilename)[1] == '.db':
            print '[ERROR][deleteDb]%s is not a proper database filename' % self.dbFilename
            return
        os.remove(self.dbFilename)
        print '[deleteDb]Database: %s deleted' % self.dbFilename

    # data manage

    def findTuple(self, select, table, where):
        """Find tuple in table
        args:
            select - string, maybe "*"
            table - string, table name
            where - list of strings, e.g. "sid LIKE _s_"
        return:
            list of results
        """
        sql = "SELECT %s FROM %s WHERE %s;" % (select, table, ' AND '.join(where))
        print "[findTuple]SQL=%s" % sql
        cur = self.conn.execute(sql)
        return cur.fetchall()

    def insertTuples(self, table, values):
        """Insert values into table.
        If the table has only one key USE (VAL,) INSTEAD OF (VAL)!!!
        args:
            conn - connection to db
            table - string, table name
            values - list of tuple(val, val, ...)
        return:
            succ or not
        """
        cur = self.conn.cursor()
        placeholders = "(%s)" % ("?,"*(values[0].__len__()-1) + "?")
        sql = "INSERT INTO %s VALUES %s" % (table, placeholders)
        cur.executemany(sql, values)
        self.conn.commit()
        print '[insertTuples]insert into %s done' % table

    # request handler

    def queryUpdate(self, q):
        """return dict(q, time) or None(if not found)"""
        result = self.findTuple("*", "Updates", ["q = '%s'" % q])
        uptime = result and result[0][1] or "0"
        return {"q": q, "time": uptime}

    def querySearch(self, q, site, sid, page):
        """return a list of results(q, site, sid, page)"""
        """TODO"""
        sessionRes = self.findTuple("data", "Sessions", ["sid = '%s'" % sid])
        print "### 1",
        print sessionRes
        self.fetchAndStore(q, site)

        if not sessionRes:
            itemsRes = self.findTuple("*", "Items", ["q = '%s'" % q, "site = '%s'" % site])
            print "### 2",
            print itemsRes
            if not itemsRes:
                time.sleep(self.waitTimeForFetch)
                itemsRes = self.findTuple("*", "Items", ["q = '%s'" % q, "site = '%s'" % site])
                print "### 3",
                print itemsRes
            # write itemsres to sessions
            sessionRes = self.findTuple("data", "Sessions", ["sid = '%s'" % sid])
            print "### 4",
            print sessionRes
        # fine. result in sessionres.
        # paging, paging
        return sessionRes

    def renewUpdate(self, q):
        """renew update time for keyword q"""
        sql = "DELETE FROM Updates WHERE q = '%s';" % q
        self.conn.execute(sql)
        self.conn.commit()

        currentTime = time.time()
        self.insertTuples("Updates", [(q, currentTime)])
        print "[renewUpdate]Uptime of %s is %s now" % (q, currentTime)

    # data fetch

    @threaded
    def fetchAndStore(self, q, site='All'):
        """Fetch data using PriceParser, store them into database
        """
        ''' todo fetch each site!'''
        # get controller
        controller = DbController(self.dbFilename)
        updateTime = int(float(controller.queryUpdate(q)["time"]))
        currentTime = int(float(time.time()))
        if currentTime-updateTime < self.minDelayBetweenFetches:
            print "[fetchAndStore]Time from last query is %s, skip" % q
            pass
        else:
            parser = PriceParser.PriceParser()
            for page in range(1, self.maxFetchPages + 1):
                results = parser.parseEverything(q, page, site)
                if results.__len__() > 0:
                    controller.insertTuples("Items", [(item['pid'], item['site'], item['url'], item['price'], item['img'], item['title'], q) for item in results])
            controller.renewUpdate(q)
            print "[fetchAndStore]Query %s from %s done" % (q, site)

        controller.closeDb()
