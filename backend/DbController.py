# -*- coding: utf-8 -*-
import sqlite3
import os
import threading
import PriceParser
import sys
import time
import json


def threaded(fn):
    """Decorator, makes a method run in separate thread
    """
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


def dictFactory(cursor, row):
    """[{'key': value, 'key': value}, {...}, ...]"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DbController(object):
    """Database search and update.
    Usage:
        db = DbController(dbFileName)
        db.initDb()
        db. ...()
    """

    # Config

    dbFilename = "soda.db"
    """Sqlite database filename. Default: 'soda.db'"""
    maxFetchPages = 5
    """Maximum pages fetched from shopping sites in a query. Default: 5"""
    minDelayBetweenFetches = 30
    """Minimum delay time(sec) between two queries with same keyword. Default: 30"""
    waitTimeForFetch = 3
    """Time(sec) waiting for items to be fetched and stored into database. Default: 3"""
    itemsPerPage = 24
    """Maximum number of items in a result page. Default: 24"""

    dbInitSql = '''
        CREATE TABLE IF NOT EXISTS
            Updates(q    TEXT PRIMARY KEY,
                    time TEXT);

        CREATE TABLE IF NOT EXISTS
            Items(q     TEXT NOT NULL,
                  id    TEXT NOT NULL,
                  site  TEXT,
                  url   TEXT,
                  price FLOAT,
                  img   TEXT,
                  title TEXT,
                  PRIMARY KEY(q, id));

        CREATE TABLE IF NOT EXISTS
            Sessions(sid TEXT PRIMARY KEY,
                     data TEXT);

        CREATE INDEX Items_index ON
            Items(q, id);
        '''
    """SQL for initialize database"""
    conn = None
    """Connection object to database"""

    def __init__(self, dbFilename=None):
        """Connect the database with given filename.
        If no such file exists, a new one will be created.
        """
        super(DbController, self).__init__()
        reload(sys)
        sys.setdefaultencoding('utf8')
        if dbFilename:
            self.dbFilename = dbFilename
        self.connDb()

    # Connection and db file manage

    def connDb(self):
        self.conn = sqlite3.connect(self.dbFilename)
        self.conn.row_factory = dictFactory
        self.conn.text_factory = str
        print '[connDb]Connection established'

    def closeDb(self):
        self.conn.close()
        self.conn = None
        print '[closeDb]Connection flushed'

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
        print '[deleteDb]Deleted database: %s' % self.dbFilename

    def initDb(self):
        """Initialize and connect to database(clear anything exists)
        """
        self.deleteDb()
        self.connDb()
        self.conn.executescript(self.dbInitSql)
        print '[initDb]Initialize done'

    # Data manage

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

    def insertTuples(self, table, values, replace=False):
        """Insert values into table(will commit).
        If the table has only one key USE (VAL,) INSTEAD OF (VAL)!!!
        args:
            table - string, table name
            values - list of tuple, e.g. [(val, ...), (val, ...)]
            replace - boolean, if True: execute 'insert or replace' instead of 'insert'
        """
        cur = self.conn.cursor()
        placeholders = "(%s)" % ("?,"*(values[0].__len__()-1) + "?")
        sql = "INSERT %s INTO %s VALUES %s" % (replace and "OR REPLACE" or "", table, placeholders)
        cur.executemany(sql, values)
        self.conn.commit()
        print '[insertTuples]insert%s into %s done' % (replace and " and replace" or "", table)

    # Request handler

    def refreshUptime(self, q):
        """Refresh updatetime for keyword q"""
        currentTime = time.time()
        self.insertTuples("Updates", [(q, currentTime)], replace=True)
        print "[refreshUptime]Uptime of %s is %s now" % (q, currentTime)

    def queryUpdate(self, q):
        """Returns a dict including last update time of keyword q in db"""
        result = self.findTuple("*", "Updates", ["q = '%s'" % q])
        uptime = result and result[0]["time"] or "0"
        return {"q": q,
                "updateTime": uptime}

    def querySearch(self, q, site, sid, page):
        """Returns a dict including everything for showing result page"""
        page = int(page)
        site = site.capitalize()

        # Commit a fetch from websites in separate thread
        self.fetchAndStore(q, site)
        print "[querySearch]Sent fetchAndStore(%s, %s)" % (q, site)

        # Try to find existing result from Sessions
        fromSessions = self.findTuple("data", "Sessions", ["sid = '%s'" % sid])
        items = fromSessions and json.loads(fromSessions[0]["data"]) or None

        if not items:
            # Try to search someing corresponding 'q' from Items
            items = self.findTuple("*", "Items", ["q = '%s'" % q, "site = '%s'" % site])
            if not items:
                # Found nothing... Wait few seconds for fetchAndStore to fill some
                time.sleep(self.waitTimeForFetch)
                items = self.findTuple("*", "Items", ["q = '%s'" % q, "site = '%s'" % site])
            # Keep a new session
            self.insertTuples("Sessions", [(sid, json.dumps(items))], replace=True)

        # Paging
        pagedItems = items[(page-1)*self.itemsPerPage:page*self.itemsPerPage]
        print "[querySearch]Total %d items, paged from %d to %d" % (items.__len__(), (page-1)*self.itemsPerPage, (page)*self.itemsPerPage-1)
        return {"q": q,
                "site": site,
                "session": sid,
                "page": page,
                "count": pagedItems.__len__(),
                "totalPage": items.__len__()/self.itemsPerPage,
                "items": pagedItems}

    # Fetch from websites

    @threaded
    def fetchAndStore(self, q, site='All'):
        """Fetch data using PriceParser, then store them into database.
        Use another db connection than caller, due to limit of sqlite3 in multithreading
        TODO fetch each site/all site!
        """
        controller = DbController(self.dbFilename)
        updateTime = int(float(controller.queryUpdate(q)["updateTime"]))
        currentTime = int(float(time.time()))
        print "[fetchAndStore]Time from last query is %ds" % (currentTime-updateTime)
        if currentTime-updateTime < self.minDelayBetweenFetches:
            print "[fetchAndStore]skip"
        else:
            controller.refreshUptime(q)
            parser = PriceParser.PriceParser()
            itemCount = 0
            for page in range(1, self.maxFetchPages + 1):
                results = parser.parseEverything(q, page, site)
                if results.__len__() > 0:
                    controller.insertTuples("Items", [(q, item['pid'], item['site'], item['url'], item['price'], item['img'], item['title']) for item in results], replace=True)
                    itemCount += results.__len__()
            print "[fetchAndStore]Fetch %s from %s done. %d items." % (q, site, itemCount)
        controller.closeDb()
