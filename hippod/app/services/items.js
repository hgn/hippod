"use strict";

hippoD.factory('ItemService', function($http) {

    var srv = {};

    srv.getItemList = function() {
        var obj = { };
        obj['limit'] = 0;
        obj['ordering'] = "by-submitting-date-reverse";
        obj['filter-by-result'] = "all";
        obj['filter-by-maturity-level'] = "all";

    return $http({
        url: '/api/v1/objects',
        dataType: 'json',
        method: 'POST',
        data: obj,
        headers: { "Content-Type": "application/json" }
    });
    };   

    // Public API
    return {
        getItemList: function() {
            return srv.getItemList();
        }
    };
});
