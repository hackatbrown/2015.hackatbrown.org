function saveChange(key, value) {
    secret = window.location.pathname.replace('/secret/', '');
    var data = {};
    data[key] = value;
    $.ajax({
      url : '/__update_hacker/' + secret,
      type : 'POST',
      data : JSON.stringify(data)
    });

    // success(function(data, status, headers, config) {
    //   console.log('success');
    // }).
    // error(function(data, status, headers, config) {
    //   console.log('failed');
    // });
}
