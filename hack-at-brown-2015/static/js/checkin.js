var checkinApp = angular.module('checkinApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);


checkinApp.controller('Controller', ['$scope', '$http', function ($scope, $http){
  $scope.missingInfo = false;

  $scope.reminders = false;

  $scope.showStatus = false;
  $scope.hacker = {};


  $scope.requestMoreInfo = function() {
    $http.get('/checkin/info/' + $scope.hackerID).
      success(function(response) {
        $scope.hacker = response.hacker;
        $scope.missingInfo = response.missingInfo;
        $scope.reminders = ['Remind this hacker about food or something.', 'Remind this hacker that travel receipts are due on 1.2.2015'];

        $scope.showStatus = !$scope.missingInfo;
      }).
      error(function(error) {
        console.log('error');
        console.log(error);
      });
  }

  $scope.checkinHacker = function() {
    $http.post('/checkin', {'id' : $scope.hackerID})/
      success(function(response) {
        console.log(response);
      }).
      error(function(error) {
        console.log('error');
        console.log(error);
      });
  }


}]);


