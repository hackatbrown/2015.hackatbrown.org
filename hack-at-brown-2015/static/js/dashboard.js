var dashApp = angular.module('dashApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

var breakdownsApp = angular.module('breakdownsApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

breakdownsApp.controller('MainCtrl', ['$scope', '$http', function ($scope, $http){

  $scope.schools = {};

}]);


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

  $scope.showBreakdowns = false;

  $scope.charts = [{
      name : 'By School',
      value : 'school',
      hc_type : 'pie'
    }, {
      name : 'By Shirt Size',
      value : 'shirt',
      hc_type : 'pie'
    }, {
      name : 'By Dietary Restrictions',
      value : 'diet',
      hc_type : 'pie'
    }, {
      name : 'By Gender',
      value : 'gender',
      hc_type : 'pie'
    }, {
      name : 'By Year',
      value : 'year',
      hc_type : 'pie'
    }, {
      name : 'First Hackathon',
      value : 'first_hackathon',
      hc_type : 'pie'
    }, {
      name : 'Hardware Hackers',
      value : 'hardware_hack',
      hc_type : 'pie'
    }, {
      name : 'By Status',
      value : 'status',
      hc_type : 'pie'
    }];
  $scope.currentChart = $scope.charts[0];
  $scope.showChartStatus = false;
  $scope.chartStatus = "";

  $scope.getContent = function (option) {
    return 'PLACEHOLDER'
  };

  $scope.getStats = function () {

    $http({method: 'GET', url: '/__get_dash_stats'}).
        success(function(data, status) {
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
      return;
    };

    $http.post('/__manual', {change: action, emails: emails}).
    success(function(data, status, headers, config) {
        $scope.manualStatus = action + " Success!";
        $scope.showManualStatus = true;
    }).
    error(function(data, status, headers, config) {
      $scope.manualStatus = action + " failed..."
      $scope.showManualStatus = true;
    });

  };

  $scope.lookupHacker = function(){
    $scope.manualEmails = $scope.manualEmails.toLowerCase();
    emails = $scope.manualEmails.trim().replace(/\s+/g, '');
    $http({method: 'GET', url: '/__lookup_hacker/' + emails}).
        success(function(data) {
          $scope.lookupResult = data;
        }).
        error(function(data) {
          $scope.manualStatus = data;
          $scope.showManualStatus = true;
        });
  };


  $scope.getBreakdowns = function(){
    $scope.showBreakdowns = !$scope.showBreakdowns;
    if ($scope.schools){
      return;
    }
    $http({method: 'GET', url: '/__breakdown/' + "all"}).
        success(function(data, status) {


          if (data != "null") {
            $scope.schools = data.schools;
            $scope.shirts = data.shirts;
            $scope.hardware = data.hardware;
            $scope.firstHack = data.firstHack;
            $scope.diet = data.diet;
            $scope.years = data.year;
          }

        }).
        error(function(data, status) {
          $scope.data = data || "Request failed";
          $scope.status = status;

      });
  }

  $scope.populateCharts = function() {

    $http({method: 'GET', url: '/__breakdown/' + $scope.currentChart.value}).
        success(function(data, status) {
          $scope.showChartStatus = (data == "null");
          $scope.chartStatus = (data == "null") ? "Could not load chart data" : "";
          $('#chart_1').toggle(data != "null");

          console.log(data);

          if (data != "null") {
            var series = [];
            $.each(data, function(key, value) {
              series.push({"name" : key, "y": value});
            });
            $('#chart_1').highcharts({
                  title : {
                    text : $scope.currentChart.name
                  },
                  series: [{
                      type : $scope.currentChart.hc_type,
                      name: 'Hackers',
                      data: series
                  }]
                });
          }
        }).
        error(function(data, status) {
          $scope.data = data || "Request failed";
          $scope.status = status;

      });

  };

}]);
