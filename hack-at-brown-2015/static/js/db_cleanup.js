var cleanupApp = angular.module('cleanupApp', []).config(function($interpolateProvider){
        $interpolateProvider.startSymbol('%%').endSymbol('%%');
    }
);


cleanupApp.controller('MainCtrl', ['$scope', '$http', '$sce', function ($scope, $http, $sce){
  $scope.content = "";
  $scope.header = "";

  $scope.showPropertyValues = false;
  $scope.property = "":

  $scope.getContent = function (option) {
    return 'PLACEHOLDER'
  };

  $scope.cleanup = function() {
    var property = $('.property').val();
    var originalValues = {};
    var newValue = $('.newValue');
    $('.selected').each(function(val) {
      originalValues[val] = newValue;
    });

    $display = $('.display');


    if (property == "") {

    }

    $.ajax({
      url : '/__cleanup',
      type : 'POST',
      data : data,
      success: function(response) {
        response = JSON.parse(response);
        if (response.success === true) {
          $display.addClass('.success');
        } else if (response.success === false) {
          $display.addClass('.failure');
        }
        $display.val(response.msg);
      },
      failure: function(response) {
        response = JSON.parse(response);
        $display.addClass('failure');
        $display.val("Server Error");
      }
    });
  }

}]);
