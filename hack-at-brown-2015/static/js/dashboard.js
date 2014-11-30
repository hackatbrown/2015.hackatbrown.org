var dashApp = angular.module('dashApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

dashApp.controller('MainCtrl', ['$scope', '$http', function ($scope, $http){
  $scope.content = "";
  $scope.header = "";

  $scope.showEmailStatus = false;
  $scope.emailStatus = ""
  $scope.emailSubject = "";
  $scope.emailBody = "";

  $scope.showManualStatus = false;
  $scope.manualStatus = "";
  $scope.manualEmails = "";

  $scope.signupCount = 0;
  $scope.registerCount = 0;
  $scope.acceptedCount = 0;
  $scope.waitlistCount = 0;
  $scope.declinedCount = 0;
  $scope.getContent = function (option) {
    return 'PLACEHOLDER'
  };

  $scope.getStats = function () {

    $http({method: 'GET', url: '/__get_dash_stats'}).
        success(function(data, status) {
          console.log('successfully hit __get_dash_stats!')
          $scope.status = status;
          $scope.signupCount = data.signup_count;
          $scope.registerCount = data.registered_count;
          $scope.acceptedCount = data.accepted_count;
          $scope.waitlistCount = data.waitlist_count;
          $scope.declinedCount = data.declined_count;
        }).
        error(function(data, status) {
          console.log('failed to hit __get_dash_stats')
          $scope.data = data || "Request failed";
          $scope.status = status;
      });
        //return $scope.signup_count;
  };

  $scope.sendEmails = function(){
    if ($scope.emailSubject == "" || $scope.emailBody == "" || $scope.emailOption == "unselected") {
      console.log("Failed")
      return "Failed";
    };
    $http.post('/__send_email', {recipients: $scope.emailOption, subject: $scope.emailSubject,body:$scope.emailBody }).
    success(function(data, status, headers, config) { 
      console.log("sent emails!");
      $scope.emailStatus = "Sent Email to " + $scope.emailOption + "!";
      $scope.showEmailStatus = true;
    }).
    error(function(data, status, headers, config) {
      console.log('failed to send emails');
      $scope.emailStatus = "Send failed...";
      $scope.showEmailStatus = true;
    });

  };

  $scope.changeStatus = function(action){
    emails = $scope.manualEmails.trim().split(",");
    if (emails == []) {
      console.log("No recipients")
      return;
    };

    $http.post('/__manual', {change: action, emails: $scope.emails}).
    success(function(data, status, headers, config) { 
        console.log("successfully changed status for emails");
        $scope.manualStatus = action + " Success!";
        $scope.showManualStatus = true;
    }).
    error(function(data, status, headers, config) {
      console.log('failed to send change status')
      $scope.manualStatus = action + " failed..."
      $scope.showManualStatus = true;
    });

  };
}]);