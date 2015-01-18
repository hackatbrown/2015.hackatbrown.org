var checkinApp = angular.module('checkinApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);


checkinApp.controller('Controller', ['$scope', '$http', function ($scope, $http){
  $scope.showMissingInfo = false;
  $scope.missingInfo = ['phone_number'];

  $scope.showReminders = false;
  $scope.reminders = ['Remind this hacker about food or something.', 'Remind this hacker that travel receipts are due on 1.2.2015'];

  $scope.showStatus = false;
  $scope.hacker = {};


  $scope.requestMoreInfo = function() {
    console.log('called');
    $.ajax({
      type: 'GET',
      url: '/checkin/info/' + $scope.hackerID,
      success : function(response) {
        response = JSON.parse(response);
        console.log(response);
        $scope.hacker = response.hacker;
        var missingInfo = response.missingInfo;
        $scope.showStatus = !!missingInfo;
        $scope.showMissingInfo = $scope.showStatus;
        $scope.showReminders = true;

      },
      error: function(error) {
        console.log('error');
        console.log(error);
      }
    });
  }

  $scope.checkinHacker = function() {
    $.ajax({
      type: 'POST',
      url: '/checkin',
      data: {'id' : $scope.hackerID},
      success: function(response) {
        console.log(response);
      },
      error: function(error) {
        console.log('error');
        console.log(error);
      }
    });
  }


}]);


