"use strict";

hippoD.controller("ItemsCtrl", function ($scope, ItemService) {

	ItemService.getItemList().then(function(res) {
		console.log(res);
	}, function(error) {
		console.log(res);
	});

});

