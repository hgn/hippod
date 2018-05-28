"use strict";

hippoD.controller("ReportCtrl", function($scope, ReportService, GetReportsService) {
    $scope.report_filter = "Latest Tests";
    $scope.filter_actions = ["Latest Tests", "Anchored Tests"];

    // function createReport(filter) {
    //     switch(filter){
    //         case "Latest Tests": return "latest";
    //         case "Anchored Tests": return "anchored";
    //         default
    //     }

    $scope.filter_change = function(name){
            $scope.report_filter = name;
        }

    $scope.create = function() {
        ReportService.createReport($scope.report_filter)
    }

    GetReportsService.getReports().then(function(response){
        $scope.reports_list = response
        })
});