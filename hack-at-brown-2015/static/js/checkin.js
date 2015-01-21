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

  $scope.session_checked_in = 0;
  //TODO: animate counter
  $scope.total_checked_in = initial_total_checked_in;

  $scope.requestMoreInfo = function() {
    if ($scope.hackerID === "") {
      return;
    }

    $http.get('/checkin/info/' + $scope.hackerID).
      success(function(response) {
        $scope.hacker = response.hacker;
        console.log(response);

        $scope.missingOptionalInfo = (response.missingOptionalInfo.length > 0) ? response.missingOptionalInfo : null;

        $scope.requiredInfo = (response.requiredInfo.length > 0) ? response.requiredInfo : null;

        $scope.reminders = response.reminders;
        $scope.showStatus = !$scope.requiredInfo
      }).
      error(function(error) {
        console.log('error');
        console.log(error);
      });
  }

  $scope.checkinHacker = function() {
    if (!$scope.showStatus || $scope.hackerID === '') {
      console.log('no status or id is null');
      return;
    }

    if ($scope.hacker.id !== $('#search').val()) {
      console.log("didn't update id");
      return;
    }

    if ($scope.hacker.status != "confirmed") {
      console.log('status not confirmed');
    }

    if ($scope.hacker.checked_in) {
      console.log('already checked in');
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
      // $scope.total_checked_in = newTotal;
      $scope.total_checked_in++;
    });
  }

  $scope.createPerson = function(kind) {
    var requiredFields = ['email'];
    switch (kind) {
      case 'Hacker':
        break;
      case 'Volunteer':
        //TODO: lock this down.
        requiredFields = requiredFields.concat(['name', 'team/role']);
        break;
      case 'Mentor':
        requiredFields = requiredFields.concat(['name', 'company']);
        break;
    }

    $scope.newPerson = {'kind' : kind, 'fields' : requiredFields};
  }

  $scope.submitNewPerson = function() {
    console.log('hey');
    console.log($scope.newPerson);


    $scope.newPerson = null;
  }

}]);


