"use strict";

hippoD.controller("AdminCtrl", function ($scope, ResourcesService) {

	ResourcesService.getRessource().then(function(res) {
		$scope.overall_data_byte = res['data']['data']['overall'];
	}, function(error) {
		$scope.overall_data_byte = "unknown (API error)";
	});

});

