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


