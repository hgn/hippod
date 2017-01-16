"use strict";

hippoD.controller("ItemCntrl", function ($scope, $stateParams, $window, DBService, HippodDataService) {
    $scope.id = $stateParams.id
    $scope.sub_id =$stateParams.sub_id

    function updateAchievementChart(res) {

        function getWeekDate(date){
            var weekNumber = date.getWeek();
            var year = date.getFullYear();
            return new Date(year, 0, 1+((weekNumber-1)*7));
        };

        function getDayDate(date){
            var day = date.getUTCDate();
            var month = date.getUTCMonth();
            var year = date.getUTCFullYear();
            return new Date(year, month, day, 0, 0, 0);
        };


        function singularToMult(data) {
            var o = { };
            o['pass'] = new Array();
            o['fail'] = new Array();
            o['non']  = new Array();

            angular.forEach(data, function(value, key) {
                var t = new Date(value['date']).getTime();
                o['pass'].push([t, value['pass']]);
                o['fail'].push([t, value['fail']]);
                o['non'].push([t, value['non']]);
            });
            return o;
        };


        var achiev_res_date_arr = new Array();

        angular.forEach(res, function(value, key) {
            var date = new Date(value['date-added']);
            var norm_data = getDayDate(date);

            if (achiev_res_date_arr.length <= 0) {
                var entry = { };
                entry['date'] = norm_data;
                entry['pass'] = 0;
                entry['fail'] = 0;
                entry['non'] = 0;
                achiev_res_date_arr.push(entry);
            } else {
                if (achiev_res_date_arr[achiev_res_date_arr.length - 1]['date'].getTime() != norm_data.getTime()) {
                    var entry = { };
                    entry['date'] = norm_data;
                    entry['pass'] = 0;
                    entry['fail'] = 0;
                    entry['non'] = 0;
                    achiev_res_date_arr.push(entry);
                }
            }

            var index = achiev_res_date_arr.length - 1;

            switch (value['result']) {
                case "failed":
                    achiev_res_date_arr[index]['fail'] += 1;
                    break;
                case "passed":
                    achiev_res_date_arr[index]['pass'] += 1;
                    break;
                case "nonapplicable":
                    achiev_res_date_arr[index]['non'] += 1;
                    break;
                default:
                    console.log("unknown result: " + value['result']);
                    break;
            }
        });

        var mult = singularToMult(achiev_res_date_arr);

        $scope.graphTestResultData = [
        {
            "key" : "Passed" ,
                "values" : mult['pass']
        },

        {
            "key" : "Failed" ,
            "values" : mult['fail']
        },

        {
            "key" : "Non Applicable" ,
            "values" : mult['non']
        }
        ];

    };

function updateVaritiesData(res) {
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
        console.log($scope.varieties)
    });
};

HippodDataService.getAchievements($scope.id, $scope.sub_id).then(function(res) {
    updateVaritiesData(res);
    updateAchievementChart(res);
});

function formatCategories(cat_arr) {
    var ret_str = "";
    angular.forEach(cat_arr, function(v, k) {
        ret_str += '<span class="glyphicon glyphicon-menu-right"></span> ' + v;
    });
    return ret_str;
};

function formatTags(tags_arr) {
    var ret_str = "";
    angular.forEach(tags_arr, function(v, k) {
        ret_str += " " + v;
    });
    return ret_str;
};

function formatReferences(ref_arr) {
    var ret_str = "";
    angular.forEach(ref_arr, function(v, k) {
        ret_str = " " + v;
    });
    return ret_str;
};

DBService.getFoo($scope.id, $scope.sub_id).then(function(res) {
    $scope.data = res;
    console.log(res)
    if ('object-attachment' in res){
        $scope.responsible = res['object-attachment']['responsible'];
        $scope.tags        = formatTags(res['object-attachment']['tags']);
        $scope.references  = formatReferences(res['object-attachment']['references']);
        $scope.date_added  = humanFormatDateYYYYMMDDHHMM(res['object-attachment']['date-added']);
        }
    $scope.categories  = formatCategories(res['object-item']['categories']);
    $scope.conflict = res['conflict'];
    $scope.latest_index = res['latest_index'];
    $scope.index = res['requested-index']
    console.log($scope.index)
});

$scope.graphTestResultOptions = {
    chart: {
        type: 'multiBarChart',
        height: 160,
        margin : {
            top: 0,
            right: 10,
            bottom: 30,
            left: 5
        },
        stacked: true,
        x: function(d){return d[0];},
        y: function(d){return d[1];},
        useVoronoi: false,
        clipEdge: true,
        duration: 100,
        useInteractiveGuideline: true,
        xAxis: {
            showMaxMin: false,
            tickFormat: function(d) {
                return d3.time.format('%Y-%m-%d')(new Date(d))
            }
        },
        yAxis: {
            tickFormat: function(d){
                return d3.format(',.0f')(d);
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


});
