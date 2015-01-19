$(document).on('keyup', function(event) {
  if (event.which == 13) {
    angular.element($('#scope')).scope().checkinHacker();
  }
});

var checkinApp = angular.module('checkinApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);


checkinApp.controller('Controller', ['$scope', '$http', function ($scope, $http){
  $scope.missingInfo = null;

  $scope.reminders = null;

  $scope.showStatus = null;
  $scope.hacker = {};


  $scope.requestMoreInfo = function() {
    if ($scope.hackerID === "") {
      return;
    }

    $http.get('/checkin/info/' + $scope.hackerID).
      success(function(response) {
        $scope.hacker = response.hacker;
        console.log($scope.hacker);
        response.missingInfo = [];
        $scope.missingInfo = response.missingInfo;
        $scope.reminders = ['Remind this hacker about food or something.', 'Remind this hacker that travel receipts are due on 1.2.2015'];

        $scope.showStatus = $scope.missingInfo.length === 0;
      }).
      error(function(error) {
        console.log('error');
        console.log(error);
      });
  }

  $scope.checkinHacker = function() {
    console.log('neh');
    return;
    $http.post('/checkin', {'id' : $scope.hackerID}).
      success(function(response) {
        console.log(response);
      }).
      error(function(error) {
        console.log('error');
        console.log(error);
      });
  }


}]);


