"use strict";

hippoD.controller("ItemCtrl", function ($scope, $stateParams, $window, DBService, HippodDataService) {
	$scope.id = $stateParams.id

	DBService.getFoo($scope.id).then(function(res) {
		$scope.data = res;
	});


	HippodDataService.getAchievements($scope.id).then(function(res) {

		var var_data = new Array();
		angular.forEach(res, function(value, key) {
			var found_variety = false;
			angular.forEach(var_data, function(value2, key2) {
				if (value['variety-id'] == value2['variety-id']) {
					found_variety = true;

					var achievment = { };
					achievment['id'] = value['id'];
					achievment['result'] = value['result'];
					achievment['anchor'] = value['anchor'];
					achievment['submitter'] = value['submitter'];
					achievment['test-date'] = humanFormatDateYYYYMMDDHHMM(value['test-date']);
					achievment['date-added'] = humanFormatDateYYYYMMDDHHMM(value['date-added']);

					console.log("XXX");

					console.log(var_data);
					value2['achievements'].push(achievment);
				}
			});

			if (found_variety == false) {
				// new entry
				var achievment = { };
				achievment['id'] = value['id'];
				achievment['result'] = value['result'];
				achievment['anchor'] = value['anchor'];
				achievment['submitter'] = value['submitter'];
				achievment['test-date'] = humanFormatDateYYYYMMDDHHMM(value['test-date']);
				achievment['date-added'] = humanFormatDateYYYYMMDDHHMM(value['date-added']);

				// new container required
				var var_container = { };
				var_container['variety'] = new Array();
				var_container['variety-id'] = value['variety-id'];
				if ('variety' in value) {
					angular.forEach(value['variety'], function(v3, k3) {
						var_container['variety'].push([k3, v3]);
					});

				}

				var_container['achievements'] = new Array();
				var_container['achievements'].push(achievment);


				var_data.push(var_container);
			}

			$scope.varieties = var_data;
		});
	});

});
