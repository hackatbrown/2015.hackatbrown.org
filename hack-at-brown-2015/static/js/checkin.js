/* Vanilla JS */
function onMessage(message) {
    angular.element($('#scope')).scope().updateTotal(message.data);
}

/* Angular JS */
var checkinApp = angular.module('checkinApp', ['ngAnimate']).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

checkinApp.directive('shortcut', function() {
  return {
    restrict: 'E',
    replace: true,
    scope: true,
    link:    function postLink(scope, iElement, iAttrs){
      $(document).on('keyup', function(e){
         scope.$apply(scope.keyPressed(e));
       });
    }
  };
});

checkinApp.animation('.slide-animation', function() {
  return {
    addClass: function(element, className, done) {
      if(className == 'ng-hide') {
        $(element).stop().show().slideToggle(200, 'swing', done);
//        $(element).stop().hide().slideToggle(200, 'swing', done);
      }
    },
    removeClass : function(element, className, done) {
      if(className == 'ng-hide') {
        $(element).stop().hide().slideToggle(200, 'swing', done);
//        $(element).stop().show().slideToggle(200, 'swing', done);
      }
    },
    leave: function(element, done) {
      console.log('left');
    },
    enter: function(element, done) {
      console.log('enered');
    }
  };
});

checkinApp.controller('Controller', ['$scope', '$http', function ($scope, $http){
  $scope.missingOptionalInfo = null;
  $scope.requiredInfo = null;
  $scope.reminders = null;

  $scope.showStatus = null;
  $scope.hacker = {};

  $scope.notification;

  $scope.session_checked_in = 0;
  $scope.total_checked_in = initial_total_checked_in;

  $scope.keyPressed = function(event) {
    if (!event.ctrlKey)
      return;

    switch (event.which) {
      case 13:
        $scope.checkinHacker();
        break;
      case 72: //'h'
        $scope.createPerson('Hacker');
        break;
      case 86: //'v'
        $scope.createPerson('Volunteer');
        break;
      case 82: //'r'
        $scope.createPerson('Rep');
        break;
      case 73: //'i'
        $scope.createPerson('Visitor');
        break;
      case 83: //'s'
        searchBar.focus();
        break;
    }
  }

  $scope.requestMoreInfo = function() {
    $scope.clearNotifications();
    $scope.newPerson = false;
    if ($scope.hackerID === "") {
      $scope.hacker = {};
      $scope.missingOptionalInfo = null;
      $scope.requiredInfo = null;
      $scope.reminders = null;
      $scope.showStatus = null;
      return;
    }

    $scope.collectedInfo = {};
    $http.get('/checkin/info/' + $scope.hackerID).
      success(function(response) {
        $scope.hacker = response.hacker;
      $scope.showStatus = true;
      if(!$scope.hacker.checked_in) {

        $scope.missingOptionalInfo = (response.missingOptionalInfo.length > 0) ? response.missingOptionalInfo : null;

        $scope.requiredInfo = (Object.keys(response.requiredInfo).length > 0) ? response.requiredInfo : null;

        $scope.reminders = response.reminders;

        $scope.showCheckin = !$scope.requiredInfo;

        if($scope.requiredInfo) {

          setTimeout(function() {
            $("input[type=tel]").mask("(999) 999-9999");
            $('#required-info input')[0].focus();
          }, 100);
        }
      }
      }).
      error(function(error) {
        console.log(error);
        $scope.notify('Error!');
      });
  }

  $scope.clearNotifications = function() {
    $scope.notify("");
  }
  $scope.notify = function(message) {
    $scope.notification = message;
  }

  $scope.checkinHacker = function() {
    if ($scope.hackerID === '') {
      console.log('id is null');
      return;
    }

    if (!$scope.showCheckin) {
      $scope.notify("You must obtain the required info before you can check in.");
      return;
    }

    if ($scope.hacker.id !== $('#search').val()) {
      //We need this so the enter event when selecting doesn't checkin people
      return;
    }

    if ($scope.hacker.checked_in ) {
      $scope.notify("Already Checked In");
      return;
    }

    if (!($scope.hacker.status == "confirmed" || $scope.hacker.status == 'waitlisted')) {
      $scope.notify('Status Not Confirmed')
      return;
    }

    //TODO: update source in selectize
    // w/ hacker.checked_in = true;

    $http.post('/checkin', {'id' : $scope.hackerID}).
      success(function(response) {
        if (!response.success) {
          return;
          $scope.notify(response.msg);
        }

        $scope.hacker.checked_in = true;
        $scope.reminders = false;
        $scope.missingOptionalInfo = false;
        $scope.requiredInfo = false;
        $scope.showCheckin = false;
        $scope.hacker.status = 'checked in';
        $scope.total_checked_in = response.total_checked_in;
        $scope.session_checked_in++;
      searchBar.focus();
      }).
      error(function(error) {
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
    $scope.showCheckin = null;
    $scope.hacker = {};
    $search[0].selectize.clear();

    var requiredFields = ['email', 'name'];
    switch (kind) {
      case 'Hacker':
        requiredFields = requiredFields.concat(['phone_number']);
        break;
      case 'Visitor':
        requiredFields = requiredFields.concat(['org']);
        break;
      case 'Volunteer':
        requiredFields = requiredFields.concat(['role', 'phone_number', 'shirt_gen', 'shirt_size']);
        break;
      case 'Rep':
        requiredFields = requiredFields.concat(['company', 'phone_number', 'shirt_gen', 'shirt_size']);
        break;
      default:
        console.log('not a thing');
        return;
    }

    $scope.newPerson = {'kind' : kind, 'fields' : requiredFields};

    setTimeout(function() {$('#newPerson-email').focus();}, 100);
  }

  $scope.cancelPerson = function() {
    $scope.$apply(function() {
      $scope.newPerson = null;
    });
  }

  $scope.submitNewPerson = function() {

    function failure(msg) {
      $scope.notify("Could not create person: " + msg);
    }

    $http.post('/checkin/new', $scope.newPerson).
      success(function(response) {
        if (response.success) {
          $scope.notify("Created and checked in!");
        } else {
          failure(response.msg);
        }
        $scope.newPerson = null;
      }).
      error(function(error) {
        console.log('error');
        failure(error);
      });
  }

  $scope.requiredHandled = function() {
   if ($.isEmptyObject($scope.collectedInfo)) {
       $scope.requiredInfo = null;
       $scope.showStatus = true;
       $scope.showCheckin = true;
       return;
   }

    $scope.collectedInfo['id'] = $scope.hackerID;
    $http.post('/checkin/requiredInfo', $scope.collectedInfo).
      success(function(response) {
        if (response.success) {
          $scope.requiredInfo = null;
          $scope.showStatus = true;
          $scope.showCheckin = true;
          $scope.notify('Saved!');
        } else {
          $scope.notify('Invalid Number');
        }
      }).
      error(function(error) {
        $scope.collectedInfo = {};
      });

  }
}]);




