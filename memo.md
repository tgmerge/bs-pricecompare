## Server side

### database

* Updates(*q*, time)
* Items(*q*, *id*, site, url, price, img, title)
* Sessions(*sid*, data)

### process

	querysearch(q, site, sid, page)
		# see the code 'w'

	queryupdate(q)
		findtuple(Updates, q=q)
		return JSON(time)

## Client side

### ajax/json transfer

#### [C]-->[S.searchUrl]

* q: query keyword
* site: site name, can be 'all', 'amazon', etc
* session: random session id
* page: new page we're jumping to

#### [C]<--[S.searchUrl]

* q
* site
* session
* page
* count: total number of returned items
* updateTime: server side update time of query 'q'
* totalPage: we have at most this number of pages
* items: [{img, price, site, url, title}, ...] list of actual items

- - -

#### [C]-->[S.updateUrl]

* q: query keyword

#### [C]<--[S.updateUrl]

* q
* updateTime: server side update time of query 'q'

## CheckUpdate process

For client side:

    New search:
        start_clock(10s)
        set_page_to(1)

    Next page:
        set_page_to(n)

    While clock triggered:
        stop_clock()

    While clock tick clicked:
        new search()