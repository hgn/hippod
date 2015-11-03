"use strict";

hippoD.controller("AdminCtrl", function ($scope, ResourcesService) {

	ResourcesService.getRessource().then(function(res) {
		$scope.overall_data_byte_human = prettyNumber(res['data']['data']['overall'], 'iec');
		$scope.overall_data_byte_vanilla = res['data']['data']['overall'];
	}, function(error) {
		$scope.overall_data_byte_human = "unknown (API error)";
		$scope.overall_data_byte_vanilla = "unknown (API error)";
	});

});

