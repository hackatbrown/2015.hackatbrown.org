var dashApp = angular.module('dashApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

dashApp.controller('MainCtrl', ['$scope', '$http', function ($scope, $http){
  $scope.content = "";
  $scope.header = "";
  $scope.emailSubject = "";
  $scope.emailBody = "";

  $scope.manualEmails = ""

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
      console.log("successfully sent emails");
      console.log(data.recipients)
    }).
    error(function(data, status, headers, config) {
      console.log('failed to send emails')
    });

  };

  $scope.changeStatus = function(){
    emails = $scope.manualEmails.trim().split(",");
    if (emails == []) {
      console.log("No recipients")
      return "Failed";
    };
    $http.post('/__manual', {emails: emails, subject: $scope.emailSubject,body:$scope.emailBody }).
    success(function(data, status, headers, config) { 
      if (data.success){
        console.log("successfully changed status for emails");
      }
      else
        console.log("failed to change status");
      
    }).
    error(function(data, status, headers, config) {
      console.log('failed to send change status')
    });

  };
}]);