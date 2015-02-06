/* Angular JS */
var dispatchApp = angular.module('dispatchApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

dispatchApp.controller('Controller', ['$scope', '$http', '$timeout', function ($scope, $http, $timeout){

  $scope.requests = [];
  $scope.mentors = [];
  $scope.assignedRequests = [];
  $scope.assignedPairs = [];
  $scope.assignedMentors = [];


  $scope.currentMentor = null;

  $scope.request = {};

  $scope.poll = function() {
      $timeout(function() {
          $scope.getRequests();
          $scope.getAssignedMentors();
          //check if new data
          $scope.poll();
      }, 5000);
  };

  $scope.poll();

  $scope.getRequests = function() {
    $http.get('/dashboard/mentor_dispatch/get_requests').
      success(function(response) {
        $scope.requests = response.requests;
      }).error(function(error) {
        console.log(error);
      });
  }

  $scope.viewRequest = function(request) {
    $http.get('/dashboard/mentor_dispatch/request/' + request.id).
      success(function(response) {
        $scope.request = response.request;
        $scope.mentors = response.mentors;
        $scope.currentMentor = null;
        console.log(response);
      }).error(function(error) {
        console.log(error);
      });
  }

  $scope.viewAssignedRequest = function(request) {

      $scope.request = request;

      var matchedPairs = $.grep($scope.assignedPairs, function(pair){ return pair.request == request.id; });

      if (matchedPairs.length > 0) {
        var mentor = matchedPairs[0].mentor;
        $scope.currentMentor = $.grep($scope.assignedMentors, function(m){return m.id == mentor;})[0];
      } else {
        $scope.currentMentor = null;
      }

  }

  $scope.viewMentor = function(mentor) {
    $scope.currentMentor = mentor;
    if (mentor.assigned) {
      var matchedPairs = $.grep($scope.assignedPairs, function(pair){ return pair.mentor == mentor.id; });
      if (matchedPairs.length > 0) {
        var request = matchedPairs[0].request;

        $scope.request = $.grep($scope.assignedRequests, function(r){return r.id == request;})[0];
      } else {
        $scope.request = {};
      }
    }
  }

  $scope.pair = function() {
    $http.post('/dashboard/mentor_dispatch', {mentor : $scope.currentMentor.id, request : $scope.request.id}).
      success(function(response) {
        $scope.getRequests();
        $scope.mentors = [];
        $scope.request = {};

      }).error(function(error) {
        console.log(error);
      });
  }

  $scope.unpair = function() {
    console.log('unpair');
  }

  $scope.getAssignedMentors = function() {
    $http.get('/dashboard/mentor_dispatch/assigned').
      success(function(response) {
        $scope.assignedMentors = response.assigned_mentors;
        $scope.assignedRequests = response.assigned_requests;
        $scope.assignedPairs = response.pairs;
      }).error(function(error) {
        console.log(error);
      });
  }

}]);


