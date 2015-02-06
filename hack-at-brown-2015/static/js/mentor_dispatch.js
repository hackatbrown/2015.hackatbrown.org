/* Angular JS */
var dispatchApp = angular.module('dispatchApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

dispatchApp.controller('Controller', ['$scope', '$http', '$timeout', function ($scope, $http, $timeout){

  $scope.requests = [];
  $scope.mentors = [];
  $scope.currentMentor = null;

  $scope.request = {
    requester : 'Sam',
    requester_email : 'sam@brown.edu',
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
      }, 5000);
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

  $scope.viewMentor = function(mentor) {
    console.log(mentor);
    $scope.currentMentor = mentor;
  }

  $scope.pair = function() {
    $http.post('/dashboard/mentor_dispatch', {mentor : $scope.currentMentor.id, request : $scope.request.id}).
      success(function(response) {
        console.log(response);
        $scope.getRequests();
      }).error(function(error) {
        console.log(error);
      });

  }

}]);


