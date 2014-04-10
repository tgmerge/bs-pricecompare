# -*- coding: utf-8 -*-
from bottle import route, run, static_file, get, request, Bottle
import DbController

db = DbController.DbController('test.db')
db.initDb()
priceCompare = Bottle()

with priceCompare:
    @route('/')
    def indexHtml():
        return staticFile('index.html')

    @route('/<filepath:path>')
    def staticFile(filepath):
        return static_file(filepath, root='./../static/')

    @get('/search')
    def query():
        # todo add value validator
        return db.querySearch(q=request.GET.get('q'),
                              site=request.GET.get('site'),
                              sid=request.GET.get('session'),
                              page=request.GET.get('page'))

    @get('/update')
    def queryUpdate():
        # todo add value validator
        return db.queryUpdate(q=request.GET.get('q'))

run(app=priceCompare, host='localhost', port=8080)
