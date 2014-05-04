// jquery
var searchInput = $("#search-box");
var siteList = $("#site-tab");
var pageList = $("#paging-section");
var resultList = $("#result-all>div.row");

var alertNum = $("#alert-resultnum");
var alertRefresh = $("#alert-refresh");
var clockExist = $("#clock-exist");

var itemTemp = $("#template>div.item");
var pageTemp = $("#template>li.pageno.normal");
var pageActiveTemp = $("#template>li.pageno.active")

// const
var searchUrl = "/search";
var updateUrl = "/update";

//init
var session = Math.random();
var oldTime = 0;
var oldq = ""; // todo in search: if q != oldq: generate new session, oldq = q
var oldsite = "";
var clockId = 0;

// Methods for query
var newSearch = function() {
    session = Math.random();
    clockId = window.setInterval("sendForUpdate();", 10000);
    clockExist.show();
    updatePageNumber(1, 1);
    sendSearch();
}

var search = function() {
    var newq = searchInput.val();
    var newsite = siteList.find("li.active a").attr('site');
    if (newq != oldq || newsite != oldsite) {
        oldq = newq;
        oldsite = newsite;
        window.clearInterval(clockId);
        clockExist.hide();
        newSearch();
    } else {
        sendSearch();
    }
}

// Methods for getting json(with updating page)

var sendSearch = function() {
    // TODO some validator
    $.getJSON(
        searchUrl, {
            'q': searchInput.val(),
            'site': siteList.find("li.active a").attr('site'),
            'session': session,
            'page': pageList.pagination('getCurrentPage')
        }, function(data) {
            updatePage(data);
        }
    );
}

var sendForUpdate = function() {
    var q = searchInput.val();
    var t = 0;
    $.getJSON(
        updateUrl, {
            'q': q
        },
        function(data) {
            updateTimeTips(data.updateTime);
        }
    );
};

// Methods for updating html

var updatePage = function(json) {
    // TODO some validator
    updateSearchCount(json.count);
    updateTimeTips(json.updateTime);
    updatePageNumber(json.page, json.totalPage);
    updateItems(json.items);
}

var updateSearchCount = function(count) {
    alertNum.show(100);
    alertNum.text("搜索到" + count + "条结果。");
    console.log("[updateSearchCount]" + count);
}

var updateTimeTips = function(updateTime) {
    if (updateTime - oldTime > 100) {
        alertRefresh.show(100);
        oldTime = updateTime;
        window.clearInterval(clockId);
        clockExist.hide();
    } else {
        alertRefresh.hide(100);
    }
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
}

var clearItems = function() {
    resultList.find("div.item").remove();
    console.log("[clearItems]cleared all items.");
}

updatePageNumber(1, 1);
