"use strict";

hippoD.factory('ResourcesService', function($http) {

    var srv = {};

    srv.getRessource = function() {
        return $http.get('/api/v1.0/resources', {});
    };

    // Public API
    return {
        getRessource: function() {
            return srv.getRessource();
        }
    };
});
