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
					 var achievements = response.data.data['object-achievements'];
					 for (var i = 0; i < achievements.length; i++) {
						//console.log(achievements[i]);
					 }
					 response.data.data['__attachments'] = attachments;

					 var item_data = response.data.data['object-item']['data'];
					 var attachments = new Array();
					 for (var i = 0; i < item_data.length; i++) {
						 if (item_data[i]['type'] !== 'description') {
							 var entry = {};
							 entry['name'] = item_data[i]['name'];
							 entry['size-real'] = item_data[i]['size-real'];
							 entry['data-id'] = item_data[i]['data-id'];
							 attachments.push(entry);
						 }
					 }
					response.data.data['__attachments'] = attachments;

					 // fetch description
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
										 var text = response_enc.data;
										 item_data[i]['data'] = text;
										 response.data.data['__description'] = text;

										 return response.data.data;
									 });
						 }
					 }

					 return response.data.data;
				 });
		 return promise;
   }
	 }
});


hippoD.factory('HippodDataService', function($http) {

	var getAchievements = function (core_id) {

			 var obj = {};
			 var promise = $http(
				 {
					 url: '/api/v1/object/' + core_id,
					 dataType: 'json',
					 method: 'POST',
					 data: obj,
					 headers: { "Content-Type": "application/json" }
			   })
				 .then(function (response) {
					 return response.data.data['object-achievements'];
				 })

				 return promise;

	};

	return {
		getAchievements: getAchievements
	};
});

hippoD.filter('toHtmlSave', function($sce) {

	function replaceAll(str, find, replace) {
		if (!str)
			return str;
		return str.replace(new RegExp(find, 'g'), replace);
	}

	return function(text, argument) {
		// we correct the link from username (tomato.png) to
		// link: api/v1/data/34994393434934
		angular.forEach(argument, function(value, key) {
			text = replaceAll(text, value['name'],'api/v1/data/' + value['data-id']);
		});
		return $sce.trustAsHtml(text);
	};
});
