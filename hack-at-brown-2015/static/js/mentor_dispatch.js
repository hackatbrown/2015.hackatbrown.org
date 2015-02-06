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

  $scope.pair = {
    mentor : null,
    request : null,
    id : ''
  };

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
        $scope.pair.request = response.request;
        $scope.mentors = response.mentors;
        $scope.pair.mentor = null;
      }).error(function(error) {
        console.log(error);
      });
  }

  $scope.viewAssignedRequest = function(request) {
      $scope.pair.request = request;
      $scope.getMatch(request.id, false);
  }

  $scope.getMatch = function(id, isMentor) {
    var matchedPairs = $.grep($scope.assignedPairs, function(pair){
      return pair[(isMentor ? 'mentor' : 'request')] == id;
    });

    if (matchedPairs.length == 0) {
      console.log('no match');
      return;
    }

    var matchedPair = matchedPairs[0];
    var matchedID = matchedPair[(isMentor ? 'request' : 'mentor')];
    var counterParts = isMentor ? $scope.assignedRequests : $scope.assignedMentors;

    var out = $.grep(counterParts, function(cp){
      return cp.id == matchedID;
    });

    if (out.length == 0) {
      return;
    }

    $scope.pair[(isMentor ? 'request' : 'mentor')] = out[0];
    $scope.pair.id = matchedPair.id;
  }

  $scope.viewMentor = function(mentor) {
    $scope.pair.mentor = mentor;
    if (mentor.assigned) {
      $scope.getMatch(mentor.id, true);
    }
  }

  $scope.sendPair = function() {
    console.log('pair');
    $http.post('/dashboard/mentor_dispatch', {mentor : $scope.pair.mentor.id, request : $scope.pair.request.id}).
      success(function(response) {
        $scope.getRequests();
        $scope.mentors = [];
        $scope.pair.request = null;

      }).error(function(error) {
        console.log(error);
      });
  }

  $scope.unpair = function() {
    $scope.form['id'] = $scope.pair.id;
    $http.post('/dashboard/mentor_dispatch/unpair', $scope.form).
      success(function(response) {
        $scope.pair = {};
        console.log(response);
      }).error(function(error) {
        console.log(error);
      });
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


