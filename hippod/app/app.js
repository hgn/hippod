var hippoD = angular.module('hippoDApp', ['ui.router', 'ui.bootstrap', 'nvd3ChartDirectives']);

hippoD.config(function($stateProvider, $urlRouterProvider) {

	$urlRouterProvider.otherwise('/');

	$stateProvider
        .state('dashboard', {
            url: '/',
            templateUrl: 'templates/home.html',
            controller: 'DashboardCtrl'
        })

        .state('items', {
            url: '/items',
            templateUrl: 'templates/items.html',
            controller: 'ItemsCtrl'
        })

        .state('admin', {
            url: '/admin',
            templateUrl: 'templates/admin.html',
            controller: 'AdminCtrl'
        });
        
});
