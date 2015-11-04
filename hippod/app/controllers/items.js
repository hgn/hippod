"use strict";

hippoD.controller("ItemsCtrl", function ($scope, ItemService) {

	ItemService.getItemList().then(function(res) {
                $scope.data = res.data;
		console.log(res.data);
	}, function(error) {
		console.log(res);
	});

});

