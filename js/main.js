// query 

var searchInput = $("#search-box");
var sourceList = $("#source-tab");
var pageList = $("#page-list");
var SOURCE = {
    0: 'all',
    1: 'tmall',
    2: 'amazon',
    3: 'jd'
}
var searchUrl = "/search";
var updateUrl = "/update";

// Query
var sendSearch = function() {
    // gather query items
    // TODO some validator
    var q = searchInput.val();
    var source = SOURCE[sourceList.find("li.active a").attr('index')];
    var session = Math.random();
    var page = pageList.find("li.active a").text();

    // send ajax query, update page
    $.getJSON(
        searchUrl, {
            'q': q,
            'source': source,
            'session': session,
            'page': page
        }, updatePage(json)
    );

}

var sendForUpdate = function() {
    // gather q from 'this'
    var q = 0;

    // send ajax query, update time message
    $.getJSON(
        updateUrl, {
            'q': q
        }, function(data) {
            updateTime(data.updateTime)
        }
    );
}

// HTML updater
var updatePage = function(json) {
    // TODO some validator
    //update search count
    updateSearchCount(json.count);

    //update "is newest"
    updateTime(json.updateTime);

    //update page number
    updatePageNumber(json.page, json.totalPage);

    //update items
    updateItems(json.items);
}

var updateSearchCount = function(count) {
    // todo
    console.log("[updateSearchCount]searchCount = " + count);
}

var updateTime = function(updateTime) {
    // todo
    console.log("[updateTime]updateTime = " + updateTime);
}

var updatePageNumber = function(pageNumber) {
    // todo
    console.log("[updatePageNumber]pageNumber = " + XXX);
}

var updateItems = function(items) {
    // todo
    console.log("[updateItems]items = " + items);
}

var addItem = function(img, price, source, title) {
    // todo
    console.log("[addItem]additem:" + img + "," + price + "," + source + "," + title);
}

var clearItems = function() {
    // todo
    console.log("[clearItems]clear items.");
}
