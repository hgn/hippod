
hippoD.factory('ItemDataService', function($http) {

    var srv = {};

    srv.getRessource = function(itemNo) {
			  if (itemNo.length != 3) {
					return {};
				}
        return $http.get('/api/v1.0/resources', {item: itemNo}
        );
    };

    // Public API
    return {
        getRessource: function(no) {
            return srv.getRessource(no);
        }
    };
});

