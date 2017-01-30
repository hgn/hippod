"use strict";

function is_already_listed(data_id, id_memory) {
    var count_in_list = false
    for (var k = 0; k < id_memory.length; k++) {
        if (data_id in id_memory[k]) {
            var same_counter = id_memory[k][data_id]
            count_in_list = true
            }
        }
    return {count_in_list: count_in_list,
            same_counter: same_counter};
}

function get_name_case_snippet(name_item, data_id, num, id_memory) {
    var counter = num+"";
    counter = "00" + counter;
    var is_listed = is_already_listed(data_id, id_memory)
    var count_in_list = is_listed.count_in_list
    var same_counter = is_listed.same_counter
    if (!(count_in_list)) {
        if (name_item.includes(data_id)){
            // case of non-given name for snippet image
            name = name_item.replace(data_id, counter)
            var obj = {}
            obj[data_id] = counter
            id_memory.push(obj);
            num++
            }
        // case of snippet image with user given name
        else {name = name_item}
    } else{name = name_item.replace(data_id, same_counter)}

    return {num: num,
            name: name,
            id_memory: id_memory};
}

function get_name_case_data(name_item, data_id, num, id_memory) {
    var counter = num+"";
    counter = "00" + counter;
    var  is_listed = is_already_listed(data_id, id_memory)
    var count_in_list = is_listed.count_in_list
    var same_counter = is_listed.same_counter
    if (count_in_list){
        name = name_item.replace(data_id, same_counter)
        }
    else{
        if (name_item.includes(data_id)){
            name = name_item.replace(data_id, counter)
            var obj = {}
            obj[data_id] = counter
            id_memory.push(obj);
            num++
        }
        else{
            name = name_item;
            }
        }
    return {num: num,
            name: name,
            id_memory: id_memory};
}



hippoD.factory('ItemService', function($http) {

  var promise;
  var myService = {
    getItemList: function() {
      if ( !promise ) {
        var obj = { };
        obj['limit'] = 0;
        obj['ordering'] = "by-submitting-date-reverse";
        obj['filter-by-result'] = "all";
        obj['filter-by-maturity-level'] = "all";
        // $http returns a promise, which has a then function, which also returns a promise
        promise = $http(
{
        url: '/api/v1/objects-detail-last',
        dataType: 'json',
        method: 'POST',
        data: obj,
        headers: { "Content-Type": "application/json" }
    }
)


          .then(function (response) {
          // The then function here is an opportunity to modify the response
          // The return value gets picked up by the then in the controller.
          return response.data;
        });
      }
      // Return the promise to the controller
      return promise;
    }
  };
  return myService;
});


hippoD.factory('DBService', function($http) {
    return {
        getFoo:  function(id, sub_id){
                 var obj = {};
                 var promise = $http(
                         {
                             url: '/api/v1/object/' + id + '/' +  sub_id,
                             dataType: 'json',
                             method: 'POST',
                             data: obj,
                             headers: { "Content-Type": "application/json" }
                       })
                         .then(function(response){
                             var requested_index = response.data.data['requested-index'];
                             var subcontainer = response.data.data['subcontainer'];
                             var achievements = response.data.data['object-achievements'];
                             //for (var i = 0; i < achievements.length; i++) {
                             //}

                             if ('data' in subcontainer[requested_index]['object-item']) {
                             var item_data = subcontainer[requested_index]['object-item']['data'];
                             var attachments = new Array();
                             var num = 1;
                             var id_memory = new Array();
                             for (var i = 0; i < item_data.length; i++) {
                                 if (item_data[i]['type'] !== 'description') {
                                     var entry = {};
                                     var data_id = item_data[i]['data-id']
                                     entry['data-id'] = item_data[i]['data-id']
                                     entry['size-real'] = item_data[i]['size-real'];
                                     // exchange sha in name with an id_number
                                     // type entry helps to differentiate between data and snippt db
                                     if ('type' in item_data[i]) {
                                        entry['type'] = item_data[i]['type'];
                                        // case of snippet file
                                        var ret = get_name_case_snippet(item_data[i]['name'], data_id, num, id_memory)
                                        num = ret.num;
                                        entry['name'] = ret.name;
                                        id_memory =  ret.id_memory;
                                    } else {
                                        entry['type'] = 'undefined';
                                        var ret = get_name_case_data(item_data[i]['name'], data_id, num, id_memory)
                                        num = ret.num;
                                        entry['name'] = ret.name;
                                        id_memory = ret.id_memory;
                                    }
                                     attachments.push(entry);
                                 }
                             }
                            response.data.data['__attachments'] = attachments;

                             // fetch description
                             for (var i = 0; i < item_data.length; i++) {
                                 if (item_data[i]['type'] == 'description') {
                                     return $http(
                                             {
                                                 url: '/api/v1/data/' + item_data[i]['data-id'],
                                                 dataType: 'json',
                                                 method: 'POST',
                                                 data: obj,
                                                 headers: { "Content-Type": "application/json" }
                                             })
                                         .then(function (response_enc) {
                                                 var text = response_enc.data;
                                                 item_data[i]['data'] = text;
                                                 response.data.data['__description'] = text;
                                                 return response.data.data;
                                             });
                                 }
                             }}
                             return response.data.data;
                         })
        return promise
     }
    }
});


hippoD.factory('ReportService', function($http) {
    return {
        createReport: function(filter){
            var obj = {"type": filter}
            var promise = $http(
                {
                    url: '/api/v1/report',
                    dataType: 'json',
                    method: 'POST',
                    data: obj,
                    headers: {"Content-Type": "application/json"}
                })
        return promise
        }
    }
});


hippoD.factory('GetReportsService', function($http) {
    return {
        getReports: function(filter){
            var obj = {};
            var promise = $http(
                {
                    url: '/api/v1/get-reports',
                    dataType: 'json',
                    method: 'GET',
                    data: obj,
                    headers: {"Content-Type": "application/json"}
                })
                .then(function (response) {
                     var reports_list = response.data.data;
                     return response.data.data;
                 })
        return promise;
        }
    }
});


hippoD.factory('HippodDataService', function($http) {

    var getAchievements = function (core_id, sub_id) {

             var obj = {};
             var promise = $http(
                 {
                     url: '/api/v1/object/' + core_id + '/' + sub_id,
                     dataType: 'json',
                     method: 'POST',
                     data: obj,
                     headers: { "Content-Type": "application/json" }
               })
                 .then(function (response) {
                     var requested_index = response.data.data['requested-index']
                     var subcontainer = response.data.data['subcontainer'];
                     return subcontainer[requested_index]['object-achievements'];
                 })

                 return promise;

    };

    return {
        getAchievements: getAchievements
    };
});


hippoD.factory('AchievementService', function($http) {
    return{
     getAchievement: function (core_id, sub_id, achievement_id){
             var obj = {};
             var promise = $http(
                 {
                     url: '/api/v1/achievement/' + core_id + '/' + sub_id + '/' + achievement_id,
                     dataType: 'json',
                     method: 'GET',
                     data: obj,
                     headers: { "Content-Type": "application/json" }
               })
                 .then(function (response) {
                     return response;
                 })

                 return promise;
        },

    getAttachment:  function(id, sub_id, achiev_id){
                 var obj = {};
                 var promise = $http(
                         {
                             url: '/api/v1/object/' + id + '/' +  sub_id,
                             dataType: 'json',
                             method: 'POST',
                             data: obj,
                             headers: { "Content-Type": "application/json" }
                       })
                         .then(function(response){
                             var requested_index = response.data.data['requested-index'];
                             var subcontainer = response.data.data['subcontainer'];
                             var achievements = response.data.data['object-achievements'];
                             //for (var i = 0; i < achievements.length; i++) {
                             //}
                             var item_data = subcontainer[requested_index]['object-achievements'][achiev_id]['data'];
                             var attachments = new Array();
                             var num = 1;
                             var id_memory = new Array();
                             for (var i = 0; i < item_data.length; i++) {
                                 if (item_data[i]['type'] !== 'description') {
                                     var entry = {};
                                     var data_id = item_data[i]['data-id']
                                     entry['data-id'] = item_data[i]['data-id']
                                     entry['size-real'] = item_data[i]['size-real'];
                                     // exchange sha in name with an id_number
                                     // type entry helps to differentiate between data and snippt db
                                     if ('type' in item_data[i]) {
                                        entry['type'] = item_data[i]['type'];
                                        // case of snippet file
                                        var ret = get_name_case_snippet(item_data[i]['name'], data_id, num, id_memory)
                                        num = ret.num;
                                        entry['name'] = ret.name;
                                        id_memory =  ret.id_memory;
                                    } else {
                                        entry['type'] = 'undefined';
                                        var ret = get_name_case_data(item_data[i]['name'], data_id, num, id_memory)
                                        num = ret.num;
                                        entry['name'] = ret.name;
                                        id_memory = ret.id_memory;
                                    }
                                     attachments.push(entry);
                                 }
                             }
                            response.data.data['__attachments'] = attachments;
                        return response.data.data
                        })
                    return promise
                    }
    }
});


hippoD.filter('toHtmlSave', function($sce) {

    function replaceAll(str, find, replace) {
        if (!str)
            return str;
        return str.replace(new RegExp(find, 'g'), replace);
    }

    return function(text, argument) {

        // we correct the link from username (tomato.png) to
        // link: api/v1/data/34994393434934
        angular.forEach(argument, function(value, key) {
            text = replaceAll(text, value['name'],'api/v1/data/' + value['data-id']);
        });
        return $sce.trustAsHtml(text);
    };

});
