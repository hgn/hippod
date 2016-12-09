"use strict";

hippoD.controller("AchievementCtrl", function ($scope, $stateParams) {

	$scope.id = $stateParams.id;
    $scope.sub_id = $stateParams.sub_id;
	$scope.achievement = $stateParams.achievement_id;

});
