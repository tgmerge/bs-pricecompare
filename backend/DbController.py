def queryUpdate(q):
	findtuple(Updates, q=q)
	-> return JSON(time)


def querySearch(q, site, sid, page):
	if A = findtuple(Sessions, sid=sid) == None:
		if B = findtuple(Items, (q in title or q in q) and (site=site)) == None:
			fetch and parse from websites for a limited time
			write parse result to Items
			B = findtuple(Items, (q in title or q in q) and (site=site))
		write(Sessions, data from B)
	return data from Sessions from A {q, site, sid, page, [{site, img, url, price, title}, ...]