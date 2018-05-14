"use strict";

hippoD.controller("AchievementCtrl", function ($scope, $stateParams, AchievementService) {

	$scope.id = $stateParams.id;
    $scope.sub_id = $stateParams.sub_id;
	$scope.achievement = $stateParams.achievement_id;

    AchievementService.getAchievement($scope.id, $scope.sub_id, $scope.achievement).then(function(res){
        $scope.response = res.data.data;
        $scope.data = res.data.data.data;
        var data = $scope.data;
        var data_ids = get_data_id(data);
        var formats = get_format(data);
        var shown_data = check_data_types(formats);
        $scope.data_ids_scope = sanitize_ids(data_ids, shown_data);
        $scope.types_scope = sanitize_formats(formats, shown_data);
    })

    AchievementService.getAttachment($scope.id, $scope.sub_id, $scope.achievement).then(function(res){
        $scope.data_attach = res;
    })

    function get_format(data) {
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
            var type = data[i]['type']
            data_ids.push({'data-id': data_id,
                            'type': type });
        }
        return data_ids
    }

    function check_data_types(formats){
        var shown_data = new Array()
        for (var i=0; i < formats.length; i++){
            switch(formats[i]){
                case 'png':
                    shown_data.push(true);
                    break;
                case 'jpeg':
                    shown_data.push(true);
                    break;
                case 'jpg':
                    shown_data.push(true);
                    break;
                case 'gif':
                    shown_data.push(true);
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
                sanitized_ids.push({'data-id': data_ids[i]['data-id'],
                                    'type': data_ids[i]['type'] })
            }
        }
        return sanitized_ids
    }

    function sanitize_formats(formats, shown_data) {
        var sanitized_formats = new Array()
        for(var i=0; i < formats.length; i++){
            if (shown_data[i] == true){
                sanitized_formats.push(formats[i])
            }
        }
        return sanitized_formats
    }
});
