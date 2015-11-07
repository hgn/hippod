"use strict";

hippoD.controller("AdminCtrl", function ($scope, ResourcesService) {

	ResourcesService.getRessource().then(function(res) {
		var data_array = res['data']['data']['item-bytes-overtime']
		var bytes_actual = data_array[data_array.length - 1][1]
		$scope.overall_data_byte_human = prettyNumber(bytes_actual, 'iec');
		$scope.overall_data_byte_vanilla = bytes_actual;
	}, function(error) {
		$scope.overall_data_byte_human = "unknown (API error)";
		$scope.overall_data_byte_vanilla = "unknown (API error)";
	});

});

