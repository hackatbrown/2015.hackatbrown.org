var dashApp = angular.module('dashApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

var breakdownsApp = angular.module('breakdownsApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);

breakdownsApp.controller('MainCtrl', ['$scope', '$http', function ($scope, $http){

  $scope.school = {};

}]);


dashApp.controller('MainCtrl', ['$scope', '$http', '$sce', function ($scope, $http, $sce){
  $scope.content = "";
  $scope.header = "";

  $scope.showEmailStatus = false;
  $scope.emailStatus = ""
  $scope.emailSubject = "";
  $scope.emailBody = "";

  $scope.showManualStatus = false;
  $scope.manualStatus = "";
  $scope.manualEmails = "";
  $scope.lookupResult = {found : [], notFound : []};

  $scope.signupCount = 0;
  $scope.registerCount = 0;
  $scope.acceptedCount = 0;
  $scope.confirmedCount = 0;
  $scope.waitlistCount = 0;
  $scope.declinedCount = 0;

  $scope.showBreakdowns = false;
  $scope.displayEmail = false;

  $scope.charts = [
    {
      name : 'No Chart',
      value : 'none',
      hc_type : 'pie'
    },
    {
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
      value : 'shirt_gen',
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
      value : 'h_status',
      hc_type : 'pie'
    }, {
      name : 'By State',
      value : 'state',
      hc_type : 'pie'
    }];
  $scope.currentChart = $scope.charts[0];
  $scope.showChartStatus = false;
  $scope.chartStatus = "";

  $scope.getContent = function (option) {
    return 'PLACEHOLDER'
  };

  $scope.getStats = function () {

    $http({method: 'GET', url: '/dashboard/__get_dash_stats'}).
        success(function(data, status) {
          $scope.status = status;
          $scope.signupCount = data.signup_count;
          $scope.registerCount = data.registered_count;
          $scope.acceptedCount = data.accepted_count;
          $scope.confirmedCount = data.confirmed_count
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

  $scope.showEmail = function(){
      $scope.sendEmail(true);
  }
  $scope.sendEmail = function(display){
    if ($scope.emailSubject == "" || $scope.emailName == "" || $scope.emailRecpient == "") {
      console.log("Failed")
      return "Failed";
    };
    var check = true;
    var request = {recipient: $scope.emailRecipient, subject: $scope.emailSubject, emailName:$scope.emailName }
    if (display === true){
          request.display = true;
        }
    else
       check = confirm("Are you sure you want to actually send emails?");
    if(!check)
      return;
    $http.post('/__send_email', request).
    success(function(data, status, headers, config) {
      if(data.success = true){
        console.log("sent email request!");
        $scope.emailStatus = "Sent Email to " + $scope.emailRecipient + "!";
        if (data.html) {
          $scope.emailStatus = "Displaying Email Below";
          //$scope.displayEmail = $sce.trustAsHtml(data.html);
          $scope.displayEmail = true;
          var iframe = document.getElementById("email-display")
          var doc = iframe.document;
          if(iframe.contentDocument)
            doc = iframe.contentDocument;
          else if(iframe.contentWindow)
            doc = iframe.contentWindow.document;
          // Put the content in the iframe
          doc.open();
          doc.writeln(data.html);
          doc.close();
          iframe.style.height = doc.body.scrollHeight + "px";
        };
      }
      else{
        console.log('failed to send emails');
        $scope.emailStatus = "Send failed...";
      }
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

    $http.post('/dashboard/__manual', {change: action, emails: emails}).
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

    if (emails) {
      if (emails == _.pluck($scope.lookupResult.found, 'email')) {
        emails = emails.replace(/(hacker_)(\d+)(@.+)/, function(full, a, b, c) { return a + (Number(b) + 1) + c;
        });
      }
      data = emails;
    } else {
      data = "feeling_lucky";
    }

    $http({method: 'GET', url: '/dashboard/__lookup_hacker/' + data}).
        success(function(data) {
          $scope.lookupResult = data;
          $scope.manualEmails = _.pluck(data.found, 'email').join();
          $scope.manualEmails += _.map(data.notFound, function(email) {
            var emailArray = email.split('@');
            if (emailArray[1] == 'another.edu') {
              emailArray[1] = 'brown.edu';
            } else if (emailArray[1] == 'brown.edu') {
              emailArray[1] = 'another.edu';
            }
            return emailArray.join("@");
          }).join();
        }).
        error(function(data) {
          $scope.manualStatus = data;
          $scope.showManualStatus = true;
        });
  };


  $scope.getBreakdowns = function(){
    $scope.showBreakdowns = !$scope.showBreakdowns;
    if ($scope.school){
      return;
    }
    $http({method: 'GET', url: '/dashboard/__breakdown/' + "all"}).
        success(function(data, status) {


          if (data != "null") {
            $scope.school = data.school;
            $scope.shirt = data.shirt;
            $scope.hardware_hack = data.hardware_hack;
            $scope.first_hackathon = data.first_hackathon;
            $scope.diet = data.diet;
            $scope.years = data.year;
            $scope.shirt_gen = data.shirt_gen
            $scope.h_status = data.h_status
          }

        }).
        error(function(data, status) {
          $scope.data = data || "Request failed";
          $scope.status = status;

      });
  }

  $scope.populateCharts = function() {
    if ($scope.currentChart.value == "none") {
      $('#chart').toggle(false);
      return;
    }

    $http({method: 'GET', url: '/dashboard/__breakdown/' + $scope.currentChart.value}).
        success(function(data, status) {
          $scope.showChartStatus = (data == "null");
          $scope.chartStatus = (data == "null") ? "Could not load chart data" : "";
          $('#chart').toggle(data != "null");

          if (data != "null") {
            var series = [];
            $.each(data, function(key, value) {
              series.push({"name" : key, "y": value});
            });
            $('#chart').highcharts({
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
