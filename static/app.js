var hippoD = angular.module('hippoDApp', ['ui.router', 'ui.bootstrap', 'nvd3', 'angular-loading-bar']);

hippoD.config(function($stateProvider, $urlRouterProvider) {

	$urlRouterProvider.otherwise('/');

	$stateProvider
        .state('dashboard', {
            url: '/',
            templateUrl: 'static/templates/home.html',
            controller: 'DashboardCtrl'
        })

        .state('items', {
            url: '/items',
            templateUrl: 'static/templates/items.html',
            controller: 'ItemsCtrl'
        })

        .state('achievement', {
					url: '/item/:id/:sub_id/:achievement_id',
            templateUrl: 'static/templates/achievement.html',
            controller: 'AchievementCtrl'
        })

        .state('item', {
                    url: '/item/:id/:sub_id',
            templateUrl: 'static/templates/item.html',
            controller: 'ItemCntrl'
        })

        .state('admin', {
            url: '/admin',
            templateUrl: 'static/templates/admin.html',
            controller: 'AdminCtrl'
        })

        .state('report', {
            url: '/report',
            templateUrl: 'static/templates/report.html',
            controller: 'ReportCtrl'
        });
});
