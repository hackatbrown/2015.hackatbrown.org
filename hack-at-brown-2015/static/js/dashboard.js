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

  $scope.showBreakdowns = false;
  $scope.displayEmail = false;
  $scope.countData = {"Signed Up" : 0, "Registered" : 0, "Accepted" : 0, "Confirmed" : 0, "Waitlisted" : 0, "Declined" : 0};

  $scope.charts = [
    {
      name : 'No Chart',
      value : 'none',
      hc_type : {
        type : 'pie'
      }
    },
    {
      name : 'By School',
      value : 'school',
      hc_type : {
        type : 'pie'
      }
    }, {
      name : 'By Shirt Size',
      value : 'shirt',
      hc_type : {
        type : 'pie'
      }
    }, {
      name : 'By Dietary Restrictions',
      value : 'diet',
      hc_type : {
        type : 'pie'
      }
    }, {
      name : 'By Gender',
      value : 'shirt_gen',
      hc_type : {
        type : 'pie'
      }
    }, {
      name : 'By Year',
      value : 'year',
      hc_type : {
        type : 'pie'
      }
    }, {
      name : 'First Hackathon',
      value : 'first_hackathon',
      hc_type : {
        type : 'pie'
      }
    }, {
      name : 'Hardware Hackers',
      value : 'hardware_hack',
      hc_type : {
        type : 'pie'
      }
    }, {
      name : 'By Status',
      value : 'h_status',
      hc_type : {
        type : 'pie'
      }
    }, {
      name : 'By State',
      value : 'state',
      hc_type : {
        type : 'pie'
      }
    }, {
      name : "Reimbursement Budget",
      value : 'budget',
      hc_type : {
        polar : false,
        type : 'bar',
      }
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
          console.log(data);
          $scope.countData = data;
          $scope.status = status;
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
            $scope.breakdownData = data;
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
          if (data == "null") {
            return;
          }

          var dictToSeriesData = function(obj) {
            return _.map(obj, function(v, k) { return {"name" : k, "y": v};});
          }

          var series;
          var tooltip = {};

          if ($scope.currentChart.value == "budget") {
            tooltip = {
              shared: true,
              pointFormat: '<span style="color:{series.color}">{series.name}: <b>${point.y:,.0f}</b><br/>'
            };
            series = _.map(data, function(series) {
              series.data = dictToSeriesData(series.data);
              return series;
            });
            var sum = function(memo, pt) { return memo + pt.y};
            $scope.showChartStatus = true;
            $scope.chartStatus = "Total Allocated: $" + _.reduce(series[0].data, sum, 0) + " Total Spent: $" + _.reduce(series[1].data, sum, 0);

          } else {
            series = [{name : 'Hackers', data : dictToSeriesData(data)}];
          }

          $('#chart').highcharts({
                chart :  $scope.currentChart.hc_type,
                title : {
                  text : $scope.currentChart.name
                },
                xAxis : {
                  categories : []
                },
                yAxis : {
                  min : 0
                },
                tooltip : tooltip,
                series: series
              });
        }).
        error(function(data, status) {
          $scope.data = data || "Request failed";
          $scope.status = status;

      });

  };

}]);
