from bottle import route, run, static_file, get, request
import PriceParser
import time


@route('/')
def indexHtml():
    return staticFile('index.html')


@route('/<filepath:path>')
def staticFile(filepath):
    return static_file(filepath, root='./../static/')


@get('/search')
def query():
    # todo value validator

    p = PriceParser.PriceParser()

    data = p.parseEverything(request.GET.get('q'),
                             1,
                             request.GET.get('site'))
    return {'q': request.GET.get('q'),
            'site': request.GET.get('site'),
            'session': request.GET.get('session'),
            'page': request.GET.get('page'),
            'totalPage': "4",
            'count': data.__len__(),
            'updateTime': time.time(),
            'items': data}


@get('/update')
def queryUpdate():
    # todo value validator

    return {'q': request.GET.get('q'),
            'updateTime': time.time()}

run(host='localhost', port=8080)
