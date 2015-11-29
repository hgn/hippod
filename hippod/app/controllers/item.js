"use strict";

hippoD.controller("ItemCtrl", function ($scope, $stateParams, $window, DBService) {
	$scope.id = $stateParams.id

	DBService.getFoo($scope.id).then(function(res) {
		$scope.data = res;
	});

});
