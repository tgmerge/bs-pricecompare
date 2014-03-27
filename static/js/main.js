// query 

var searchInput = $("#search-box");
var siteList = $("#site-tab");
var pageList = $("#paging-section");
var resultList = $("#result-all>div.row");

var itemTemp = $("#template>div.item");
var pageTemp = $("#template>li.pageno.normal");
var pageActiveTemp = $("#template>li.pageno.active")

var searchUrl = "/search";
var updateUrl = "/update";

// Query
var sendSearch = function() {
    // TODO some validator
    var q = searchInput.val();
    var site = siteList.find("li.active a").attr('site');
    var session = Math.random();
    var page = pageList.pagination('getCurrentPage');
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
    $("#paging-section").pagination({
        pages: totalPage,
        currentPage: page,
        displayedPages: 10,
        cssStyle: 'light-flat-theme',
        prevText: "<<",
        nextText: ">>",
        onPageClick: function() {
            sendSearch()
        }
    });
    console.log("[updatePageNumber]page, totalpage = " + page + "," + totalPage);
}

var updateItems = function(items) {
    clearItems();
    s = items;
    for (i in items) {
        var item = items[i];
        addItem(item.img, item.url, item.price, item.site, item.title);
    }
    console.log("[updateItems]" + items.length);
}

var addItem = function(img, url, price, site, title) {
    var item = itemTemp.clone();
    item.find("img").attr("src", img);
    item.find("a.img-link").attr("href", url);
    item.find("span.price").text(price);
    item.find("span.site").text(site);
    item.find("p.item-title").text(title);
    resultList.append(item);
    //console.log("[addItem]additem:" + img + "," + price + "," + site + "," + title);
}

var clearItems = function() {
    resultList.find("div.item").remove();
    console.log("[clearItems]cleared all items.");
}

//init
updatePageNumber(1, 5);
