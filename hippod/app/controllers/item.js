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









  $scope.graphTestResultOptions = {
            chart: {
                type: 'stackedAreaChart',
                height: 150,
                margin : {
                    top: 0,
                    right: 0,
                    bottom: 30,
                    left: 55
                },
                x: function(d){return d[0];},
                y: function(d){return d[1];},
                useVoronoi: false,
                clipEdge: true,
                duration: 100,
                useInteractiveGuideline: true,
                xAxis: {
                    showMaxMin: false,
                    tickFormat: function(d) {
                        return d3.time.format('%x')(new Date(d))
                    }
                },
                yAxis: {
                    tickFormat: function(d){
                        return d3.format(',.2f')(d);
                    }
                },
								showYAxis: false,
								showLegend: false,
								showControls: false,
                zoom: {
                    enabled: true,
                    scaleExtent: [1, 10],
                    useFixedDomain: false,
                    useNiceScale: false,
                    horizontalOff: false,
                    verticalOff: true,
                    unzoomEventType: 'dblclick.zoom'
                }
            }
        };

        $scope.graphTestResultData = [
            {
                "key" : "Passed" ,
                "values" : [ [ 1025409600000 , 2] , [ 1028088000000 , 3] ] 
            },

            {
                "key" : "Failed" ,
                "values" : [ [ 1025409600000 , 3] , [ 1028088000000 , 0] ]
            },

            {
                "key" : "Non Applicable" ,
                "values" : [ [ 1025409600000 , 1] , [ 1028088000000 , 0] ]
            },

            {
                "key" : "Not Tested" ,
                "values" : [ [ 1025409600000 , 0] , [ 1028088000000 , 0] ]
            }



        ];





});
