  function slideOut($element, time) {
    time = time || 200;
    $element.stop().hide().slideToggle(time);
  }

  function slideIn($element) {
    $element.stop().show().slideToggle(200);
  }
