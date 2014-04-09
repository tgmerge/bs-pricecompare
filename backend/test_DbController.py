# -*- coding: utf-8 -*-

import DbController as DC
from time import sleep

dataUpdates = [('dadiao1', 1),
               ('dadiao2', 2),
               ('dadiao3', 3),
               ]

dataItems = [('id1', 'site1', 'url1', 100.1, 'img1', 'title1', 'q1'),
             ('id2', 'site2', 'url2', 200.2, 'img2', 'title2', 'q2'),
             ('id3', 'site3', 'url3', 300.3, 'img3', 'title3', 'q3'),
             ('id4', 'site4', 'url4', 400.4, 'img4', 'title4', 'q4'),
             ]

dataSessions = [('sid1', 'data1'),
                ('sid2', 'data2'),
                ]

'''
db = DC.DbController('test.db')
db.initDb()
db.fetchAndStore("大雕", "Amazon")
db.fetchAndStore("大雕", "Jd")
db.fetchAndStore("大雕", "Taobao")
db.fetchAndStore("dadiao", "Jd")
db.fetchAndStore("dadiao", "Taobao")
sleep(15)
res = db.findTuple('*', 'Items', ['q like "%%大雕%%"'])
print "res="
print res
'''

'''
db.insertTuples('Updates', dataUpdates)
db.insertTuples('Items', dataItems)
db.insertTuples('Sessions', dataSessions)
res = db.findTuple('*', 'Updates', ['q like "%%dadiao%%"'])
print res
res = db.queryUpdate('dadiadddo2')
print res
'''

'''
db = DC.DbController('test.db')
db.initDb()
db.renewUpdate('大雕')
sleep(2)
db.fetchAndStore("大雕", "Jd")
'''

db = DC.DbController('test.db')
db.initDb()
db.renewUpdate('大雕')
sleep(10)
db.querySearch('大雕', 'Jd', 'xxxx', 1)
