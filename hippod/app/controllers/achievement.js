"use strict";

hippoD.controller("AchievementCtrl", function ($scope, $stateParams) {
	$scope.id = $stateParams.id
	$scope.achievement = $stateParams.achievement_id
});
