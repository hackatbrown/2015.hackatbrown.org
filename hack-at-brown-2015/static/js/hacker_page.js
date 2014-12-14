function saveChange(key, value) {
    secret = window.location.pathname.replace('/secret', '');
    $.ajax({
      url : '/__update_hacker/' + secret,
      type : 'POST',
    });

    http.post('/__update_hacker/' + secret, {key : value}).
    success(function(data, status, headers, config) {
      console.log('success');
    }).
    error(function(data, status, headers, config) {
      console.log('failed');
    });
}
