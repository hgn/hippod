"use strict";

hippoD.controller("ReportCtrl", function($scope, ReportService) {
    $scope.report_filter = "Latest Tests";
    $scope.filter_actions = ["Latest Tests", "Anchored Tests"];
    console.log($scope.report_filter);

    // function createReport(filter) {
    //     switch(filter){
    //         case "Latest Tests": return "latest";
    //         case "Anchored Tests": return "anchored";
    //         default
    //     }

    $scope.filter_change = function(name){
            $scope.report_filter = name;
        }

    ReportService.createReport($scope.report_filter).then(function(res) {
        
    })
    
})