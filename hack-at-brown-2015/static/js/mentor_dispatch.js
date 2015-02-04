/* Angular JS */
var dispatchApp = angular.module('dispatchApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

dispatchApp.controller('Controller', ['$scope', '$http', function ($scope, $http){

}]);


