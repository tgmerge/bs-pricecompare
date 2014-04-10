# -*- coding: utf-8 -*-
import urllib2
import urllib
from BeautifulSoup import BeautifulSoup as MoeSoup


class PriceParser(object):
    """Parse search result page
    To support another site "SITE", just add SiteUrl, parseSiteUrl(),
    parseSiteDiv(), parseSiteItem().
    """

    TaobaoUrl = 'http://s.m.taobao.com/search.htm?s=%(startItem)d&n=20&q=%(q)s'
    JdUrl = 'http://m.jd.com/ware/search.action?cid=0&keyword=%(q)s&sort=0&page=%(page)d'
    AmazonUrl = 'http://www.amazon.cn/gp/aw/s?page=%(page)d&keywords=%(q)s'
    TaobaoItemsPerPage = 20
    availableSites = ["Amazon", "Jd", "Taobao"]

    def __init__(self):
        super(PriceParser, self).__init__()

    def parseTaobaoUrl(self, q, page):
        return self.TaobaoUrl % {'startItem': self.TaobaoItemsPerPage * page,
                                 'q': urllib.quote_plus(q)}

    def parseJdUrl(self, q, page):
        return self.JdUrl % {'page': page + 1,
                             'q': urllib.quote_plus(q)}

    def parseAmazonUrl(self, q, page):
        return self.AmazonUrl % {'page': page + 1,
                                 'q': urllib.quote_plus(q)}

    def parseTaobaoDiv(self, soup):
        return soup.findAll('div', attrs={'class': 'detail'})

    def parseJdDiv(self, soup):
        return soup.findAll('div', attrs={'class': 'pmc'})

    def parseAmazonDiv(self, soup):
        return soup.findAll('div', attrs={'class': 'toTheEdge productList'})

    def parseTaobaoItem(self, item):
        return {
            'img': item.findChild('img')['src'].rsplit('_', 1)[0] + '_200x200.jpg',
            'price': item.findChild('strong', attrs={'class': 'red'}).getText(),
            'title': item.findChild('a').getText(),
            'url': 'http://item.taobao.com/item.htm?id=' +
                   item.findChild('a')['href'].split('/i', 1)[1].split('.htm', 1)[0],
            'pid': item.findChild('a')['href'].split('/i', 1)[1].split('.htm')[0],
            'site': 'Taobao'
        }

    def parseJdItem(self, item):
        return {
            'img': item.findChild('img')['src'].replace('n4', 'n2', 1),
            'price': item.findChild('div', attrs={'class': 'price'}).findChild(
                'font').getText().rsplit(';', 1)[1],
            'title': item.findChild('a').getText(),
            'url': 'http://item.jd.com' + item.findChild('a')['href'],
            'pid': item.findChild('a')['href'].rsplit('/', 1)[1].split('.', 1)[0],
            'site': 'Jd'
        }

    def parseAmazonItem(self, item):
        return {
            'img': item.findChild('img')['src'].replace('._SL75_.', '._AA200_.', 1),
            'price': item.findChild('span', attrs={'class': 'dpOurPrice'}).getText().rsplit(
                u'￥', 1)[1],
            'title': item.findChild('span', attrs={'class': 'productTitle'}).findChild(
                'a').getText(),
            'url': 'http://www.amazon.cn' + item.findChild('a')['href'].replace(
                'gp/aw/d', 'dp', 1),
            'pid': item.findChild('a')['href'].split('qid=', 1)[1].split('&', 1)[0],
            'site': 'Amazon'
        }

    def parseEverything(self, q, page, site):
        """Parse everything.
        args:
            q   : string, query string
            page: int, result page index
            site: string, currently can be "amazon", "jd", "taobao"
        return:
            a list of dict{img, price, title, url, pid}
        """
        print "[parseEverything]%s, %s, %s" % (q, page, site)

        # Take out tools
        site = site.title()
        page = int(page)
        parseUrl = getattr(self, "parse%sUrl" % site)
        parseDiv = getattr(self, "parse%sDiv" % site)
        parseItem = getattr(self, "parse%sItem" % site)

        # Put page into soup
        url = parseUrl(q, page)
        print "[parseEverything]URL=%s" % url
        soup = MoeSoup(urllib2.urlopen(url))

        # Take out what we need, ignoring ones can't be parsed 'w'
        items = parseDiv(soup)
        datas = []
        for item in items:
            try:
                data = parseItem(item)
                if data['img'] and data['price'] and data['title'] and data['url'] and data['pid']:
                    datas.append(data)
                    print "[%s]Item #%d: %s ..." % (site, datas.__len__(), data['title'][:15])
                else:
                    print "[%s]Null value in item, ignoring item" % site
            except (IndexError, AttributeError, TypeError) as e:
                    print "[%s]Exception, ignoring item" % site
                    print e

        print "---Returning %d items---" % datas.__len__()
        return datas
