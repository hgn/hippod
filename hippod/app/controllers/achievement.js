"use strict";

hippoD.controller("AchievementCtrl", function ($scope, $stateParams, AchievementService) {

	$scope.id = $stateParams.id;
    $scope.sub_id = $stateParams.sub_id;
	$scope.achievement = $stateParams.achievement_id;

    AchievementService.getAchievement($scope.id, $scope.sub_id, $scope.achievement).then(function(res){
        $scope.data = res.data.data.data;
        var data = $scope.data;
        var data_ids = get_data_id(data);
        var types = get_type(data);
        var shown_data = check_data_types(types);
        $scope.data_ids_scope = sanitize_ids(data_ids, shown_data);
        $scope.types_scope = sanitize_types(types, shown_data);
    })

    AchievementService.getAttachment($scope.id, $scope.sub_id).then(function(res){
        $scope.data_attach = res;
        console.log(res)
    })

    function get_type(data) {
        var extensions = new Array();
        for (var i=0; i < data.length; i++){
            var filename = data[i]['name'];
            var extension = filename.substr(filename.lastIndexOf('.')+1)
            extensions.push(extension);
            }
        return extensions
    }

    function get_data_id(data) {
        var data_ids = new Array();
        for (var i=0; i < data.length; i++){
            var data_id = data[i]['data-id'];
            data_ids.push(data_id)
        }
        return data_ids
    }

    function check_data_types(types){
        var shown_data = new Array()
        for (var i=0; i < types.length; i++){
            switch(types[i]){
                case 'png':
                    shown_data.push(true);
                    break;
                case 'jpeg':
                    shown_data.push(true);
                    break;
                case 'jpg':
                    shown_data.push(true);
                    break;
                default:
                    shown_data.push(false);
                    break;
                }
        }
        return shown_data
    }

    function sanitize_ids(data_ids, shown_data) {
        var sanitized_ids = new Array()
        for(var i=0; i < data_ids.length; i++){
            if (shown_data[i] == true){
                sanitized_ids.push(data_ids[i])
            }
        }
        return sanitized_ids
    }

    function sanitize_types(types, shown_data) {
        var sanitized_types = new Array()
        for(var i=0; i < types.length; i++){
            if (shown_data[i] == true){
                sanitized_types.push(types[i])
            }
        }
        return sanitized_types
    }
});
