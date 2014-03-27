// query 

var searchInput = $("#search-box");
var siteList = $("#site-tab");
var pageList = $("#page-list");
var resultList = $("#result-all>div.row");

var itemTemp = $("#template>div.item");
var pageTemp = $("#template>li.pageno.normal");
var pageActiveTemp = $("#template>li.pageno.active")

var siteDict = {
    '0': 'all',
    '1': 'taobao',
    '2': 'amazon',
    '3': 'jd'
}
var searchUrl = "/search";
var updateUrl = "/update";

// Query
var sendSearch = function() {
    // TODO some validator
    var q = searchInput.val();
    var site = siteList.find("li.active a").attr('site');
    var session = Math.random();
    var page = pageList.find("li.active a").text();
    $.getJSON(
        searchUrl, {
            'q': q,
            'site': site,
            'session': session,
            'page': page
        }, function(data) {
            updatePage(data)
        }
    );

}

var sendForUpdate = function() {
    var q = searchInput.val();
    $.getJSON(
        updateUrl, {
            'q': q
        },
        function(data) {
            updateTime(data.updateTime)
        }
    )
};

// HTML updater
var updatePage = function(json) {
    // TODO some validator
    updateSearchCount(json.count);
    updateTime(json.updateTime);
    updatePageNumber(json.page, json.totalPage);
    updateItems(json.items);
}

var updateSearchCount = function(count) {
    // todo
    console.log("[updateSearchCount]" + count);
}

var updateTime = function(updateTime) {
    // todo
    console.log("[updateTime]" + updateTime);
}

var updatePageNumber = function(page, totalPage) {
    var pageItems = pageList.find("li").remove()
    pageList.append(pageItems[0])
    for (var i = 1; i <= totalPage; i++) {
        pageList.append(
            (i == page ? pageActiveTemp : pageTemp).clone().children("a").text(i).parent()
        );
    }
    pageList.append(pageItems[pageItems.length - 1]);
    console.log("[updatePageNumber]page, totalpage = " + page + "," + totalPage);
}

var updateItems = function(items) {
    clearItems();
    s = items;
    for (i in items) {
        var item = items[i];
        addItem(item.img, item.price, item.site, item.title);
    }

    console.log("[updateItems]items = " + items);
}

var addItem = function(img, price, site, title) {
    var item = itemTemp.clone();
    item.find("img").attr("src", img);
    item.find("span.price").text(price);
    item.find("span.site").text(site);
    item.find("p.item-title").text(title);
    resultList.append(item);
    console.log("[addItem]additem:" + img + "," + price + "," + site + "," + title);
}

var clearItems = function() {
    resultList.find("div.item").remove();
    console.log("[clearItems]cleared all items.");
}
