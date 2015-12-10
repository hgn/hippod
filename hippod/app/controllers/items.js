"use strict";

hippoD.controller("ItemsCtrl", function ($scope, ItemService, $uibModal, $log, $interval) {

	  // Maturity Level Buttons
		$scope.maturity_button = "All";
		$scope.maturity_actions = [
			"All", "Testing", "Stable", "Outdated"
		];
		$scope.maturity_change = function(name){
			$scope.maturity_button = name;
		}


	  // Limit Result Buttons
		$scope.result_button = "All";
		$scope.result_actions = [
			"All", "Passed", "Failed", "Non Applicable"
		];
		$scope.result_change = function(name){
			$scope.result_button = name;
		}

	  // Submiter Buttons
		$scope.submitter_button = "All";
		$scope.submitter_actions = [
			"All", "Foo", "Bar"
		];
		$scope.submitter_change = function(name){
			$scope.submitter_button = name;
		}


	  // Resonsible Buttons
		$scope.responsible_button = "All";
		$scope.responsible_actions = [
			"All", "Foo", "Bar"
		];
		$scope.responsible_change = function(name){
			$scope.responsible_button = name;
		}

		function resultNameMapper(button_name) {
			switch (button_name) {
				case "Passed": return "passed";
				case "Failed": return "failed";
				case "Non Applicable": return "nonapplicable";
				default: console.log("result name not supported");
			}
		};

		$scope.filterSelection = function () {
			return function (item) {

				if ($scope.result_button !== $scope.result_actions[0]) {
					var match = resultNameMapper($scope.result_button);
					if (match !== item['object-achievements']['test-result'])
						return false;
				}

				if ($scope.maturity_button !== $scope.maturity_actions[0]) {
					var match = $scope.maturity_button.toLowerCase();
					if (match !== item['maturity-level']['level'])
						return false;
				}

				if ($scope.submitter_button !== $scope.submitter_actions[0]) {
					if ($scope.submitter_button !== item['object-achievements']['submitter'])
						return false;
				}

				if ($scope.responsible_button !== $scope.responsible_actions[0]) {
					if ($scope.responsible_button !== item['object-attachment']['responsible'])
						return false;
				}

				return true;
			}
		}



	  // Sorting Buttons
		$scope.sort_button = "Tested";
		$scope.sort_actions = [
			"Tested", "Untested", "New"
		];
		$scope.sort_change = function(name){
			$scope.sort_button = name;
		}

		// Verbose/Condensed Button
	  $scope.condensed = true;
    $scope.verbose_button = function () {
        $scope.condensed = !$scope.condensed;
    }
    $scope.condensed_button = function () {
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

			var colorArray = [ '#4CAF50', '#F44336', '#2196F3', '#A1887F' ];
			function colorFunction() {
				return function(d, i) {
					return colorArray[i];
				};
			};

			$scope.optionsPieChart = {
				chart: {
					type: 'pieChart',
					height: 500,
					x: function(d){return d.key;},
					y: function(d){return d.y;},
					showLabels: true,
					duration: 500,
					labelThreshold: 0.01,
					labelSunbeamLayout: true,
				  growOnHover: true,
	        color:colorFunction(),
					legend: {
						margin: {
							top: 20,
							right: 0,
							bottom: 0,
							left: 0
						}
					}
				}
			};

			$scope.exampleData2 = [
				{ key: "Passed", y: passed_achievement },
				{ key: "Failed", y: failed_achievement },
				{ key: "Non Applicable", y: nonapplicable_achievement },
				{ key: "Never Tested", y: no_achievements }
			];

			$scope.testDateOldest = humanRelativeDate(test_date_oldest);
			$scope.testDateYoungest = humanRelativeDate(test_date_youngest);
  

		}, function(error) {
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


});

