"use strict";

hippoD.controller("ItemsCtrl", function ($scope, ItemService, $uibModal, $log) {



	  $scope.condensed = true;
    $scope.button1 = function () {
        $scope.condensed = !$scope.condensed;
    }

    $scope.button2 = function () {
        $scope.condensed = !$scope.condensed;
    }

		// if called we fill the data
		ItemService.getItemList().then(function(res) {
		  var number = 0;
			var passed_achievement = 0;
			var failed_achievement = 0;
			var nonapplicable_achievement = 0;
			var no_achievements = 0;

			$scope.passedAchievements = 0;
			$scope.noAchievements = 0;

			var test_date_found_once = false;
			var test_date_oldest;
			var test_date_youngest;

			$scope.testDateOldest = "";
			$scope.testDateYoungest = "";

			$scope.data = res.data;
			angular.forEach(res.data, function(value, key) {
				number++;
				if ("object-achievements" in value) {

					var result = value['object-achievements']['test-result'];
					if (result == "passed") {
						passed_achievement++;
					} else if (result == "failed") {
						failed_achievement++;
					} else if (result == "nonapplicable") {
						nonapplicable_achievement++;
					} else {
						console.log("corrupt achievement!");
						console.log(value);
					}

					var test_date = new Date(value['object-achievements']['test-date']);
					if (!test_date_found_once) {
						test_date_oldest = test_date;
						test_date_youngest = test_date;
						test_date_found_once = true;
					}

					if (test_date.getTime() > test_date_youngest.getTime()) {
						test_date_youngest = test_date;
					}
					if (test_date.getTime() < test_date_oldest.getTime()) {
						test_date_oldest = test_date;
					}

				} else {
					no_achievements++;
				}
			});

		  $scope.numberItems = number;
			$scope.passedAchievements = passed_achievement;
			$scope.failedAchievements = failed_achievement;
			$scope.nonApplicableAchievements = nonapplicable_achievement;
			$scope.noAchievements = no_achievements;

			$scope.exampleData2 = [
				{ key: "Passed", y: passed_achievement },
				{ key: "Failed", y: failed_achievement },
				{ key: "Non Applicable", y: nonapplicable_achievement },
				{ key: "Never Tested", y: no_achievements }
			];

			$scope.testDateOldest = humanRelativeDate(test_date_oldest);
			$scope.testDateYoungest = humanRelativeDate(test_date_youngest);
  

		}, function(error) {
			console.log(res);
			$scope.data = null;
		});

		$scope.xFunction = function(){
			return function(d) {
				return d.key;
			};
		}
		$scope.yFunction = function(){
			return function(d){
				return d.y;
			};
		}
		var colorArray = [ '#4CAF50', '#F44336', '#2196F3', '#0091EA' ];
		$scope.colorFunction = function() {
			return function(d, i) {
				return colorArray[i];
			};
		}



  $scope.items = ['item1', 'item2', 'item3'];

  $scope.open = function (sha_id) {

    var modalInstance = $uibModal.open({
      animation: false,
      templateUrl: 'templates/modal-object-item.html',
      controller: 'ModalInstanceCtrl',
      size: 'lg',
      resolve: {
        items: function () {
          return $scope.items;
        },
        id: function () {
          return sha_id;
        }
      }
    });

    modalInstance.result.then(function (selectedItem) {
      $scope.selected = selectedItem;
    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };

});


hippoD.controller('ModalInstanceCtrl', function ($scope, $uibModalInstance, items, id) {

	$scope.id = id;
  $scope.items = items;

  $scope.selected = {
    item: $scope.items[0]
  };

  $scope.ok = function () {
    $uibModalInstance.close($scope.selected.item);
  };

  $scope.cancel = function () {
    $uibModalInstance.dismiss('cancel');
  };
});
