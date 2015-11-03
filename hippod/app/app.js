var hippoD = angular.module('hippoDApp', ['ui.router', 'ui.bootstrap']);

hippoD.config(function($stateProvider, $urlRouterProvider) {

	$urlRouterProvider.otherwise('/');

	$stateProvider
        .state('dashboard', {
            url: '/',
            templateUrl: 'templates/home.html'
        })

        .state('items', {
            url: '/items',
            templateUrl: 'templates/items.html'
        })

        .state('admin', {
            url: '/admin',
            templateUrl: 'templates/admin.html',
						controller: 'AdminCtrl'
        });
        
});
