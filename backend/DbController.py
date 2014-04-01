import sqlite3

dbFilename = "soda.db"
dbInitSql = '''
    CREATE TABLE IF NOT EXISTS Updates(q TEXT, time INTEGER);
    CREATE TABLE IF NOT EXISTS Items(id TEXT, site TEXT, url TEXT, price FLOAT, img TEXT, title TEXT, q TEXT);
    CREATE TABLE IF NOT EXISTS Sessions(sid TEXT, data TEXT);'''

conn = None


def queryUpdate(q):
    '''
    findtuple(Updates, q=q)
    -> return JSON(time)
    '''


def querySearch(q, site, sid, page):
    '''

    if A = findtuple(Sessions, sid=sid) == None:
        if B = findtuple(Items, (q in title or q in q) and (site=site)) == None:
            fetch and parse from websites for a limited time
            write parse result to Items
            B = findtuple(Items, (q in title or q in q) and (site=site))
        write(Sessions, data from B)
    return data from Sessions from A {q, site, sid, page, [{site, img, url, price, title}, ...]
    '''


def findTuple(select, table, where):
    sql = "SELECT %s FROM %s WHERE %s" % (select, table, ' AND '.join(where))
    cur = conn.execute(sql)
    return cur.fetchAll()


def initDb(dbFilename, dbInitSql):
    '''Initialize sqlite database.
    Return:
        a connection
        '''
    conn = sqlite3.connect(dbFilename, row_factory=sqlite3.Row)
    conn.executescript(dbInitSql)
    return conn
