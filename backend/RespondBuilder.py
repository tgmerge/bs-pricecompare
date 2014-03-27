# -*- coding: utf-8 -*-


class RespondBuilder:
    '''Build respond dict from integrets.'''

    def buildQueryRespond(q, qpage, data, count, time):
        return {'q': q,
                'page': qpage,
                'totalPage': count,
                'updateTime': time,
                'items': data}
