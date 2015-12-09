var hippoD = angular.module('hippoDApp', ['ui.router', 'ui.bootstrap', 'nvd3', 'angular-loading-bar']);

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

        .state('achievement', {
					url: '/item/:id/:achievement_id',
            templateUrl: 'templates/achievement.html',
            controller: 'AchievementCtrl'
        })

        .state('item', {
					url: '/item/:id',
            templateUrl: 'templates/item.html',
            controller: 'ItemCtrl'
        })


        .state('admin', {
            url: '/admin',
            templateUrl: 'templates/admin.html',
            controller: 'AdminCtrl'
        });
        
});
