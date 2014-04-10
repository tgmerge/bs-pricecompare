# -*- coding: utf-8 -*-

import sqlite3
import os
import threading
import PriceParser
import sys
import time
import json


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
    maxFetchPages = 5 # 5 default
    minDelayBetweenFetches = 30 # 10 default
    waitTimeForFetch = 3 # 3 default
    itemsPerPage = 10 # 20 default

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

    def dictFactory(self, cursor, row):
        """[{'key': value, 'key': value}, {...}, ...]"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def connDb(self):
        self.conn = sqlite3.connect(self.dbFilename)
        self.conn.row_factory = self.dictFactory
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

    def insertTuples(self, table, values, replace=False):
        """Insert values into table.
        If the table has only one key USE (VAL,) INSTEAD OF (VAL)!!!
        args:
            conn - connection to db
            table - string, table name
            values - list of tuple(val, val, ...)
        """
        cur = self.conn.cursor()
        placeholders = "(%s)" % ("?,"*(values[0].__len__()-1) + "?")
        sql = "INSERT %s INTO %s VALUES %s" % (replace and "OR REPLACE" or "", table, placeholders)
        cur.executemany(sql, values)
        self.conn.commit()
        print '[insertTuples]insert%s into %s done' % (replace and " and replace" or "", table)

    # request handler

    def queryUpdate(self, q):
        """return dict(q, time) or None(if not found)"""
        result = self.findTuple("*", "Updates", ["q = '%s'" % q])
        uptime = result and result[0]["time"] or "0"
        return {"q": q,
                "updateTime": uptime}

    def querySearch(self, q, site, sid, page):
        """return a list of results(q, site, sid, page)"""
        """TODO"""
        page = int(page)
        site = site.capitalize()

        self.fetchAndStore(q, site)
        print "[querySearch]Sent fetchAndStore(%s, %s)" % (q, site)

        print "[querySearch]Try to fetch from Sessions...",
        fromSessions = self.findTuple("data", "Sessions", ["sid = '%s'" % sid])
        items = fromSessions and json.loads(fromSessions[0]["data"]) or None
        print items and "OK" or "Failed"

        if not items:
            print "[querySearch]Try to fetch from Items...",
            items = self.findTuple("*", "Items", ["q = '%s'" % q, "site = '%s'" % site])
            print items and "OK" or "Failed"
            if not items:
                print "[querySearch]Waiting...",
                time.sleep(self.waitTimeForFetch)
                items = self.findTuple("*", "Items", ["q = '%s'" % q, "site = '%s'" % site])
                print items and "re-search OK" or "re-search Failed"
                self.insertTuples("Sessions", [(sid, json.dumps(items))], replace=True)

        pagedItems = items[(page-1)*self.itemsPerPage:page*self.itemsPerPage]
        print "[querySearch]Total %d items, paged from %d to %d" % (items.__len__(), (page-1)*self.itemsPerPage, (page)*self.itemsPerPage-1)
        return {"q": q,
                "site": site,
                "session": sid,
                "page": page,
                "count": pagedItems.__len__(),
                "totalPage": items.__len__()/self.itemsPerPage,
                "items": pagedItems}

    def renewUpdate(self, q):
        """renew update time for keyword q"""
        currentTime = time.time()
        self.insertTuples("Updates", [(q, currentTime)], replace=True)
        print "[renewUpdate]Uptime of %s is %s now" % (q, currentTime)

    # data fetch

    @threaded
    def fetchAndStore(self, q, site='All'):
        """Fetch data using PriceParser, store them into database
        """
        ''' todo fetch each site!'''
        # get controller
        controller = DbController(self.dbFilename)
        updateTime = int(float(controller.queryUpdate(q)["updateTime"]))
        currentTime = int(float(time.time()))
        print "[fetchAndStore]Time from last query is %d" % (currentTime-updateTime)
        if currentTime-updateTime < self.minDelayBetweenFetches:
            print "[fetchAndStore]skip"
            pass
        else:
            controller.renewUpdate(q)
            parser = PriceParser.PriceParser()
            for page in range(1, self.maxFetchPages + 1):
                results = parser.parseEverything(q, page, site)
                if results.__len__() > 0:
                    controller.insertTuples("Items", [(q, item['pid'], item['site'], item['url'], item['price'], item['img'], item['title']) for item in results], replace=True)
            print "[fetchAndStore]Query %s from %s done" % (q, site)

        controller.closeDb()
