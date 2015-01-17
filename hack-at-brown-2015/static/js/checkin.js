function checkinHacker(id) {
  $.ajax({
    type: 'POST',
    url: '/checkin',
    data: {'id' : id},
    success: function(response) {
      console.log(response);
    },
    error: function(error) {
      console.log('error');
      console.log(error);
    }
  })
}

function requestMoreInfo(id) {
  $.ajax({
    type: 'GET',
    url: '/checkin/info/' + id,
    success : function(response) {
      response = JSON.parse(response);
      var hacker = response.hacker;
      console.log(hacker);
      var missingInfo = response.missingInfo;
      var check = confirm("Check this person in?");
      if (check) checkinHacker(id);

    },
    error: function(error) {
      console.log('error');
      console.log(error);
    }
  });
}
