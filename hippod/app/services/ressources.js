"use strict";

hippoD.factory('ResourcesService', function($http) {

    var srv = {};

    srv.getRessource = function() {
			 var promise = $http(
				 {
					 url: '/api/v1.0/resources',
					 dataType: 'json',
					 method: 'GET',
					 data: { },
					 headers: { "Content-Type": "application/json" }
			   })
				 .then(function (response) {

					 // calculate avg value for mimetype compression
					 response.data.data['__compression'] = [];
					 var ptr = response.data.data['data-compression'];
					 var cnt = 0;
					 for (var property in ptr) {
						 var mimetype = property;
						 var rounds = 0;
						 var sum = 0;
						 for (var i = 0; i < ptr[property].length; i++) {
							 var pct = ptr[property][i]['size-compressed'] / (ptr[property][i]['size-raw'] / 100.0);
							 sum += pct;
							 rounds++;
						 }
						 if (rounds) {
							 var avg = sum / rounds;
							 response.data.data['__compression'][cnt] = new Array(mimetype, avg);
						 }
						 cnt++;
					 }

					 return response;
				 });
		 return promise;
		};

    //srv.getRessource = function() {
    //    return $http.get('/api/v1.0/resources', {});
    //};

    // Public API
    return {
        getRessource: function() {
            return srv.getRessource();
        }
    };
});
