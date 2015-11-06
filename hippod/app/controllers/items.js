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
    $scope.data = res.data;
		console.log(res.data);
	}, function(error) {
		console.log(res);
	});


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
