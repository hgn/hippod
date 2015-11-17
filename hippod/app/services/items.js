"use strict";

hippoD.factory('ItemService', function($http) {



  var promise;
  var myService = {
    getItemList: function() {
      if ( !promise ) {
        var obj = { };
        obj['limit'] = 0;
        obj['ordering'] = "by-submitting-date-reverse";
        obj['filter-by-result'] = "all";
        obj['filter-by-maturity-level'] = "all";
        // $http returns a promise, which has a then function, which also returns a promise
        promise = $http(
{
        url: '/api/v1/objects',
        dataType: 'json',
        method: 'POST',
        data: obj,
        headers: { "Content-Type": "application/json" }
    }
)


          .then(function (response) {
          // The then function here is an opportunity to modify the response
          console.log(response);
          // The return value gets picked up by the then in the controller.
          return response.data;
        });
      }
      // Return the promise to the controller
      return promise;
    }
  };
  return myService;
});


hippoD.factory('DBService', function($http) {
   return {
     getFoo: function(id) {
			 var obj = {};
			 var promise = $http(
				 {
					 url: '/api/v1/object/' + id,
					 dataType: 'json',
					 method: 'POST',
					 data: obj,
					 headers: { "Content-Type": "application/json" }
			   })
				 .then(function (response) {
					 console.log(response.data.data);
					 var achievements = response.data.data['object-achievements'];
					 for (var i = 0; i < achievements.length; i++) {
						 console.log(achievements[i]);
					 }

					 var item_data = response.data.data['object-item']['data'];
					 for (var i = 0; i < item_data.length; i++) {
						 if (item_data[i]['type'] == 'description') {
							 return $http(
									 {
										 url: '/api/v1/data/' + item_data[i]['data-id'],
										 dataType: 'json',
										 method: 'POST',
										 data: obj,
										 headers: { "Content-Type": "application/json" }
									 })
							     .then(function (response_enc) {
										 item_data[i]['data'] = response_enc.data
										 response.data.data['__description'] = response_enc.data

										 return response.data.data;
									 });
						 }
					 }

					 return response.data;
				 });
		 return promise;
   }
	 }
});

hippoD.filter('unsafe', function($sce) { return $sce.trustAsHtml; });
