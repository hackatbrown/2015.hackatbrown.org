/* Angular JS */
var dispatchApp = angular.module('dispatchApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

dispatchApp.controller('Controller', ['$scope', '$http', '$timeout', function ($scope, $http, $timeout){

  $scope.requests = [{
    created : 1,
    responses : 1,
    tags : ['Angular JS', 'Web', 'Node', "Javascript"],
    id : 1
  }, {
    created : 2,
    responses : 1,
    tags : ['Hats', "Java"],
    id : 2
  }, {
    created : 1,
    responses : 5,
    tags : ['Cats', "Rats"],
    id : 3
  }];

  $scope.mentors = [{
    rating : 1,
    responses : 2,
    tags : ['Angular.JS', 'Hats', 'Bats', 'Rats']
  }, {
    rating : 1,
    responses : 2,
    tags : ['Angular.JS', 'Hats', 'Bats', 'Rats']
  }, {
    rating : 1,
    responses : 2,
    tags : ['Angular.JS', 'Hats', 'Bats', 'Rats']
  }];

  $scope.request = {
    requester : 'Sam',
    location : 'Sayles',
    created : '1 hour ago',
    responses : '3',
    issue : 'lipsum',
    tags : ['a', 'b', 'c'],
    status : 'unassigned'
  };

  $scope.poll = function() {
      $timeout(function() {
          console.log('sup');
          $scope.getRequests();
          //check if new data
          $scope.poll();
      }, 500000);
  };

  $scope.poll();

  $scope.getRequests = function() {
    $http.get('/dashboard/mentor_dispatch/get_requests').
      success(function(response) {
        $scope.requests = response.requests;
        console.log(response);
      }).error(function(error) {
        console.log(error);
      });
  }

  $scope.viewRequest = function(request) {
    $http.get('/dashboard/mentor_dispatch/request/' + request.id).
      success(function(response) {
        $scope.request = response.request;
        $scope.mentors = response.mentors;
        console.log(response);
      }).error(function(error) {
        console.log(error);
      });
  }

}]);


