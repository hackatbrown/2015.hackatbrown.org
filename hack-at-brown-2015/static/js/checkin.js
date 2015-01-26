/* Vanilla JS */
function onMessage(message) {
    angular.element($('#scope')).scope().updateTotal(message.data);
}

/* Angular JS */
var checkinApp = angular.module('checkinApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

checkinApp.controller('Controller', ['$scope', '$http', function ($scope, $http){
  $scope.missingOptionalInfo = null;
  $scope.requiredInfo = null;
  $scope.reminders = null;

  $scope.showStatus = null;
  $scope.hacker = {};

  $scope.notification;

  $scope.session_checked_in = 0;
  $scope.total_checked_in = initial_total_checked_in;

  $scope.requestMoreInfo = function() {
    if ($scope.hackerID === "") {
      return;
    }

    $http.get('/checkin/info/' + $scope.hackerID).
      success(function(response) {
        $scope.hacker = response.hacker;
        $scope.missingOptionalInfo = (response.missingOptionalInfo.length > 0) ? response.missingOptionalInfo : null;

        $scope.requiredInfo = (Object.keys(response.requiredInfo).length > 0) ? response.requiredInfo : null;

        $scope.reminders = response.reminders;
        $scope.showStatus = !$scope.requiredInfo;
      }).
      error(function(error) {
        console.log('error');
        console.log(error);
      });
  }

  $scope.notify = function(message) {
    $scope.notification = message;
    setTimeout(function() {
      $scope.$apply(function() {
        $scope.notification = null;
      });
    }, 3000);
  }

  $scope.checkinHacker = function() {
    if ($scope.hackerID === '') {
      console.log('id is null');
      return;
    }

    if ($scope.requiredInfo) {
      $scope.notify("You must obtain the required info before you can check in.")
      return;
    }

    if ($scope.hacker.id !== $('#search').val()) {
      //We need this so the enter event when selecting doesn't checkin people
      return;
    }

    if ($scope.hacker.status != "confirmed") {
      $scope.notify('Status Not Confirmed')
      return;
    }

    if ($scope.hacker.checked_in) {
      $scope.notify("Already Checked In");
      return;
    }

    //TODO: update source in selectize
    // w/ hacker.checked_in = true;

    $http.post('/checkin', {'id' : $scope.hackerID}).
      success(function(response) {
        $scope.hacker.checked_in = true;
        $scope.hacker.status = 'checked in';
        $scope.total_checked_in = response.total_checked_in;
        $scope.session_checked_in++;
        console.log(response);
      }).
      error(function(error) {
        console.log('error');
        console.log(error);
      });
  }

  $scope.updateTotal = function(newTotal) {
    $scope.$apply(function() {
      $scope.total_checked_in = newTotal;
    });
  }

  $scope.createPerson = function(kind) {
    $scope.missingOptionalInfo = null;
    $scope.requiredInfo = null;
    $scope.reminders = null;
    $scope.showStatus = null;
    $scope.hacker = {};
    $search[0].selectize.clear();

    var requiredFields = ['email'];
    switch (kind) {
      case 'Hacker':
        break;
      case 'Visitor':
        requiredFields = requiredFields.concat(['name']);
        break;
      case 'Volunteer':
        //TODO: lock this down.
        requiredFields = requiredFields.concat(['name', 'team/role', 'phone number']);
        break;
      case 'Company Rep':
        requiredFields = requiredFields.concat(['name', 'company']);
        break;
    }

    $scope.newPerson = {'kind' : kind, 'fields' : requiredFields};
  }

  $scope.cancelPerson = function() {
    $scope.$apply(function() {
      $scope.newPerson = null;
    });
  }

  $scope.submitNewPerson = function() {

    $http.post('/checkin/new', $scope.newPerson).
      success(function(response) {
        $scope.notify("Success!");
        console.log('created');
        $scope.newPerson = null;
      }).
      error(function(error) {
        console.log('error');
        console.log(error);
      });



  }

  $scope.requiredHandled = function() {
    $scope.requiredInfo = null;
    $scope.showStatus = true;
  }

}]);


